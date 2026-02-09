# Copyright (c) 2025 GenOrca (by zenoengine). All Rights Reserved.

import unreal
import json
import traceback

ACTOR_ACTIONS_MODULE = "actor_actions"

# Helper function (consider if it should be private or utility)
def _get_actor_by_label(actor_label: str):
    """
    Helper function to find an actor by its label.
    Returns the actor or None if not found.
    """
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = subsystem.get_all_level_actors()
    for actor in all_actors:
        if actor.get_actor_label() == actor_label:
            return actor
    return None

def ue_spawn_from_object(asset_path: str = None, location: list = None) -> str:
    """
    Spawns an actor from the specified asset path at the given location.
    Wrapped in a ScopedEditorTransaction.

    :param asset_path: Path to the asset in the Content Browser
    :param location: [x, y, z] coordinates for the actor spawn position
    :return: JSON string indicating success or failure and actor label if spawned
    """
    if asset_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_path' is missing."})
    if location is None:
        return json.dumps({"success": False, "message": "Required parameter 'location' is missing."})

    transaction_description = "MCP: Spawn Actor from Object"
    asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
    if not asset_data:
        return json.dumps({"success": False, "message": f"Asset not found: {asset_path}"})

    if len(location) != 3:
        return json.dumps({"success": False, "message": "Invalid location format. Expected list of 3 floats."})

    try:
        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            vec = unreal.Vector(float(location[0]), float(location[1]), float(location[2]))
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not asset:
                 return json.dumps({"success": False, "message": f"Failed to load asset: {asset_path}"})

            actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(
                asset, vec
            )
            if actor:
                return json.dumps({"success": True, "actor_label": actor.get_actor_label(), "actor_path": actor.get_path_name()})
            else:
                return json.dumps({"success": False, "message": "Failed to spawn actor. spawn_actor_from_object returned None."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during spawn: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_duplicate_selected(offset: list) -> str:
    """
    Duplicates all selected actors in the editor and applies a position offset to each duplicate.

    :param offset: [x, y, z] offset to apply to each duplicated actor.
    :return: JSON string indicating success or failure and details of duplicated actors.
    """
    if len(offset) != 3:
        return json.dumps({"success": False, "message": "Invalid offset format. Expected list of 3 floats."})

    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        selected_actors = subsystem.get_selected_level_actors()
        if not selected_actors:
            return json.dumps({"success": False, "message": "No actors selected."})

        duplicated_actors = []
        for actor in selected_actors:
            offset_vector = unreal.Vector(float(offset[0]), float(offset[1]), float(offset[2]))
            duplicated_actor = subsystem.duplicate_actor(actor, offset=offset_vector)
            if duplicated_actor:
                duplicated_actors.append(duplicated_actor.get_actor_label())

        return json.dumps({
            "success": True,
            "message": f"Duplicated {len(duplicated_actors)} actors with offset {offset}.",
            "duplicated_actors": duplicated_actors
        })
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during duplication: {e}"})

def ue_select_all() -> str:
    """
    Selects all actors in the current level.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        subsystem.select_all(unreal.EditorLevelLibrary.get_editor_world())
        return json.dumps({"success": True, "message": "All actors selected."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during selection: {e}"})

def ue_invert_selection() -> str:
    """
    Inverts the selection of actors in the current level.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        subsystem.invert_selection(unreal.EditorLevelLibrary.get_editor_world())
        return json.dumps({"success": True, "message": "Actor selection inverted."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during selection inversion: {e}"})

def ue_delete_by_label(actor_label: str) -> str:
    """
    Deletes an actor with the specified name from the current level.

    :param actor_label: Name of the actor to delete.
    :return: JSON string indicating success or failure.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = subsystem.get_all_level_actors()
        deleted_actors = []

        for actor in all_actors:
            if actor.get_actor_label() == actor_label:
                if subsystem.destroy_actor(actor):
                    deleted_actors.append(actor_label)

        if deleted_actors:
            return json.dumps({
                "success": True,
                "message": f"Deleted actors: {deleted_actors}",
                "deleted_actors": deleted_actors
            })
        else:
            return json.dumps({"success": False, "message": f"No actor found with name: {actor_label}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during actor deletion: {e}"})

def ue_list_all_with_locations() -> str:
    """
    Lists all actors in the current level along with their world locations.

    :return: JSON string containing actor names and locations.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = subsystem.get_all_level_actors()
        actor_data = []

        for actor in all_actors:
            location = actor.get_actor_location()
            actor_data.append({
                "name": actor.get_actor_label(),
                "location": [location.x, location.y, location.z]
            })

        return json.dumps({"success": True, "actors": actor_data})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during actor listing: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_spawn_from_class(class_path: str = None, location: list = None, rotation: list = None) -> str:
    """
    Spawns an actor from the specified class path at the given location and rotation
    using unreal.EditorLevelLibrary.spawn_actor_from_class.
    Wrapped in a ScopedEditorTransaction.

    :param class_path: Path to the actor class (e.g., "/Game/Blueprints/MyActorBP.MyActorBP_C" or "/Script/Engine.StaticMeshActor").
    :param location: [x, y, z] coordinates for the actor spawn position.
    :param rotation: Optional [pitch, yaw, roll] for the actor spawn rotation. Defaults to [0.0, 0.0, 0.0].
    :return: JSON string indicating success or failure and actor label/path if spawned.
    """
    if class_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'class_path' is missing."})
    if location is None:
        return json.dumps({"success": False, "message": "Required parameter 'location' is missing."})

    transaction_description = "MCP: Spawn Actor from Class (EditorLevelLibrary)"
    if rotation is None:
        rotation = [0.0, 0.0, 0.0]

    if len(location) != 3:
        return json.dumps({"success": False, "message": "Invalid location format. Expected list of 3 floats."})
    if len(rotation) != 3:
        return json.dumps({"success": False, "message": "Invalid rotation format. Expected list of 3 floats."})

    try:
        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            actor_class = unreal.load_class(None, class_path)
            
            if not actor_class:
                return json.dumps({"success": False, "message": f"Failed to load actor class from path: {class_path}. Ensure it's a valid class path (e.g., with _C for Blueprints or /Script/ for native classes)."})

            vec_location = unreal.Vector(float(location[0]), float(location[1]), float(location[2]))
            rot_rotation = unreal.Rotator(float(rotation[2]), float(rotation[0]), float(rotation[1]))

            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                actor_class,
                vec_location,
                rot_rotation
            )

            if actor:
                return json.dumps({
                    "success": True, 
                    "actor_label": actor.get_actor_label(), 
                    "actor_path": actor.get_path_name()
                })
            else:
                return json.dumps({"success": False, "message": "Failed to spawn actor using EditorLevelLibrary.spawn_actor_from_class. The function returned None."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during spawn_actor_from_class (EditorLevelLibrary): {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_get_all_details() -> str:
    """
    Lists all actors in the current level with detailed information including
    label, class, location, rotation, and world-space bounding box.

    :return: JSON string containing a list of actor details.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = subsystem.get_all_level_actors()
        actors_details = []

        for actor in all_actors:
            loc = actor.get_actor_location()
            rot = actor.get_actor_rotation()
            
            bounds_origin, bounds_extent = actor.get_actor_bounds(False)

            detail = {
                "label": actor.get_actor_label(),
                "class": actor.get_class().get_path_name(),
                "location": [loc.x, loc.y, loc.z],
                "rotation": [rot.pitch, rot.yaw, rot.roll],
                "world_bounds_origin": [bounds_origin.x, bounds_origin.y, bounds_origin.z],
                "world_bounds_extent": [bounds_extent.x, bounds_extent.y, bounds_extent.z],
                "world_dimensions": [bounds_extent.x * 2, bounds_extent.y * 2, bounds_extent.z * 2]
            }
            
            if isinstance(actor, unreal.StaticMeshActor):
                sm_component = actor.static_mesh_component
                if hasattr(actor, 'get_static_mesh_component'):
                    sm_component = actor.get_static_mesh_component()

                if sm_component and sm_component.static_mesh:
                    detail["static_mesh_asset_path"] = sm_component.static_mesh.get_path_name()

            actors_details.append(detail)

        return json.dumps({"success": True, "actors": actors_details})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error listing all actors details: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_set_transform(actor_label: str = None, location: list = None, rotation: list = None, scale: list = None) -> str:
    """
    Sets the transform (location, rotation, scale) of a specified actor.
    Any component of the transform not provided will remain unchanged.
    This operation is wrapped in a ScopedEditorTransaction.
    """
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})

    transaction_description = f"MCP: Set Transform for actor {actor_label}"
    try:
        actor_to_modify = _get_actor_by_label(actor_label)
        if not actor_to_modify:
            return json.dumps({"success": False, "message": f"Actor with label \'{actor_label}\' not found."})

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            modified_properties = []
            if location is not None:
                if len(location) == 3:
                    new_loc = unreal.Vector(float(location[0]), float(location[1]), float(location[2]))
                    actor_to_modify.set_actor_location(new_loc, False, False) # bSweep, bTeleport
                    modified_properties.append("location")
                else:
                    return json.dumps({"success": False, "message": "Invalid location format. Expected list of 3 floats."})

            if rotation is not None:
                if len(rotation) == 3:
                    new_rot = unreal.Rotator(float(rotation[2]), float(rotation[0]), float(rotation[1]))
                    actor_to_modify.set_actor_rotation(new_rot, False) # bTeleport
                    modified_properties.append("rotation")
                else:
                    return json.dumps({"success": False, "message": "Invalid rotation format. Expected list of 3 floats."})

            if scale is not None:
                if len(scale) == 3:
                    new_scale = unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2]))
                    actor_to_modify.set_actor_scale3d(new_scale)
                    modified_properties.append("scale")
                else:
                    return json.dumps({"success": False, "message": "Invalid scale format. Expected list of 3 floats."})
            
            if not modified_properties:
                return json.dumps({"success": True, "message": f"No transform properties provided for actor \'{actor_label}\'. Actor was not modified."})

            return json.dumps({"success": True, "message": f"Actor \'{actor_label}\' transform updated for: {', '.join(modified_properties)}."})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error setting transform for actor \'{actor_label}\': {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_set_location(actor_label: str = None, location: list = None) -> str:
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})
    if location is None:
        return json.dumps({"success": False, "message": "Required parameter 'location' is missing."})
    return ue_set_transform(actor_label=actor_label, location=location)

def ue_set_rotation(actor_label: str = None, rotation: list = None) -> str:
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})
    if rotation is None:
        return json.dumps({"success": False, "message": "Required parameter 'rotation' is missing."})
    return ue_set_transform(actor_label=actor_label, rotation=rotation)

def ue_set_scale(actor_label: str = None, scale: list = None) -> str:
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})
    if scale is None:
        return json.dumps({"success": False, "message": "Required parameter 'scale' is missing."})
    return ue_set_transform(actor_label=actor_label, scale=scale)

def ue_spawn_on_surface_raycast(
    asset_or_class_path: str = None,
    ray_start: list = None,
    ray_end: list = None,
    is_class_path: bool = True,
    desired_rotation: list = None,
    location_offset: list = None, # New parameter
    trace_channel: str = 'Visibility',
    actors_to_ignore_labels: list = None
) -> str:
    if asset_or_class_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'asset_or_class_path' is missing."})
    if ray_start is None:
        return json.dumps({"success": False, "message": "Required parameter 'ray_start' is missing."})
    if ray_end is None:
        return json.dumps({"success": False, "message": "Required parameter 'ray_end' is missing."})

    transaction_description = f"MCP: Spawn Actor on Surface via Raycast ({asset_or_class_path})"

    if desired_rotation is None:
        desired_rotation = [0.0, 0.0, 0.0]
    if location_offset is None: # Default offset
        location_offset = [0.0, 0.0, 0.0]

    if len(ray_start) != 3 or len(ray_end) != 3 or len(desired_rotation) != 3 or len(location_offset) != 3:
        return json.dumps({"success": False, "message": "Invalid vector/rotator/offset format. Expected lists of 3 floats."})

    try:
        start_loc = unreal.Vector(float(ray_start[0]), float(ray_start[1]), float(ray_start[2]))
        end_loc = unreal.Vector(float(ray_end[0]), float(ray_end[1]), float(ray_end[2]))
        
        actors_to_ignore_objects = []
        if actors_to_ignore_labels:
            for label in actors_to_ignore_labels:
                actor = _get_actor_by_label(label)
                if actor:
                    actors_to_ignore_objects.append(actor)
        
        trace_type_query = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1
        if trace_channel.lower() == 'camera':
            trace_type_query = unreal.TraceTypeQuery.TRACE_TYPE_QUERY2

        hit_result = unreal.SystemLibrary.line_trace_single(
            world_context_object=unreal.EditorLevelLibrary.get_editor_world(),
            start=start_loc,
            end=end_loc,
            trace_channel=trace_type_query, 
            trace_complex=True,
            actors_to_ignore=actors_to_ignore_objects,
            draw_debug_type=unreal.DrawDebugTrace.FOR_DURATION,
            ignore_self=True
        )

        if not hit_result:
            return json.dumps({"success": False, "message": "Raycast did not hit any surface."})

        (
            blocking_hit,
            initial_overlap,
            time,
            distance,
            location,
            impact_point,
            normal,
            impact_normal,
            phys_mat,
            hit_actor,
            hit_component,
            hit_bone_name,
            bone_name,
            hit_item,
            element_index,
            face_index,
            trace_start,
            trace_end
        ) = hit_result.to_tuple()
        
        if not blocking_hit:
            return json.dumps({"success": False, "message": "Raycast did not hit any blocking surface."})

        spawn_location = location
        # Apply location offset
        spawn_location.x += float(location_offset[0])
        spawn_location.y += float(location_offset[1])
        spawn_location.z += float(location_offset[2])

        # Apply rotation final
        spawn_rotation_final = unreal.Rotator(float(desired_rotation[2]), float(desired_rotation[0]), float(desired_rotation[1]))

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            actor_spawned = None
            if is_class_path:
                actor_class = unreal.load_class(None, asset_or_class_path)
                if not actor_class:
                    return json.dumps({"success": False, "message": f"Failed to load actor class: {asset_or_class_path}"})
                actor_spawned = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, spawn_location, spawn_rotation_final)
            else:
                asset = unreal.EditorAssetLibrary.load_asset(asset_or_class_path)
                if not asset:
                    return json.dumps({"success": False, "message": f"Failed to load asset: {asset_or_class_path}"})
                actor_spawned = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(asset, spawn_location)

            if actor_spawned:
                return json.dumps({
                    "success": True, 
                    "actor_label": actor_spawned.get_actor_label(), 
                    "actor_path": actor_spawned.get_path_name(),
                    "location": [spawn_location.x, spawn_location.y, spawn_location.z],
                    "rotation": [spawn_rotation_final.pitch, spawn_rotation_final.yaw, spawn_rotation_final.roll],
                })
            else:
                return json.dumps({"success": False, "message": "Failed to spawn actor after raycast hit."})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during spawn_actor_on_surface_with_raycast: {str(e)}", "traceback": traceback.format_exc()})

def ue_get_in_view_frustum() -> str:
    """
    Retrieves a list of actors that are potentially visible within the active editor viewport's frustum.

    This function performs an *approximate* frustum check using a sphere-cone intersection test:
    - Actors are represented by their bounding spheres.
    - The view frustum is approximated as a cone based on the camera's vertical FOV.
    - Camera location and rotation are fetched using `unreal.UnrealEditorSubsystem().get_level_viewport_camera_info()`.
    - FOV, Aspect ratio, near plane, and far plane are based on defaults as they cannot be reliably queried
      through the subsystem directly. This means actors visible in the horizontal periphery of a wide viewport
      or very close/far might be misclassified.

    :return: JSON string containing a list of potentially visible actor details or an error message.
    """
    try:
        cam_loc = None
        cam_rot = None
        # Default values. FOV is not returned by UnrealEditorSubsystem.get_level_viewport_camera_info()
        v_fov_degrees = 60.0      # Default Vertical FOV
        aspect_ratio = 16.0 / 9.0 # Default aspect ratio
        near_plane = 10.0         # Default near clip plane
        far_plane = 100000.0      # Default far clip plane

        # Get core camera info using UnrealEditorSubsystem
        try:
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            if not editor_subsystem:
                return json.dumps({"success": False, "message": "Failed to get UnrealEditorSubsystem."})
            
            camera_info = editor_subsystem.get_level_viewport_camera_info()
            if camera_info:
                cam_loc, cam_rot = camera_info
            else:
                return json.dumps({"success": False, "message": "Failed to obtain camera info from UnrealEditorSubsystem."})

        except Exception as e:
            return json.dumps({"success": False, "message": f"Failed to obtain essential camera info from UnrealEditorSubsystem: {e}"})

        if cam_loc is None or cam_rot is None:
            return json.dumps({"success": False, "message": "Failed to obtain essential camera location and rotation from UnrealEditorSubsystem."})

        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = actor_subsystem.get_all_level_actors()
        visible_actors_details = []

        cam_forward_vec = cam_rot.get_forward_vector()
        v_fov_rad = unreal.MathLibrary.degrees_to_radians(v_fov_degrees)

        for actor in all_actors:
            if not actor: continue

            bounds_origin, bounds_extent = actor.get_actor_bounds(False)
            actor_bounding_radius = bounds_extent.length()
            
            vec_to_actor_center = bounds_origin - cam_loc
            dist_to_actor_center = vec_to_actor_center.length()

            sphere_closest_to_cam = dist_to_actor_center - actor_bounding_radius
            sphere_farthest_from_cam = dist_to_actor_center + actor_bounding_radius

            if sphere_farthest_from_cam < near_plane or sphere_closest_to_cam > far_plane:
                continue

            if dist_to_actor_center <= actor_bounding_radius:
                pass
            elif dist_to_actor_center > 0:
                vec_to_actor_center_normalized = vec_to_actor_center.normal()
                dot_product = cam_forward_vec.dot(vec_to_actor_center_normalized)
                dot_product_clamped = unreal.MathLibrary.clamp(dot_product, -1.0, 1.0)
                angle_to_actor_center_rad = unreal.MathLibrary.acos(dot_product_clamped)

                if dist_to_actor_center > actor_bounding_radius:
                    asin_arg = unreal.MathLibrary.clamp(actor_bounding_radius / dist_to_actor_center, -1.0, 1.0)
                    angular_radius_of_sphere_rad = unreal.MathLibrary.asin(asin_arg)
                else:
                    angular_radius_of_sphere_rad = unreal.MathLibrary.PI

                if angle_to_actor_center_rad > (v_fov_rad / 2.0) + angular_radius_of_sphere_rad:
                    continue
            else:
                pass

            loc = actor.get_actor_location()
            rot = actor.get_actor_rotation()
            actor_details_dict = {
                "label": actor.get_actor_label(),
                "class": actor.get_class().get_path_name(),
                "location": [loc.x, loc.y, loc.z],
                "rotation": [rot.pitch, rot.yaw, rot.roll],
                "world_bounds_origin": [bounds_origin.x, bounds_origin.y, bounds_origin.z],
                "world_bounds_extent": [bounds_extent.x, bounds_extent.y, bounds_extent.z]
            }
            if isinstance(actor, unreal.StaticMeshActor):
                sm_component = actor.static_mesh_component
                if sm_component and sm_component.static_mesh:
                    actor_details_dict["static_mesh_asset_path"] = sm_component.static_mesh.get_path_name()
            
            visible_actors_details.append(actor_details_dict)

        return json.dumps({"success": True, "visible_actors": visible_actors_details})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error in ue_get_in_view_frustum: {str(e)}", "type": type(e).__name__})
