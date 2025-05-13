"""
Defines Python action functions to be executed within Unreal Engine.
"""
import unreal
import json
import sys
import importlib
import traceback  # Ensure traceback is imported

# Core dispatcher for executing dynamic Python commands received from the MCP server
def execute_action(module_name, function_name, args_list):
    """
    Dynamically imports and executes the specified function from the given module.
    It reloads the module on each call to ensure the latest version is used.

    :param module_name: Name of the module containing the function (e.g., "mcp_unreal_actions")
    :param function_name: Name of the function to call (e.g., "ue_print_message")
    :param args_list: List of arguments to pass to the target function
    :return: JSON-formatted string representing the function's result
    """
    try:
        # Import the module first
        target_module = __import__(module_name)
        # Reload the module to ensure the latest code is used
        importlib.reload(target_module)

        target_function = getattr(target_module, function_name)
        result = target_function(*args_list)
        if isinstance(result, str):
            return result
        else:
            return json.dumps({
                "success": True,
                "data": result,
                "message": f"Result from {function_name} serialized to JSON."
            })
    except ImportError as e:
        error = f"ImportError: Could not import module '{module_name}'. Details: {e}"
        return json.dumps({"success": False, "error": error, "type": "ImportError"})
    except AttributeError as e:
        error = f"AttributeError: Function '{function_name}' not found in module '{module_name}'. Details: {e}"
        return json.dumps({"success": False, "error": error, "type": "AttributeError"})
    except Exception as e:
        error = f"Exception during execution of '{module_name}.{function_name}': {e}"
        return json.dumps({"success": False, "error": error, "type": type(e).__name__})

def ue_print_message(message: str) -> str:
    """
    Logs a message to the Unreal log and returns a JSON success response.
    """
    unreal.log(f"MCP Message: {message}")
    return json.dumps({
        "received_message": message,
        "success": True,
        "source": "ue_print_message"
    })

def ue_find_asset_by_name(name: str) -> str:
    """
    Returns a JSON list of asset paths under '/Game' containing the given name.
    """
    assets = unreal.EditorAssetLibrary.list_assets('/Game', recursive=True)
    matches = [asset for asset in assets if name in asset]
    return json.dumps(matches)

def ue_find_asset_by_query(name : str, asset_type : str) -> str:
    """
    Returns a JSON list of asset paths under '/Game' matching the given query dict.
    Supported keys: 'name' (substring match), 'asset_type' (Unreal class name, e.g. 'StaticMesh')
    """
    assets = unreal.EditorAssetLibrary.list_assets('/Game', recursive=True)
    matches = []
    for asset in assets:
        if name and name not in asset:
            continue
        if asset_type:
            loaded = unreal.EditorAssetLibrary.load_asset(asset)
            if not loaded or loaded.get_class().get_name() != asset_type:
                continue
        matches.append(asset)
    return json.dumps(matches)

def ue_spawn_actor_from_object(asset_path: str, location: list) -> str:
    """
    Spawns an actor from the specified asset path at the given location.
    Wrapped in a ScopedEditorTransaction.

    :param asset_path: Path to the asset in the Content Browser
    :param location: [x, y, z] coordinates for the actor spawn position
    :return: JSON string indicating success or failure and actor label if spawned
    """
    transaction_description = "MCP: Spawn Actor from Object"
    asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
    if not asset_data:
        return json.dumps({"success": False, "message": f"Asset not found: {asset_path}"})

    if len(location) != 3:
        return json.dumps({"success": False, "message": "Invalid location format. Expected list of 3 floats."})

    try:
        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            vec = unreal.Vector(float(location[0]), float(location[1]), float(location[2]))
            # Ensure the asset is loaded before trying to spawn from it
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not asset:
                 return json.dumps({"success": False, "message": f"Failed to load asset: {asset_path}"})

            actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(
                asset, vec # Use the loaded asset object
            )
            if actor:
                return json.dumps({"success": True, "actor_label": actor.get_actor_label(), "actor_path": actor.get_path_name()})
            else:
                # If spawn_actor_from_object returns None, it means spawning failed.
                # We might want to cancel the transaction if nothing was changed.
                # However, ScopedEditorTransaction handles this; if no changes were made, it won't create an undo step.
                return json.dumps({"success": False, "message": "Failed to spawn actor. spawn_actor_from_object returned None."})
    except Exception as e:
        # It's good practice to ensure the transaction is cancelled if an exception occurs.
        # However, the 'with' statement handles this automatically for ScopedEditorTransaction.
        return json.dumps({"success": False, "message": f"Error during spawn: {str(e)}", "type": type(e).__name__})

def ue_duplicate_selected_actors_with_offset(offset: list) -> str:
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

