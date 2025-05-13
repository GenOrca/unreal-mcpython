from fastmcp import FastMCP
import socket
import json
from typing import Annotated, Optional, List
from pydantic import Field

mcp = FastMCP("Unreal MCP Server")

# Define the name of the Python module as it's known within Unreal's Python environment
UNREAL_PYTHON_MODULE = "mcp_unreal_actions"

@mcp.tool(
    name="unreal_print_message",
    description="Sends a message to be printed in the Unreal Engine output log.",
    tags={"unreal", "logging", "debug"}
)
def run_unreal_print(
    message: Annotated[str, Field(description="The message string to log in Unreal.", min_length=1, max_length=1024)]
) -> dict:
    """Internal: Calls ue_print_message in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_print_message",
        "args": [message]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_find_asset",
    description="Finds Unreal Engine assets by name and/or type within the project's /Game directory. At least one of name or asset_type must be provided.",
    tags={"unreal", "asset", "search", "content-browser"}
)
def find_asset_by_query(
    name: Annotated[Optional[str], Field(description="Substring to match in asset names. Case-sensitive.", min_length=1)] = None,
    asset_type: Annotated[Optional[str], Field(description="Unreal class name of the asset type to filter by (e.g., 'StaticMesh', 'Blueprint').", min_length=1)] = None
) -> dict:
    """Internal: Calls ue_find_asset_by_query in Unreal."""
    if name is None and asset_type is None:
        return {"success": False, "message": "At least one of 'name' or 'asset_type' must be provided."}

    args = []
    if name is not None:
        args.append(name)
    else:
        args.append(None) # Explicitly pass None if name is not provided

    if asset_type is not None:
        args.append(asset_type)
    else:
        args.append(None) # Explicitly pass None if asset_type is not provided
    
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_find_asset_by_query",
        "args": args
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_spawn_actor_from_asset",
    description="Spawns an actor in the Unreal Engine level from a specified asset path and at a given location.",
    tags={"unreal", "actor", "spawn", "level-editing", "asset"}
)
def spawn_actor_from_object(
    asset_path: Annotated[str, Field(description="Path to the asset in the Content Browser (e.g., '/Game/Meshes/MyCube.MyCube').", min_length=1)],
    location: Annotated[List[float], Field(description="List of 3 floats [X, Y, Z] for the actor's spawn position in world space.", min_items=3, max_items=3)]
) -> dict:
    """Internal: Calls ue_spawn_actor_from_object in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_spawn_actor_from_object",
        "args": [asset_path, location]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_duplicate_selected_actors",
    description="Duplicates currently selected actors in the Unreal Engine editor and applies a positional offset to each new duplicate.",
    tags={"unreal", "actor", "duplicate", "level-editing", "selection"}
)
def duplicate_selected_actors_with_offset(
    offset: Annotated[List[float], Field(description="List of 3 floats [X, Y, Z] representing the positional offset to apply.", min_items=3, max_items=3)]
) -> dict:
    """Internal: Calls ue_duplicate_selected_actors_with_offset in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_duplicate_selected_actors_with_offset",
        "args": [offset]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_select_all_actors",
    description="Selects all actors in the current Unreal Engine level.",
    tags={"unreal", "actor", "select", "level-editing"}
)
def select_all_actors() -> dict:
    """Internal: Calls ue_select_all_actors in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_select_all_actors",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_invert_actor_selection",
    description="Inverts the current actor selection in the Unreal Engine level.",
    tags={"unreal", "actor", "select", "level-editing"}
)
def invert_actor_selection() -> dict:
    """Internal: Calls ue_invert_actor_selection in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_invert_actor_selection",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_delete_actor_by_label",
    description="Deletes an actor from the current Unreal Engine level, identified by its label.",
    tags={"unreal", "actor", "delete", "level-editing"}
)
def delete_actor_by_name(
    actor_name: Annotated[str, Field(description="The exact label of the actor to delete.", min_length=1)]
) -> dict:
    """Internal: Calls ue_delete_actor_by_name in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_delete_actor_by_name",
        "args": [actor_name]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_list_all_actors_locations",
    description="Lists all actors in the current Unreal Engine level along with their world locations.",
    tags={"unreal", "actor", "list", "location", "level-editing"}
)
def list_all_actors_with_locations() -> dict:
    """Internal: Calls ue_list_all_actors_with_locations in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_list_all_actors_with_locations",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_spawn_actor_from_class",
    description="Spawns an actor in the Unreal Engine level from a specified class path at a given location and optional rotation.",
    tags={"unreal", "actor", "spawn", "level-editing", "class", "blueprint"}
)
def spawn_actor_from_class(
    class_path: Annotated[str, Field(description="Path to the actor class (e.g., '/Game/Blueprints/MyActorBP.MyActorBP_C', '/Script/Engine.StaticMeshActor').", min_length=1)],
    location: Annotated[List[float], Field(description="List of 3 floats [X, Y, Z] for the actor's spawn position.", min_items=3, max_items=3)],
    rotation: Annotated[Optional[List[float]], Field(description="Optional list of 3 floats [Pitch, Yaw, Roll] for spawn rotation. Defaults to [0,0,0].", min_items=3, max_items=3)] = None
) -> dict:
    """Internal: Calls ue_spawn_actor_from_class in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_spawn_actor_from_class",
        "args": [class_path, location, rotation] if rotation else [class_path, location]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_get_static_mesh_details",
    description="Retrieves details for a static mesh asset, including its bounding box and dimensions.",
    tags={"unreal", "asset", "staticmesh", "details", "geometry"}
)
def get_static_mesh_asset_details(
    asset_path: Annotated[str, Field(description="Path to the static mesh asset (e.g., '/Game/Meshes/MyCube.MyCube').", min_length=1)]
) -> dict:
    """Internal: Calls ue_get_static_mesh_asset_details in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_static_mesh_asset_details",
        "args": [asset_path]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_get_all_actors_details",
    description="Retrieves detailed information for all actors in the current Unreal Engine level.",
    tags={"unreal", "actor", "list", "details", "level-editing"}
)
def get_all_actors_details() -> dict:
    """Internal: Calls ue_get_all_actors_details in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_all_actors_details",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_set_actor_transform",
    description="Sets the transform (location, rotation, scale) of a specified actor in Unreal Engine by its label.",
    tags={"unreal", "actor", "transform", "location", "rotation", "scale", "level-editing"}
)
def set_actor_transform(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.", min_length=1)],
    location: Annotated[Optional[List[float]], Field(description="Optional new location [X, Y, Z].", min_items=3, max_items=3)] = None,
    rotation: Annotated[Optional[List[float]], Field(description="Optional new rotation [Pitch, Yaw, Roll].", min_items=3, max_items=3)] = None,
    scale: Annotated[Optional[List[float]], Field(description="Optional new scale [X, Y, Z].", min_items=3, max_items=3)] = None
) -> dict:
    """Internal: Calls ue_set_actor_transform in Unreal."""
    args = [actor_label]
    args.append(location if location is not None else None)
    args.append(rotation if rotation is not None else None)
    args.append(scale if scale is not None else None)

    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_transform",
        "args": args
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_set_actor_location",
    description="Sets the location of a specified actor in Unreal Engine by its label.",
    tags={"unreal", "actor", "location", "level-editing"}
)
def set_actor_location(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.", min_length=1)],
    location: Annotated[List[float], Field(description="New location [X, Y, Z].", min_items=3, max_items=3)]
) -> dict:
    """Internal: Calls ue_set_actor_location in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_location",
        "args": [actor_label, location]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_set_actor_rotation",
    description="Sets the rotation of a specified actor in Unreal Engine by its label.",
    tags={"unreal", "actor", "rotation", "level-editing"}
)
def set_actor_rotation(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.", min_length=1)],
    rotation: Annotated[List[float], Field(description="New rotation [Pitch, Yaw, Roll].", min_items=3, max_items=3)]
) -> dict:
    """Internal: Calls ue_set_actor_rotation in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_rotation",
        "args": [actor_label, rotation]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_set_actor_scale",
    description="Sets the scale of a specified actor in Unreal Engine by its label.",
    tags={"unreal", "actor", "scale", "level-editing"}
)
def set_actor_scale(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.", min_length=1)],
    scale: Annotated[List[float], Field(description="New scale [X, Y, Z].", min_items=3, max_items=3)]
) -> dict:
    """Internal: Calls ue_set_actor_scale in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_scale",
        "args": [actor_label, scale]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_spawn_actor_on_surface_raycast",
    description="Spawns an actor on a surface detected by a raycast in Unreal Engine. Can use asset or class path.",
    tags={"unreal", "actor", "spawn", "raycast", "surface", "level-editing"}
)
def spawn_actor_on_surface_with_raycast(
    asset_or_class_path: Annotated[str, Field(description="Path to asset (e.g., /Game/Meshes/Cube.Cube) or class (e.g., /Game/BP/MyActor.MyActor_C).", min_length=1)],
    ray_start: Annotated[List[float], Field(description="List of 3 floats [X, Y, Z] for ray start location.", min_items=3, max_items=3)],
    ray_end: Annotated[List[float], Field(description="List of 3 floats [X, Y, Z] for ray end location.", min_items=3, max_items=3)],
    is_class_path: Annotated[bool, Field(True, description="True if asset_or_class_path is a class path, False for asset path.")] = True,
    desired_rotation: Annotated[Optional[List[float]], Field(description="Optional list of 3 floats [Pitch, Yaw, Roll] for desired actor rotation.", min_items=3, max_items=3)] = None,
    align_to_surface_normal: Annotated[bool, Field(False, description="If True, aligns actor's Z-axis with the surface normal.")] = False,
    trace_channel: Annotated[str, Field("Visibility", description="Trace channel for raycast (e.g., 'Visibility', 'Camera').")] = 'Visibility',
    actors_to_ignore: Annotated[Optional[List[str]], Field(description="Optional list of actor labels to ignore during raycast.")] = None
) -> dict:
    """Internal: Calls ue_spawn_actor_on_surface_with_raycast in Unreal."""
    args = [
        asset_or_class_path,
        ray_start,
        ray_end,
        is_class_path,
        desired_rotation,
        align_to_surface_normal,
        trace_channel,
        actors_to_ignore
    ]
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_spawn_actor_on_surface_with_raycast",
        "args": args
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_get_actors_in_view_frustum",
    description="Gets a list of actors potentially visible within the active Unreal Engine editor viewport's frustum.",
    tags={"unreal", "actor", "list", "frustum", "viewport", "camera", "visibility"}
)
def get_actors_in_editor_view_frustum() -> dict:
    """Internal: Calls ue_get_actors_in_editor_view_frustum in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_actors_in_editor_view_frustum",
        "args": []
    }
    return send_to_unreal(command)

