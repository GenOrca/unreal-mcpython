# Copyright (c) 2025 GenOrca. All Rights Reserved.

import unreal
import json
import traceback
from typing import List, Dict, Optional, Any # Modified import

def ue_get_selected_assets() -> str:
    """Gets the set of currently selected assets."""
    try:
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        
        serialized_assets = []
        for asset in selected_assets:
            serialized_assets.append({
                "asset_name": asset.get_name(),
                "asset_path": asset.get_path_name(),
                "asset_class": asset.get_class().get_name(),
            })
        
        return json.dumps({"success": True, "selected_assets": serialized_assets})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})

# Helper function to load MaterialInterface assets (can be Material or MaterialInstance)
def _load_material_interface(material_path: str):
    # Helper implementation (ensure this is robust or use existing if available)
    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if not material:
        raise FileNotFoundError(f"Material asset not found at path: {material_path}")
    if not isinstance(material, unreal.MaterialInterface): # Allows Material or MaterialInstance
        raise TypeError(f"Asset at {material_path} is not a MaterialInterface, but {type(material).__name__}")
    return material

# Helper function to load StaticMesh assets
def _load_static_mesh(mesh_path: str):
    # Helper implementation (ensure this is robust or use existing if available)
    mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
    if not mesh:
        raise FileNotFoundError(f"StaticMesh asset not found at path: {mesh_path}")
    if not isinstance(mesh, unreal.StaticMesh):
        raise TypeError(f"Asset at {mesh_path} is not a StaticMesh, but {type(mesh).__name__}")
    return mesh

# Helper function to get material paths from a mesh component
def _get_component_material_paths(component: unreal.MeshComponent) -> List[str]:
    material_paths = []
    if component:
        for i in range(component.get_num_materials()):
            material = component.get_material(i)
            if material:
                material_paths.append(material.get_path_name())
            else:
                material_paths.append("") # Represent empty slot
    return material_paths

# Helper function to get actors by their paths
def _get_actors_by_paths(actor_paths: List[str]) -> List[unreal.Actor]:
    actors = []
    all_level_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for path in actor_paths:
        actor = next((a for a in all_level_actors if a.get_path_name() == path), None)
        if actor:
            actors.append(actor)
        else:
            unreal.log_warning(f"MCP: Actor not found at path: {path}")
    return actors

# Helper to create a map of actor paths to their unique material asset paths
def _get_materials_map_for_actors(actors_list: List[unreal.Actor]) -> Dict[str, List[str]]:
    materials_map = {}
    if not actors_list:
        return materials_map
    for actor in actors_list:
        if not actor: continue
        actor_path_name = actor.get_path_name()
        actor_material_paths = set()
        mesh_components = actor.get_components_by_class(unreal.MeshComponent.static_class())
        for comp in mesh_components:
            if comp:
                for i in range(comp.get_num_materials()):
                    material = comp.get_material(i)
                    if material:
                        actor_material_paths.add(material.get_path_name())
        materials_map[actor_path_name] = sorted(list(actor_material_paths))
    return materials_map

# Helper to get static mesh path from a static mesh component
def _get_component_mesh_path(component: unreal.StaticMeshComponent) -> str:
    if component and hasattr(component, 'static_mesh') and component.static_mesh:
        return component.static_mesh.get_path_name()
    return ""

# Helper to create a map of actor paths to their unique static mesh asset paths
def _get_meshes_map_for_actors(actors_list: List[unreal.Actor]) -> Dict[str, List[str]]:
    meshes_map = {}
    if not actors_list:
        return meshes_map
    for actor in actors_list:
        if not actor: continue
        actor_path_name = actor.get_path_name()
        actor_mesh_paths = set()
        sm_components = actor.get_components_by_class(unreal.StaticMeshComponent.static_class())
        for comp in sm_components:
            mesh_path = _get_component_mesh_path(comp)
            if mesh_path:
                actor_mesh_paths.add(mesh_path)
        meshes_map[actor_path_name] = sorted(list(actor_mesh_paths))
    return meshes_map

