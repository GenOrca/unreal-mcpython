# Actor management actions for Unreal Engine

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

def ue_spawn_actor_from_object(asset_path: str = None, location: list = None) -> str:
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

def ue_duplicate_selected_actors_with_offset(offset: list = None) -> str:
    """
    Duplicates all selected actors in the editor and applies a position offset to each duplicate.

    :param offset: [x, y, z] offset to apply to each duplicated actor.
    :return: JSON string indicating success or failure and details of duplicated actors.
    """
    if offset is None:
        return json.dumps({"success": False, "message": "Required parameter 'offset' is missing."})

    if len(offset) != 3:
        return json.dumps({"success": False, "message": "Invalid offset format. Expected list of 3 floats."})

    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        selected_actors = subsystem.get_selected_level_actors()
        if not selected_actors:
            return json.dumps({"success": False, "message": "No actors selected."})

        duplicated_actors_labels = []
        with unreal.ScopedEditorTransaction("MCP: Duplicate Selected Actors with Offset") as trans:
            for actor in selected_actors:
                offset_vector = unreal.Vector(float(offset[0]), float(offset[1]), float(offset[2]))
                new_actors = unreal.EditorLevelLibrary.duplicate_actors([actor])
                if new_actors and len(new_actors) > 0:
                    duplicated_actor = new_actors[0]
                    original_location = duplicated_actor.get_actor_location()
                    new_location = original_location + offset_vector
                    duplicated_actor.set_actor_location(new_location, False, False) # bSweep, bTeleport
                    duplicated_actors_labels.append(duplicated_actor.get_actor_label())
                else:
                    unreal.log_warning(f"Failed to duplicate actor: {actor.get_actor_label()}")

        return json.dumps({
            "success": True,
            "message": f"Duplicated {len(duplicated_actors_labels)} actors with offset {offset}.",
            "duplicated_actors": duplicated_actors_labels
        })
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during duplication: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_select_all_actors() -> str:
    """
    Selects all actors in the current level.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        subsystem.select_all_level_actors()
        return json.dumps({"success": True, "message": "All actors selected."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during selection: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_invert_actor_selection() -> str:
    """
    Inverts the selection of actors in the current level.
    """
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        subsystem.invert_selected_level_actors()
        return json.dumps({"success": True, "message": "Actor selection inverted."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during selection inversion: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_delete_actor_by_name(actor_name: str = None) -> str:
    """
    Deletes an actor with the specified name (label) from the current level.
    Wrapped in a ScopedEditorTransaction.
    """
    if actor_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_name' is missing."})

    transaction_description = f"MCP: Delete Actor by Name ({actor_name})"
    try:
        actor_to_delete = _get_actor_by_label(actor_name)
        if not actor_to_delete:
            return json.dumps({"success": False, "message": f"No actor found with name (label): {actor_name}"})

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if subsystem.destroy_actor(actor_to_delete):
                return json.dumps({
                    "success": True,
                    "message": f"Actor '{actor_name}' deleted.",
                    "deleted_actor_label": actor_name
                })
            else:
                return json.dumps({"success": False, "message": f"Failed to delete actor '{actor_name}' using subsystem.destroy_actor."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during actor deletion: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

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
        return json.dumps({"success": False, "message": f"Error during actor listing: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})

def ue_spawn_actor_from_class(class_path: str = None, location: list = None, rotation: list = None) -> str:
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

def ue_set_actor_transform(actor_label: str = None, location: list = None, rotation: list = None, scale: list = None) -> str:
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

def ue_set_actor_location(actor_label: str = None, location: list = None) -> str:
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})
    if location is None:
        return json.dumps({"success": False, "message": "Required parameter 'location' is missing."})
    return ue_set_actor_transform(actor_label=actor_label, location=location)

def ue_set_actor_rotation(actor_label: str = None, rotation: list = None) -> str:
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})
    if rotation is None:
        return json.dumps({"success": False, "message": "Required parameter 'rotation' is missing."})
    return ue_set_actor_transform(actor_label=actor_label, rotation=rotation)

def ue_set_actor_scale(actor_label: str = None, scale: list = None) -> str:
    if actor_label is None:
        return json.dumps({"success": False, "message": "Required parameter 'actor_label' is missing."})
    if scale is None:
        return json.dumps({"success": False, "message": "Required parameter 'scale' is missing."})
    return ue_set_actor_transform(actor_label=actor_label, scale=scale)

def ue_spawn_actor_on_surface_with_raycast(
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

def ue_get_actors_in_editor_view_frustum() -> str:
    """
    Retrieves a list of actors that are potentially visible within the active editor viewport's frustum.
    This is an approximation.
    """
    try:
        cam_loc = None
        cam_rot = None
        v_fov_degrees = 90.0
        
        editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        if not editor_subsystem:
            return json.dumps({"success": False, "message": "Failed to get UnrealEditorSubsystem."})
        
        if hasattr(editor_subsystem, 'get_level_viewport_camera_info'):
            cam_loc, cam_rot = editor_subsystem.get_level_viewport_camera_info()
        else:
            try:
                level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditor)
                if level_editor_subsystem:
                     cam_loc, cam_rot, v_fov_degrees_actual = level_editor_subsystem.get_level_viewport_camera_info()
                else:
                    return json.dumps({"success": False, "message": "Failed to get LevelEditor subsystem for camera info."})

            except Exception as cam_ex:
                 return json.dumps({"success": False, "message": f"Could not get camera info via LevelEditor: {str(cam_ex)}"})

        if cam_loc is None or cam_rot is None:
            return json.dumps({"success": False, "message": "Failed to obtain camera location and rotation."})

        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = actor_subsystem.get_all_level_actors()
        visible_actors_details = []

        cam_forward_vec = cam_rot.get_forward_vector()
        cam_right_vec = cam_rot.get_right_vector()
        cam_up_vec = cam_rot.get_up_vector()

        h_fov_degrees = v_fov_degrees * (16.0/9.0)
        
        near_plane = 10.0
        far_plane = 100000.0

        planes = []
        planes.append(unreal.Plane(cam_loc + cam_forward_vec * near_plane, cam_forward_vec))
        planes.append(unreal.Plane(cam_loc + cam_forward_vec * far_plane, -cam_forward_vec))
        
        half_v_fov_rad = unreal.MathLibrary.degrees_to_radians(v_fov_degrees / 2.0)
        half_h_fov_rad = unreal.MathLibrary.degrees_to_radians(h_fov_degrees / 2.0)

        v_fov_rad_half = half_v_fov_rad

        for actor in all_actors:
            if not actor: continue

            bounds_origin, bounds_extent = actor.get_actor_bounds(False)
            actor_bounding_radius = bounds_extent.length()
            
            vec_to_actor_center = bounds_origin - cam_loc
            dist_to_actor_center = vec_to_actor_center.length()

            if dist_to_actor_center + actor_bounding_radius < near_plane or \
               dist_to_actor_center - actor_bounding_radius > far_plane:
                continue

            if dist_to_actor_center > 0:
                vec_to_actor_center_normalized = vec_to_actor_center.get_safe_normal()
                dot_product = cam_forward_vec.dot(vec_to_actor_center_normalized)
                
                angle_rad = unreal.MathLibrary.acos(dot_product)
                
                angular_radius_of_sphere_rad = 0
                if dist_to_actor_center > actor_bounding_radius:
                    angular_radius_of_sphere_rad = unreal.MathLibrary.asin(actor_bounding_radius / dist_to_actor_center)
                else:
                    angular_radius_of_sphere_rad = unreal.MathLibrary.PI

                if angle_rad > v_fov_rad_half + angular_radius_of_sphere_rad:
                    continue
            
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
                sm_component = None
                if hasattr(actor, 'get_static_mesh_component'):
                    sm_component = actor.get_static_mesh_component()
                elif hasattr(actor, 'static_mesh_component'):
                    sm_component = actor.static_mesh_component
                
                if sm_component and sm_component.static_mesh:
                    actor_details_dict["static_mesh_asset_path"] = sm_component.static_mesh.get_path_name()
            
            visible_actors_details.append(actor_details_dict)

        return json.dumps({"success": True, "visible_actors_estimate": visible_actors_details, "message": "Frustum culling is an estimate."})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error in ue_get_actors_in_editor_view_frustum: {str(e)}", "type": e.__name__, "traceback": traceback.format_exc()})