# --- Material Editing Tools ---

@mcp.tool(
    name="unreal_create_material_expression",
    description="Creates a new material expression node within a specified material in Unreal Engine.",
    tags={"unreal", "material", "expression", "shader", "material-editor"}
)
def create_material_expression(
    material_path: Annotated[str, Field(description="Path to the Material asset (e.g., '/Game/Materials/MyMaterial.MyMaterial').", min_length=1)],
    expression_class_name: Annotated[str, Field(description="Class name of the expression (e.g., 'MaterialExpressionTextureCoordinate').", min_length=1)],
    node_pos_x: Annotated[int, Field(0, description="X position of the new expression node in the material editor graph.")] = 0,
    node_pos_y: Annotated[int, Field(0, description="Y position of the new expression node in the material editor graph.")] = 0
) -> dict:
    """Internal: Calls ue_create_material_expression in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_create_material_expression",
        "args": [material_path, expression_class_name, node_pos_x, node_pos_y]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_connect_material_expressions",
    description="Connects two material expressions within a material in Unreal Engine.",
    tags={"unreal", "material", "expression", "shader", "material-editor", "graph"}
)
def connect_material_expressions(
    material_path: Annotated[str, Field(description="Path to the Material asset.", min_length=1)],
    from_expression_identifier: Annotated[str, Field(description="Name (desc) or class name of the source expression.", min_length=1)],
    from_output_name: Annotated[str, Field(description="Name of the output pin on source (e.g., '', 'R', 'G'). Empty for default.")],
    to_expression_identifier: Annotated[str, Field(description="Name (desc) or class name of the target expression.", min_length=1)],
    to_input_name: Annotated[str, Field(description="Name of the input pin on target (e.g., 'UVs', 'Time'). Empty for default.")],
    from_expression_class_name: Annotated[Optional[str], Field(None, description="Optional: Specific class name of source expression for disambiguation.")] = None,
    to_expression_class_name: Annotated[Optional[str], Field(None, description="Optional: Specific class name of target expression for disambiguation.")] = None
) -> dict:
    """Internal: Calls ue_connect_material_expressions in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_connect_material_expressions",
        "args": [
            material_path,
            from_expression_identifier,
            from_output_name,
            to_expression_identifier,
            to_input_name,
            from_expression_class_name,
            to_expression_class_name
        ]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_recompile_material",
    description="Triggers a recompile of a specified material in Unreal Engine.",
    tags={"unreal", "material", "shader", "compile", "material-editor"}
)
def recompile_material(
    material_path: Annotated[str, Field(description="Path to the Material asset to recompile.", min_length=1)]
) -> dict:
    """Internal: Calls ue_recompile_material in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_recompile_material",
        "args": [material_path]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_get_material_instance_scalar_param",
    description="Gets the current scalar (float) parameter value from a Material Instance in Unreal Engine.",
    tags={"unreal", "material", "instance", "parameter", "scalar", "shader"}
)
def get_material_instance_scalar_parameter_value(
    instance_path: Annotated[str, Field(description="Path to the MaterialInstanceConstant asset.", min_length=1)],
    parameter_name: Annotated[str, Field(description="Name of the scalar parameter to retrieve.", min_length=1)]
) -> dict:
    """Internal: Calls ue_get_material_instance_scalar_parameter_value in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_material_instance_scalar_parameter_value",
        "args": [instance_path, parameter_name]
    }
    return send_to_unreal(command)