# Helper to create a map of actor paths to their unique skeletal mesh asset paths
def _get_skeletal_meshes_map_for_actors(actors_list: List[unreal.Actor]) -> Dict[str, List[str]]:
    skeletal_meshes_map = {}
    if not actors_list:
        return skeletal_meshes_map
    for actor in actors_list:
        if not actor:
            continue
        actor_path_name = actor.get_path_name()
        actor_skel_mesh_paths = set()
        skel_components = actor.get_components_by_class(unreal.SkeletalMeshComponent.static_class())
        for comp in skel_components:
            if hasattr(comp, 'skeletal_mesh') and comp.skeletal_mesh:
                actor_skel_mesh_paths.add(comp.skeletal_mesh.get_path_name())
        skeletal_meshes_map[actor_path_name] = sorted(list(actor_skel_mesh_paths))
    return skeletal_meshes_map


# Base helper for replacing meshes
def _replace_meshes_on_actors_components_base(
    actors: List[unreal.Actor],
    mesh_to_be_replaced_path: str, # Can be empty/None to replace any mesh
    new_mesh_path: str
) -> Dict[str, Any]:
    """Base logic for replacing static meshes on components of given actors."""
    mesh_to_replace = None
    # Only load if a specific mesh is targeted for replacement
    if mesh_to_be_replaced_path and mesh_to_be_replaced_path.lower() not in ["", "none", "any"]:
        mesh_to_replace = _load_static_mesh(mesh_to_be_replaced_path) # Uses existing helper
        # If _load_static_mesh raises, it will be caught by the calling ue_ function's try-except

    new_mesh = _load_static_mesh(new_mesh_path) # Uses existing helper
    # If _load_static_mesh raises, it will be caught by the calling ue_ function's try-except

    if mesh_to_replace and new_mesh and mesh_to_replace.get_path_name() == new_mesh.get_path_name():
        return {"success": True, "message": "Mesh to be replaced is the same as the new mesh. No changes made.", "changed_actors_count": 0, "changed_components_count": 0}


    changed_actors_count = 0
    changed_components_count = 0
    details = {"actors_affected": []}

    with unreal.ScopedEditorTransaction("Replace Static Meshes on Components") as trans:
        for actor in actors:
            if not actor: continue
            actor_path = actor.get_path_name()
            actor_changed_this_iteration = False
            actor_details = {"actor_path": actor_path, "components_changed": []}
            
            static_mesh_components = actor.get_components_by_class(unreal.StaticMeshComponent.static_class())
            for component in static_mesh_components:
                if not component or component.get_owner() != actor:
                    continue
                
                component_path = component.get_path_name()
                current_mesh = component.static_mesh
                
                should_replace = False
                # Case 1: Replace any mesh (mesh_to_be_replaced_path is empty/None/Any)
                if not mesh_to_be_replaced_path or mesh_to_be_replaced_path.lower() in ["", "none", "any"]:
                    if current_mesh != new_mesh : # Avoid replacing with itself if no specific mesh to replace
                        should_replace = True
                # Case 2: Replace a specific mesh
                elif mesh_to_replace and current_mesh and current_mesh.get_path_name() == mesh_to_replace.get_path_name():
                     if current_mesh.get_path_name() != new_mesh.get_path_name(): # Don't replace if it's already the new mesh
                        should_replace = True
                # Case 3: Component has no mesh, and we want to set one (mesh_to_be_replaced_path is empty/None/Any)
                elif (not mesh_to_be_replaced_path or mesh_to_be_replaced_path.lower() in ["", "none", "any"]) and not current_mesh:
                    should_replace = True


                if should_replace:
                    if component.set_static_mesh(new_mesh):
                        changed_components_count += 1
                        actor_changed_this_iteration = True
                        actor_details["components_changed"].append({"component_path": component_path, "previous_mesh": current_mesh.get_path_name() if current_mesh else None})
                    else:
                        unreal.log_warning(f"MCP: Failed to set static mesh on component {component_path} for actor {actor_path}")
            
            if actor_changed_this_iteration:
                changed_actors_count += 1
                details["actors_affected"].append(actor_details)
            
    if changed_actors_count > 0:
        unreal.EditorLevelLibrary.refresh_all_level_editors()

    return {
        "success": True,
        "message": f"Mesh replacement processed. Actors processed: {len(actors)}.",
        "changed_actors_count": changed_actors_count,
        "changed_components_count": changed_components_count,
        "details": details
    }