def ue_select_all_actors() -> str:
    """
    Selects all actors in the current level.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        subsystem.select_all(unreal.EditorLevelLibrary.get_editor_world())
        return json.dumps({"success": True, "message": "All actors selected."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during selection: {e}"})

def ue_invert_actor_selection() -> str:
    """
    Inverts the selection of actors in the current level.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        subsystem.invert_selection(unreal.EditorLevelLibrary.get_editor_world())
        return json.dumps({"success": True, "message": "Actor selection inverted."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during selection inversion: {e}"})

def ue_delete_actor_by_name(actor_name: str) -> str:
    """
    Deletes an actor with the specified name from the current level.

    :param actor_name: Name of the actor to delete.
    :return: JSON string indicating success or failure.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = subsystem.get_all_level_actors()
        deleted_actors = []

        for actor in all_actors:
            if actor.get_actor_label() == actor_name:
                if subsystem.destroy_actor(actor):
                    deleted_actors.append(actor_name)

        if deleted_actors:
            return json.dumps({
                "success": True,
                "message": f"Deleted actors: {deleted_actors}",
                "deleted_actors": deleted_actors
            })
        else:
            return json.dumps({"success": False, "message": f"No actor found with name: {actor_name}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during actor deletion: {e}"})

def ue_list_all_actors_with_locations() -> str:
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
        return json.dumps({"success": False, "message": f"Error during actor listing: {e}"})

def ue_spawn_actor_from_class(class_path: str, location: list, rotation: list = None) -> str:
    """
    Spawns an actor from the specified class path at the given location and rotation
    using unreal.EditorLevelLibrary.spawn_actor_from_class.

    :param class_path: Path to the actor class (e.g., "/Game/Blueprints/MyActorBP.MyActorBP_C" or "/Script/Engine.StaticMeshActor").
    :param location: [x, y, z] coordinates for the actor spawn position.
    :param rotation: Optional [pitch, yaw, roll] for the actor spawn rotation. Defaults to [0.0, 0.0, 0.0].
    :return: JSON string indicating success or failure and actor label/path if spawned.
    """
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
            rot_rotation = unreal.Rotator(float(rotation[0]), float(rotation[1]), float(rotation[2]))

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
        return json.dumps({"success": False, "message": f"Error during spawn_actor_from_class (EditorLevelLibrary): {str(e)}", "type": type(e).__name__})

def ue_get_static_mesh_asset_details(asset_path: str) -> str:
    """
    Retrieves the bounding box and dimensions of a static mesh asset.

    :param asset_path: Path to the static mesh asset (e.g., "/Game/Meshes/MyCube.MyCube").
    :return: JSON string with asset details including bounding box and dimensions.
    """
    try:
        static_mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not static_mesh:
            return json.dumps({"success": False, "message": f"Failed to load asset: {asset_path}"})

        if not isinstance(static_mesh, unreal.StaticMesh):
            return json.dumps({
                "success": False,
                "message": f"Asset at path {asset_path} is not a StaticMesh. Actual type: {type(static_mesh).__name__}"
            })

        bounding_box = static_mesh.get_bounding_box()  # This is unreal.Box
        min_b = bounding_box.min
        max_b = bounding_box.max
        dimensions = max_b - min_b

        return json.dumps({
            "success": True,
            "asset_path": asset_path,
            "bounding_box_min": [min_b.x, min_b.y, min_b.z],
            "bounding_box_max": [max_b.x, max_b.y, max_b.z],
            "dimensions": {"x": dimensions.x, "y": dimensions.y, "z": dimensions.z}
        })
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error getting static mesh asset details for {asset_path}: {str(e)}", "type": type(e).__name__})

def ue_get_all_actors_details() -> str:
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
            
            # Get actor bounds (origin and extent)
            # bOnlyCollidingComponents=False to get the bounds of all components, not just collision.
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
            
            # If it's a static mesh actor, try to get the path of the static mesh asset
            if isinstance(actor, unreal.StaticMeshActor):
                sm_component = actor.static_mesh_component
                if sm_component and sm_component.static_mesh:
                    detail["static_mesh_asset_path"] = sm_component.static_mesh.get_path_name()

            actors_details.append(detail)

        return json.dumps({"success": True, "actors": actors_details})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error listing all actors details: {str(e)}", "type": type(e).__name__})

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

def ue_set_actor_transform(actor_label: str, location: list = None, rotation: list = None, scale: list = None) -> str:
    """
    Sets the transform (location, rotation, scale) of a specified actor.
    Any component of the transform not provided will remain unchanged.
    This operation is wrapped in a ScopedEditorTransaction.

    :param actor_label: The label of the actor to modify.
    :param location: Optional new location [x, y, z].
    :param rotation: Optional new rotation [pitch, yaw, roll].
    :param scale: Optional new scale [x, y, z].
    :return: JSON string indicating success or failure.
    """
    transaction_description = f"MCP: Set Transform for actor {actor_label}"
    try:
        actor_to_modify = _get_actor_by_label(actor_label)
        if not actor_to_modify:
            return json.dumps({"success": False, "message": f"Actor with label '{actor_label}' not found."})

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
                    new_rot = unreal.Rotator(float(rotation[0]), float(rotation[1]), float(rotation[2]))
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
                return json.dumps({"success": True, "message": f"No transform properties provided for actor '{actor_label}'. Actor was not modified."})

            return json.dumps({"success": True, "message": f"Actor '{actor_label}' transform updated for: {', '.join(modified_properties)}."})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error setting transform for actor '{actor_label}': {str(e)}", "type": type(e).__name__})

def ue_set_actor_location(actor_label: str, location: list) -> str:
    """
    Sets the location of a specified actor.
    Wraps the call to ue_set_actor_transform.
    """
    return ue_set_actor_transform(actor_label, location=location)

def ue_set_actor_rotation(actor_label: str, rotation: list) -> str:
    """
    Sets the rotation of a specified actor.
    Wraps the call to ue_set_actor_transform.
    """
    return ue_set_actor_transform(actor_label, rotation=rotation)

def ue_set_actor_scale(actor_label: str, scale: list) -> str:
    """
    Sets the scale of a specified actor.
    Wraps the call to ue_set_actor_transform.
    """
    return ue_set_actor_transform(actor_label, scale=scale)

def ue_spawn_actor_on_surface_with_raycast(
    asset_or_class_path: str, 
    ray_start: list, 
    ray_end: list, 
    is_class_path: bool = True,
    desired_rotation: list = None,
    align_to_surface_normal: bool = False,
    trace_channel: str = 'Visibility',
    actors_to_ignore: list = None
) -> str:
    """
    Spawns an actor on the surface hit by a raycast. 
    The actor can be spawned from an asset path or a class path.
    The operation is wrapped in a ScopedEditorTransaction.

    :param asset_or_class_path: Path to the asset or class.
    :param ray_start: List of 3 floats for the ray start location [x, y, z].
    :param ray_end: List of 3 floats for the ray end location [x, y, z].
    :param is_class_path: True if asset_or_class_path is a class path, False for asset path.
    :param desired_rotation: Optional list of 3 floats for desired actor rotation [pitch, yaw, roll].
                               If align_to_surface_normal is True, yaw from this rotation might be used.
    :param align_to_surface_normal: If True, aligns the actor's Z-axis with the surface normal and 
                                     optionally uses yaw from desired_rotation.
    :param trace_channel: The trace channel to use for the raycast (e.g., 'Visibility', 'Camera').
    :param actors_to_ignore: Optional list of actor labels to ignore during the raycast.
    :return: JSON string indicating success or failure and actor details if spawned.
    """
    transaction_description = f"MCP: Spawn Actor on Surface via Raycast ({asset_or_class_path})"

    if desired_rotation is None:
        desired_rotation = [0.0, 0.0, 0.0]

    if len(ray_start) != 3 or len(ray_end) != 3 or len(desired_rotation) != 3:
        return json.dumps({"success": False, "message": "Invalid vector/rotator format. Expected lists of 3 floats."})

    try:
        start_loc = unreal.Vector(float(ray_start[0]), float(ray_start[1]), float(ray_start[2]))
        end_loc = unreal.Vector(float(ray_end[0]), float(ray_end[1]), float(ray_end[2]))
        
        ignored_actors_objects = []
        if actors_to_ignore:
            for label in actors_to_ignore:
                actor = _get_actor_by_label(label)
                if actor:
                    ignored_actors_objects.append(actor)

        # Perform the line trace
        hit_result = unreal.SystemLibrary.line_trace_single(
            world_context_object=unreal.EditorLevelLibrary.get_editor_world(), # Get world context for editor utilities
            start=start_loc,
            end=end_loc,
            trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
            trace_complex=True, # Trace against complex collision if available
            actors_to_ignore=ignored_actors_objects,
            draw_debug_type=unreal.DrawDebugTrace.NONE, # Or FOR_DURATION to debug
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
        spawn_rotation_final = unreal.Rotator(float(desired_rotation[0]), float(desired_rotation[1]), float(desired_rotation[2]))

        if align_to_surface_normal:
            surface_normal = normal
            rot_from_normal_z = unreal.MathLibrary.make_rot_from_z(surface_normal)
            spawn_rotation_final = unreal.Rotator(rot_from_normal_z.pitch, float(desired_rotation[1]), rot_from_normal_z.roll)

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
                actor_spawned = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(asset, spawn_location, spawn_rotation_final)

            if actor_spawned:
                return json.dumps({
                    "success": True, 
                    "actor_label": actor_spawned.get_actor_label(), 
                    "actor_path": actor_spawned.get_path_name(),
                    "location": [spawn_location.x, spawn_location.y, spawn_location.z],
                    "rotation": [spawn_rotation_final.pitch, spawn_rotation_final.yaw, spawn_rotation_final.roll],
                    "hit_surface_normal": [normal.x, normal.y, normal.z]
                })
            else:
                return json.dumps({"success": False, "message": "Failed to spawn actor after raycast hit."})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during spawn_actor_on_surface_with_raycast: {str(e)}", "type": type(e).__name__})

def ue_get_actors_in_editor_view_frustum() -> str:
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
        return json.dumps({"success": False, "message": f"Error in ue_get_actors_in_editor_view_frustum: {str(e)}", "type": type(e).__name__})