@mcp.tool(
    name="unreal_set_material_instance_scalar_param",
    description="Sets the scalar (float) parameter value for a Material Instance in Unreal Engine.",
    tags={"unreal", "material", "instance", "parameter", "scalar", "shader"}
)
def set_material_instance_scalar_parameter_value(
    instance_path: Annotated[str, Field(description="Path to the MaterialInstanceConstant asset.", min_length=1)],
    parameter_name: Annotated[str, Field(description="Name of the scalar parameter to set.", min_length=1)],
    value: Annotated[float, Field(description="The float value to set for the scalar parameter.")]
) -> dict:
    """Internal: Calls ue_set_material_instance_scalar_parameter_value in Unreal."""
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_material_instance_scalar_parameter_value",
        "args": [instance_path, parameter_name, value]
    }
    return send_to_unreal(command)

def send_to_unreal(command: dict) -> dict:
    """
    Sends a JSON command to the UnrealMCPython socket server (127.0.0.1:12029) and returns the result.
    """
    HOST = '127.0.0.1'
    PORT = 12029
    try:
        # JSON serialization - keep non-ASCII characters as is with ensure_ascii=False
        json_str = json.dumps(command, ensure_ascii=False)
        message_bytes = json_str.encode('utf-8')  # Renamed for clarity

        with socket.create_connection((HOST, PORT), timeout=10) as sock:  # Increased timeout
            sock.sendall(message_bytes)
            
            # Buffer to receive data
            response_buffer = b''
            # It's crucial to have a reliable way to determine the end of the message.
            # Assuming the Unreal side sends a complete JSON and then closes or sends EOF.
            # If messages can be very large or chunked without clear delimiters, this might need a more robust protocol
            # (e.g., length-prefixing or newline termination if JSON is guaranteed to be single-line).
            # For now, we read until socket indicates no more data for this send.
            while True:
                chunk = sock.recv(8192) # Increased buffer size
                if not chunk:
                    # This break is critical. It happens when the server closes its side of the connection
                    # or when all data for this particular send has been received.
                    break
                response_buffer += chunk
            
            if not response_buffer:
                return {"success": False, "message": "No response received from Unreal."}

            try:
                response_str = response_buffer.decode('utf-8')
                # Attempt to parse the full response as JSON
                # This assumes Unreal sends a single, complete JSON object per request.
                # If multiple JSON objects are sent back-to-back without delimiters, this will fail.
                outer_response = json.loads(response_str)
                
                # Process the parsed JSON
                if outer_response.get("success") and "result" in outer_response:
                    try:
                        # The 'result' field itself is expected to be a JSON string
                        inner_result_str = outer_response["result"]
                        if isinstance(inner_result_str, str): # Check if it's actually a string
                            inner_result = json.loads(inner_result_str)
                            return {
                                "success": True,
                                "message": outer_response.get("message", "Successfully executed."),
                                "data": inner_result
                            }
                        else: # If result is not a string, but already parsed (e.g. dict, list)
                             return {
                                "success": True,
                                "message": outer_response.get("message", "Successfully executed."),
                                "data": inner_result_str # return as is
                            }
                    except json.JSONDecodeError as je_inner:
                        # This means the 'result' field was not a valid JSON string
                        return {
                            "success": True, # The outer command might have succeeded
                            "message": outer_response.get("message", "Command sent, but result field was not valid JSON."),
                            "raw_result": outer_response.get('result') # Return the raw result field
                        }
                    except Exception as e_inner: # Catch other errors during inner processing
                        return {
                            "success": False,
                            "message": f"Error processing inner result: {str(e_inner)}",
                            "raw_result": outer_response.get('result')
                        }
                else: # If not successful or no 'result' field in the way we expect
                    return outer_response

            except json.JSONDecodeError as je:
                # This means the entire response_str was not valid JSON
                return {"success": False, "message": f"Failed to decode JSON response from Unreal: {je}", "raw_response": response_str}
            except Exception as e_response_processing: # Catch other errors during response processing
                 return {"success": False, "message": f"Error processing response from Unreal: {str(e_response_processing)}", "raw_response": response_buffer.decode('utf-8', errors='ignore')}


    except socket.timeout:
        return {"success": False, "message": f"Socket timeout: No response from Unreal within {sock.gettimeout()} seconds."}
    except ConnectionRefusedError:
        return {"success": False, "message": "Connection refused. Ensure Unreal MCPython TCP server is active and listening on port 12029."}
    except socket.error as se: # More specific socket errors
        return {"success": False, "message": f"Socket error: {se}"}
    except Exception as e: # Catch-all for other unexpected errors
        return {"success": False, "message": f"An unexpected error occurred in send_to_unreal: {e}"}

if __name__ == "__main__":
    mcp.run()