def ue_replace_mtl_on_selected(material_to_be_replaced_path: str, new_material_path: str) -> str:
    try:
        material_to_replace = _load_material_interface(material_to_be_replaced_path)
        new_material = _load_material_interface(new_material_path)
        
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        if not selected_actors:
            return json.dumps({"success": False, "message": "No actors selected."})

        mesh_components = []
        for actor in selected_actors:
            components = actor.get_components_by_class(unreal.MeshComponent.static_class())
            mesh_components.extend(c for c in components if c)
        
        if not mesh_components:
            return json.dumps({"success": False, "message": "No mesh components found on selected actors."})

        initial_materials_map = {}
        for comp in mesh_components:
            initial_materials_map[comp.get_path_name()] = _get_component_material_paths(comp)

        unreal.EditorLevelLibrary.replace_mesh_components_materials(
            mesh_components, 
            material_to_replace, 
            new_material
        )

        num_components_affected = 0
        affected_component_paths = []
        for comp in mesh_components:
            current_materials = _get_component_material_paths(comp)
            original_materials = initial_materials_map.get(comp.get_path_name(), [])
            
            component_changed_here = False
            for slot_idx, original_mat_path in enumerate(original_materials):
                if original_mat_path == material_to_replace.get_path_name():
                    if slot_idx < len(current_materials) and current_materials[slot_idx] == new_material.get_path_name():
                        component_changed_here = True
                        break 
            if component_changed_here:
                num_components_affected += 1
                affected_component_paths.append(comp.get_path_name())
        
        if num_components_affected > 0:
            return json.dumps({
                "success": True, 
                "message": f"Successfully replaced material '{material_to_be_replaced_path}' with '{new_material_path}' on {num_components_affected} mesh component(s) across {len(selected_actors)} selected actor(s).",
                "affected_actors_count": len(selected_actors),
                "affected_components_count": num_components_affected,
                "affected_component_paths": affected_component_paths
            })
        else:
            return json.dumps({
                "success": False, 
                "message": f"Failed to replace material. Target material '{material_to_be_replaced_path}' not found or not replaced on any mesh components of selected actors."
            })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_replace_mtl_on_specified(actor_paths: List[str], material_to_be_replaced_path: str, new_material_path: str) -> str:
    try:
        material_to_replace = _load_material_interface(material_to_be_replaced_path)
        new_material = _load_material_interface(new_material_path)
        
        actors_to_process = _get_actors_by_paths(actor_paths)
        if not actors_to_process:
            return json.dumps({"success": False, "message": "No valid actors found from the provided paths."})

        all_mesh_components_in_actors = []
        for actor in actors_to_process:
            components = actor.get_components_by_class(unreal.MeshComponent.static_class())
            all_mesh_components_in_actors.extend(c for c in components if c)

        if not all_mesh_components_in_actors:
            return json.dumps({"success": False, "message": "No mesh components found on the specified actors."})

        initial_materials_map = {}
        for comp in all_mesh_components_in_actors:
            initial_materials_map[comp.get_path_name()] = _get_component_material_paths(comp)
        
        unreal.EditorLevelLibrary.replace_mesh_components_materials_on_actors(
            actors_to_process, 
            material_to_replace, 
            new_material
        )
        
        num_components_affected = 0
        affected_component_paths = []
        for comp in all_mesh_components_in_actors:
            current_materials = _get_component_material_paths(comp)
            original_materials = initial_materials_map.get(comp.get_path_name(), [])
            
            component_changed_here = False
            for slot_idx, original_mat_path in enumerate(original_materials):
                if original_mat_path == material_to_replace.get_path_name():
                    if slot_idx < len(current_materials) and current_materials[slot_idx] == new_material.get_path_name():
                        component_changed_here = True
                        break
            if component_changed_here:
                num_components_affected += 1
                affected_component_paths.append(comp.get_path_name())
        
        if num_components_affected > 0:
            return json.dumps({
                "success": True, 
                "message": f"Successfully replaced material '{material_to_be_replaced_path}' with '{new_material_path}' on {num_components_affected} mesh component(s) across {len(actors_to_process)} specified actor(s).",
                "affected_actors_count": len(actors_to_process),
                "affected_components_count": num_components_affected,
                "affected_component_paths": affected_component_paths
            })
        else:
            return json.dumps({
                "success": False, 
                "message": f"Failed to replace material. Target material '{material_to_be_replaced_path}' not found or not replaced on any mesh components of specified actors."
            })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_replace_mesh_on_selected(mesh_to_be_replaced_path: str, new_mesh_path: str) -> str:
    """Replaces static meshes on components of selected actors using Unreal's batch API if available."""
    try:
        # Check if mesh_to_be_replaced_path exists (if specified)
        if mesh_to_be_replaced_path and mesh_to_be_replaced_path.lower() not in ["", "none", "any"]:
            try:
                _ = _load_static_mesh(mesh_to_be_replaced_path)
            except FileNotFoundError:
                return json.dumps({
                    "success": False,
                    "message": f"The mesh_to_be_replaced_path '{mesh_to_be_replaced_path}' does not exist as a StaticMesh asset.",
                    "error_type": "MeshToReplaceNotFound"
                })
        
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        if not selected_actors:
            return json.dumps({"success": True, "message": "No actors selected.", "changed_actors_count": 0, "changed_components_count": 0})

        mesh_to_replace = None
        if mesh_to_be_replaced_path and mesh_to_be_replaced_path.lower() not in ["", "none", "any"]:
            mesh_to_replace = _load_static_mesh(mesh_to_be_replaced_path)
        new_mesh = _load_static_mesh(new_mesh_path)

        # Gather all static mesh components from selected actors
        all_mesh_components = []
        for actor in selected_actors:
            comps = actor.get_components_by_class(unreal.StaticMeshComponent.static_class())
            all_mesh_components.extend(c for c in comps if c)

        if not all_mesh_components:
            return json.dumps({"success": False, "message": "No static mesh components found on selected actors."})

        # Save initial mesh paths for change detection
        initial_meshes_map = {comp.get_path_name(): comp.static_mesh.get_path_name() if comp.static_mesh else "" for comp in all_mesh_components}

        # Use Unreal's batch API if available
        if hasattr(unreal.EditorLevelLibrary, "replace_mesh_components_meshes_on_actors"):
            unreal.EditorLevelLibrary.replace_mesh_components_meshes_on_actors(
                selected_actors,
                mesh_to_replace,
                new_mesh
            )
        else:
            # Fallback to manual replacement if batch API is not available
            for comp in all_mesh_components:
                current_mesh = comp.static_mesh
                should_replace = False
                if not mesh_to_replace:
                    if current_mesh != new_mesh:
                        should_replace = True
                elif current_mesh and current_mesh.get_path_name() == mesh_to_replace.get_path_name():
                    if current_mesh.get_path_name() != new_mesh.get_path_name():
                        should_replace = True
                elif not current_mesh and not mesh_to_replace:
                    should_replace = True
                if should_replace:
                    comp.set_static_mesh(new_mesh)

        # Detect changes
        changed_components_count = 0
        affected_component_paths = []
        for comp in all_mesh_components:
            before = initial_meshes_map.get(comp.get_path_name(), "")
            after = comp.static_mesh.get_path_name() if comp.static_mesh else ""
            if mesh_to_replace:
                if before == mesh_to_replace.get_path_name() and after == new_mesh.get_path_name():
                    changed_components_count += 1
                    affected_component_paths.append(comp.get_path_name())
            else:
                if before != after and after == new_mesh.get_path_name():
                    changed_components_count += 1
                    affected_component_paths.append(comp.get_path_name())

        if changed_components_count > 0:
            return json.dumps({
                "success": True,
                "message": f"Successfully replaced mesh on {changed_components_count} static mesh component(s) across {len(selected_actors)} selected actor(s).",
                "affected_actors_count": len(selected_actors),
                "affected_components_count": changed_components_count,
                "affected_component_paths": affected_component_paths
            })
        else:
            return json.dumps({
                "success": False,
                "message": f"Failed to replace mesh. Target mesh '{mesh_to_be_replaced_path}' not found or not replaced on any static mesh components of selected actors."
            })
    except FileNotFoundError as e:
        unreal.log_error(f"MCP: Asset loading error in ue_replace_mesh_on_selected: {e}")
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
    except TypeError as e:
        unreal.log_error(f"MCP: Asset type error in ue_replace_mesh_on_selected: {e}")
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
    except Exception as e:
        unreal.log_error(f"MCP: Error in ue_replace_mesh_on_selected: {e}\n{traceback.format_exc()}")
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_replace_mesh_on_specified(actor_paths: List[str], mesh_to_be_replaced_path: str, new_mesh_path: str) -> str:
    """Replaces static meshes on components of specified actors using Unreal's batch API if available."""
    try:
        # Check if mesh_to_be_replaced_path exists (if specified)
        if mesh_to_be_replaced_path and mesh_to_be_replaced_path.lower() not in ["", "none", "any"]:
            try:
                _ = _load_static_mesh(mesh_to_be_replaced_path)
            except FileNotFoundError:
                return json.dumps({
                    "success": False,
                    "message": f"The mesh_to_be_replaced_path '{mesh_to_be_replaced_path}' does not exist as a StaticMesh asset.",
                    "error_type": "MeshToReplaceNotFound"
                })
        actors_to_process = _get_actors_by_paths(actor_paths)
        if not actors_to_process:
            return json.dumps({"success": False, "message": "No valid actors found from the provided paths."})
        mesh_to_replace = None
        if mesh_to_be_replaced_path and mesh_to_be_replaced_path.lower() not in ["", "none", "any"]:
            mesh_to_replace = _load_static_mesh(mesh_to_be_replaced_path)
        new_mesh = _load_static_mesh(new_mesh_path)
        # Gather all static mesh components from specified actors
        all_mesh_components = []
        for actor in actors_to_process:
            comps = actor.get_components_by_class(unreal.StaticMeshComponent.static_class())
            all_mesh_components.extend(c for c in comps if c)
        if not all_mesh_components:
            # Get the actual actor types and names for better diagnosis
            actor_info = [{"name": actor.get_name(), "class": actor.get_class().get_name()} for actor in actors_to_process]
            actors_materials_info = _get_materials_map_for_actors(actors_to_process)
            actors_meshes_info = _get_meshes_map_for_actors(actors_to_process)
            actors_skel_meshes_info = _get_skeletal_meshes_map_for_actors(actors_to_process)
            return json.dumps({
                "success": False,
                "message": "No static mesh components found on specified actors.",
                "specified_actors_info": actor_info,
                "current_materials": actors_materials_info,
                "current_meshes": actors_meshes_info,
                "current_skeletal_meshes": actors_skel_meshes_info
            })
        # Save initial mesh paths for change detection
        initial_meshes_map = {comp.get_path_name(): comp.static_mesh.get_path_name() if comp.static_mesh else "" for comp in all_mesh_components}
        # Use Unreal's batch API if available
        if hasattr(unreal.EditorLevelLibrary, "replace_mesh_components_meshes_on_actors"):
            unreal.EditorLevelLibrary.replace_mesh_components_meshes_on_actors(
                actors_to_process,
                mesh_to_replace,
                new_mesh
            )
        else:
            # Fallback to manual replacement if batch API is not available
            for comp in all_mesh_components:
                current_mesh = comp.static_mesh
                should_replace = False
                if not mesh_to_replace:
                    if current_mesh != new_mesh:
                        should_replace = True
                elif current_mesh and current_mesh.get_path_name() == mesh_to_replace.get_path_name():
                    if current_mesh.get_path_name() != new_mesh.get_path_name():
                        should_replace = True
                elif not current_mesh and not mesh_to_replace:
                    should_replace = True
                if should_replace:
                    comp.set_static_mesh(new_mesh)
        # Detect changes
        changed_components_count = 0
        affected_component_paths = []
        unchanged_components_info = []
        for comp in all_mesh_components:
            before = initial_meshes_map.get(comp.get_path_name(), "")
            after = comp.static_mesh.get_path_name() if comp.static_mesh else ""
            owner_actor = comp.get_owner()
            owner_name = owner_actor.get_name() if owner_actor else "Unknown"
            if mesh_to_replace:
                if before == mesh_to_replace.get_path_name() and after == new_mesh.get_path_name():
                    changed_components_count += 1
                    affected_component_paths.append(comp.get_path_name())
                else:
                    is_candidate = before == mesh_to_replace.get_path_name()
                    unchanged_components_info.append({
                        "component_path": comp.get_path_name(),
                        "component_name": comp.get_name(),
                        "actor_name": owner_name,
                        "current_mesh": before,
                        "is_candidate": is_candidate,
                        "reason": (
                            "Component is a candidate for replacement (matches mesh_to_be_replaced_path) but was not changed"
                            if is_candidate else
                            ("Current mesh doesn't match the mesh to be replaced" if before != mesh_to_replace.get_path_name() else "Failed to set new mesh")
                        )
                    })
            else:
                if before != after and after == new_mesh.get_path_name():
                    changed_components_count += 1
                    affected_component_paths.append(comp.get_path_name())
                else:
                    unchanged_components_info.append({
                        "component_path": comp.get_path_name(),
                        "component_name": comp.get_name(),
                        "actor_name": owner_name,
                        "current_mesh": before,
                        "is_candidate": False,
                        "reason": "Component already has the target mesh" if before == new_mesh.get_path_name() else "Failed to set new mesh"
                    })
        unchanged_components_info = unchanged_components_info if 'unchanged_components_info' in locals() else []
        if changed_components_count > 0:
            return json.dumps({
                "success": True,
                "message": f"Successfully replaced mesh on {changed_components_count} static mesh component(s) across {len(actors_to_process)} specified actor(s).",
                "affected_actors_count": len(actors_to_process),
                "affected_components_count": changed_components_count,
                "affected_component_paths": affected_component_paths,
                "unchanged_components": unchanged_components_info
            })
        else:
            actors_materials_info = _get_materials_map_for_actors(actors_to_process)
            actors_meshes_info = _get_meshes_map_for_actors(actors_to_process)
            actors_skel_meshes_info = _get_skeletal_meshes_map_for_actors(actors_to_process)
            unchanged_components_info = unchanged_components_info if 'unchanged_components_info' in locals() else []
            return json.dumps({
                "success": False,
                "message": f"Failed to replace mesh. Target mesh '{mesh_to_be_replaced_path}' not found or not replaced on any static mesh components of specified actors.",
                "current_materials": actors_materials_info,
                "current_meshes": actors_meshes_info,
                "current_skeletal_meshes": actors_skel_meshes_info,
                "unchanged_components": unchanged_components_info
            })
    except FileNotFoundError as e:
        unreal.log_error(f"MCP: Asset loading error in ue_replace_mesh_on_specified: {e}")
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
    except TypeError as e:
        unreal.log_error(f"MCP: Asset type error in ue_replace_mesh_on_specified: {e}")
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
    except Exception as e:
        unreal.log_error(f"MCP: Error in ue_replace_mesh_on_specified: {e}\n{traceback.format_exc()}")
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_replace_selected_with_bp(blueprint_asset_path: str) -> str:
    """Replaces the currently selected actors with new actors spawned from a specified Blueprint asset path using Unreal's official API."""
    import unreal
    import json
    import traceback
    try:
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        if not selected_actors:
            return json.dumps({"success": False, "message": "No actors selected."})
        # Check if the blueprint asset exists
        blueprint = unreal.EditorAssetLibrary.load_asset(blueprint_asset_path)
        if not blueprint:
            return json.dumps({"success": False, "message": f"Blueprint asset not found at path: {blueprint_asset_path}"})
        # Use the official API
        unreal.EditorLevelLibrary.replace_selected_actors(blueprint_asset_path)
        return json.dumps({
            "success": True,
            "message": f"Replaced {len(selected_actors)} actors with Blueprint '{blueprint_asset_path}' using official API.",
            "replaced_actors_count": len(selected_actors)
        })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_get_selected_bp_nodes() -> str:
    """Returns information about currently selected blueprint nodes in the editor."""
    import unreal
    import json
    try:
        nodes = unreal.MCPythonHelper.get_selected_blueprint_nodes()
        node_infos = []
        for node in nodes:
            node_info = {
                "name": node.get_name() if hasattr(node, 'get_name') else str(node),
                "class": node.get_class().get_name() if hasattr(node, 'get_class') else str(type(node)),
                "object_path": node.get_path_name() if hasattr(node, 'get_path_name') else None
            }
            node_infos.append(node_info)
        return json.dumps({
            "success": True,
            "selected_nodes_count": len(node_infos),
            "selected_nodes": node_infos
        })
    except Exception as e:
        import traceback
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_get_selected_bp_node_infos() -> str:
    """Returns compact blueprint node info optimized for LLM token efficiency."""
    import unreal
    import json
    try:
        node_infos = unreal.MCPythonHelper.get_selected_blueprint_node_infos()

        # Build node_name -> index map for selected nodes
        name_to_id = {}
        for i, n in enumerate(node_infos):
            name_to_id[n.node_name] = i

        def link_to_dict(link):
            d = {}
            # Use integer ID for selected nodes, title string for external nodes
            if link.node_name in name_to_id:
                d["node"] = name_to_id[link.node_name]
            else:
                d["node"] = link.node_title
            if link.pin_name:
                d["pin"] = link.pin_name
            return d

        def pin_to_dict(pin):
            name = pin.friendly_name if pin.friendly_name else pin.pin_name
            d = {"name": name, "dir": pin.direction}
            # Combine type + subtype
            ptype = pin.pin_type
            if pin.pin_sub_type:
                ptype += ":" + pin.pin_sub_type
            d["type"] = ptype
            # Only include default if non-empty
            if pin.default_value:
                d["default"] = pin.default_value
            # Only include linked if non-empty
            linked = list(pin.linked_to)
            if linked:
                d["linked"] = [link_to_dict(l) for l in linked]
            return d

        def node_to_dict(node, idx):
            d = {"id": idx, "title": node.node_title}
            if node.node_comment:
                d["comment"] = node.node_comment
            d["pins"] = [pin_to_dict(p) for p in node.pins]
            return d

        nodes = [node_to_dict(n, i) for i, n in enumerate(node_infos)]
        return json.dumps({
            "success": True,
            "nodes": nodes
        })
    except Exception as e:
        import traceback
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})