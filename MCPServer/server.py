from fastmcp import FastMCP
import socket
import json

mcp = FastMCP("Unreal MCP Server")

# Define the name of the Python module as it's known within Unreal's Python environment
UNREAL_PYTHON_MODULE = "mcp_unreal_actions"

@mcp.tool()
def run_unreal_print(message: str) -> dict:
    """
    Sends a command to Unreal to execute a pre-defined print function.
    """
    command = {
        "type": "python_call",  # Indicate a function call
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_print_message",
        "args": [message]  # Arguments for the function
    }
    return send_to_unreal(command)

@mcp.tool()
def find_asset_by_name(name: str) -> dict:
    """
    Sends a command to Unreal to find an asset by name using a pre-defined function.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_find_asset_by_name",
        "args": [name]
    }
    return send_to_unreal(command)

@mcp.tool()
def spawn_actor_from_object(asset_path: str, location: list[float]) -> dict:
    """
    Sends a command to Unreal to spawn an actor using a pre-defined function.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_spawn_actor_from_object",
        "args": [asset_path, location]  # location will be a list
    }
    return send_to_unreal(command)

@mcp.tool()
def duplicate_selected_actors_with_offset(offset: list[float]) -> dict:
    """
    Sends a command to Unreal to duplicate selected actors with a given offset.
    Offset should be a list of 3 floats [x, y, z].
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_duplicate_selected_actors_with_offset",
        "args": [offset]
    }
    return send_to_unreal(command)

@mcp.tool()
def select_all_actors() -> dict:
    """
    Sends a command to Unreal to select all actors in the current level.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_select_all_actors",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool()
def invert_actor_selection() -> dict:
    """
    Sends a command to Unreal to invert the current actor selection.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_invert_actor_selection",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool()
def delete_actor_by_name(actor_name: str) -> dict:
    """
    Sends a command to Unreal to delete an actor by its name.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_delete_actor_by_name",
        "args": [actor_name]
    }
    return send_to_unreal(command)

@mcp.tool()
def list_all_actors_with_locations() -> dict:
    """
    Sends a command to Unreal to list all actors and their locations.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_list_all_actors_with_locations",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool()
def spawn_actor_from_class(class_path: str, location: list[float], rotation: list[float] = None) -> dict:
    """
    Sends a command to Unreal to spawn an actor from a class path using EditorLevelLibrary.
    Location should be a list of 3 floats [x, y, z].
    Rotation (optional) should be a list of 3 floats [pitch, yaw, roll].
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_spawn_actor_from_class",
        "args": [class_path, location, rotation] if rotation else [class_path, location]
    }
    return send_to_unreal(command)

@mcp.tool()
def get_static_mesh_asset_details(asset_path: str) -> dict:
    """
    Sends a command to Unreal to get details of a static mesh asset,
    including bounding box and dimensions.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_static_mesh_asset_details",
        "args": [asset_path]
    }
    return send_to_unreal(command)

@mcp.tool()
def get_all_actors_details() -> dict:
    """
    Sends a command to Unreal to get detailed information for all actors
    in the current level, including location, rotation, and bounds.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_all_actors_details",
        "args": []
    }
    return send_to_unreal(command)

@mcp.tool()
def set_actor_transform(actor_label: str, location: list[float] = None, rotation: list[float] = None, scale: list[float] = None) -> dict:
    """
    Sends a command to Unreal to set the transform (location, rotation, scale)
    of an actor specified by its label. All parameters are optional.
    """
    args = [actor_label]
    # We need to pass None placeholders if a value isn't provided, 
    # as the Python function ue_set_actor_transform expects them in order.
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

@mcp.tool()
def set_actor_location(actor_label: str, location: list[float]) -> dict:
    """
    Sends a command to Unreal to set the location of an actor.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_location",
        "args": [actor_label, location]
    }
    return send_to_unreal(command)

@mcp.tool()
def set_actor_rotation(actor_label: str, rotation: list[float]) -> dict:
    """
    Sends a command to Unreal to set the rotation of an actor.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_rotation",
        "args": [actor_label, rotation]
    }
    return send_to_unreal(command)

@mcp.tool()
def set_actor_scale(actor_label: str, scale: list[float]) -> dict:
    """
    Sends a command to Unreal to set the scale of an actor.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_set_actor_scale",
        "args": [actor_label, scale]
    }
    return send_to_unreal(command)

@mcp.tool()
def spawn_actor_on_surface_with_raycast(
    asset_or_class_path: str,
    ray_start: list[float],
    ray_end: list[float],
    is_class_path: bool = True,
    desired_rotation: list[float] = None,
    align_to_surface_normal: bool = False,
    trace_channel: str = 'Visibility',
    actors_to_ignore: list[str] = None
) -> dict:
    """
    Sends a command to Unreal to spawn an actor on a surface detected by a raycast.
    The actor can be spawned from an asset path or a class path.
    Optionally aligns the actor to the surface normal, uses a specific trace channel,
    and ignores certain actors during the raycast.
    """
    args = [
        asset_or_class_path,
        ray_start,
        ray_end,
        is_class_path,
        desired_rotation,  # Pass None if not provided by user, ue_ function handles default
        align_to_surface_normal,
        trace_channel,
        actors_to_ignore   # Pass None if not provided by user, ue_ function handles default
    ]

    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_spawn_actor_on_surface_with_raycast",
        "args": args
    }
    return send_to_unreal(command)

@mcp.tool()
def get_actors_in_editor_view_frustum() -> dict:
    """
    Sends a command to Unreal to get a list of actors potentially visible
    within the active editor viewport's frustum.
    """
    command = {
        "type": "python_call",
        "module": UNREAL_PYTHON_MODULE,
        "function": "ue_get_actors_in_editor_view_frustum",
        "args": []
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

        print(f"Sending to Unreal: {json_str}")

        with socket.create_connection((HOST, PORT), timeout=10) as sock:  # Increased timeout slightly
            sock.sendall(message_bytes)
            response = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk

            if not response:
                print("No response received from Unreal.")
                return {"success": False, "message": "No response received from Unreal."}

            try:
                response_str = response.decode('utf-8')
                print(f"Raw response from Unreal: {response_str}")
                outer_response = json.loads(response_str)
                if outer_response.get("success") and "result" in outer_response:
                    try:
                        inner_result = json.loads(outer_response["result"])
                        return {
                            "success": True,
                            "message": outer_response.get("message", ""),
                            "data": inner_result
                        }
                    except json.JSONDecodeError as je_inner:
                        print(f"Inner JSON decode error for 'result' field: {je_inner}, raw result: {outer_response['result']}")
                        return {
                            "success": True,
                            "message": outer_response.get("message", "Result field was not valid JSON."),
                            "raw_result": outer_response['result']
                        }
                else:
                    return outer_response

            except json.JSONDecodeError as je:
                print(f"JSON decode error for outer response: {je}, Raw response: {response_str}")
                return {"success": False, "message": f"Outer JSON decoding error: {je}", "raw_response": response_str}
    except socket.timeout:
        print(f"Socket timeout communicating with Unreal on {HOST}:{PORT}")
        return {"success": False, "message": f"Socket timeout communicating with Unreal"}
    except ConnectionRefusedError:
        print(f"Connection refused by Unreal on {HOST}:{PORT}. Is the Unreal MCPython TCP server running?")
        return {"success": False, "message": "Connection refused. Ensure Unreal MCPython TCP server is active."}
    except Exception as e:
        print(f"Error communicating with Unreal: {e}")
        return {"success": False, "message": f"Connection/Execution error: {e}"}

if __name__ == "__main__":
    mcp.run()