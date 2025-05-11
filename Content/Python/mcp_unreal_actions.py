"""
Defines Python action functions to be executed within Unreal Engine.
"""
import unreal
import json
import sys

# Core dispatcher for executing dynamic Python commands received from the MCP server
def execute_action(module_name, function_name, args_list):
    """
    Dynamically imports and executes the specified function from the given module.

    :param module_name: Name of the module containing the function (e.g., "mcp_unreal_actions")
    :param function_name: Name of the function to call (e.g., "ue_print_message")
    :param args_list: List of arguments to pass to the target function
    :return: JSON-formatted string representing the function's result
    """
    try:
        target_module = __import__(module_name)
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

def ue_spawn_actor_from_object(asset_path: str, location: list) -> str:
    """
    Spawns an actor from the specified asset path at the given location.

    :param asset_path: Path to the asset in the Content Browser
    :param location: [x, y, z] coordinates for the actor spawn position
    :return: JSON string indicating success or failure and actor label if spawned
    """
    asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
    if not asset_data:
        return json.dumps({"success": False, "message": f"Asset not found: {asset_path}"})

    if len(location) != 3:
        return json.dumps({"success": False, "message": "Invalid location format. Expected list of 3 floats."})

    try:
        vec = unreal.Vector(float(location[0]), float(location[1]), float(location[2]))
        actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(
            asset_data.get_asset(), vec
        )
        if actor:
            return json.dumps({"success": True, "actor_label": actor.get_actor_label()})
        else:
            return json.dumps({"success": False, "message": "Failed to spawn actor."})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error during spawn: {e}"})

# Additional Unreal-related action functions can be added below.
