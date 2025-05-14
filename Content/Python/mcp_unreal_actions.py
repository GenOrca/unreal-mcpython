"""
Core dispatcher for executing dynamic Python commands received from the MCP server.
All specific action functions have been moved to their respective modules:
- util_actions.py
- asset_actions.py
- actor_actions.py
- material_actions.py
"""
import unreal # type: ignore # Suppress linter warning, 'unreal' module is available in UE Python environment
import json
import importlib
import traceback

# Core dispatcher for executing dynamic Python commands received from the MCP server
def execute_action(module_name: str, function_name: str, params: dict) -> str: # Changed args_list: list to params: dict
    """
    Dynamically imports and executes the specified function from the given module.
    It reloads the module on each call to ensure the latest version is used.

    Args:
        module_name (str): Name of the module containing the function (e.g., "util_actions", "actor_actions").
        function_name (str): Name of the function to call (e.g., "ue_print_message").
        params (dict): Dictionary of parameters to pass to the target function.

    Returns:
        str: JSON-formatted string representing the function's result or an error.
    """
    try:
        # Ensure the module name is valid and does not try to escape the intended directory
        # This is a basic check; more robust sandboxing might be needed depending on security requirements.
        if ".." in module_name or "/" in module_name or "\\" in module_name:
            raise ValueError(f"Invalid module name: {module_name}. Contains restricted characters.")

        # Dynamically import the module.
        # Assuming these modules are in the Python path accessible by Unreal.
        # For plugins, this usually means Content/Python or subdirectories.
        target_module = importlib.import_module(module_name)
        
        # Reload the module to pick up any changes without restarting Unreal.
        # This is crucial for development and live updates.
        importlib.reload(target_module)

        target_function = getattr(target_module, function_name)
        
        # Execute the function
        # params is now expected to be a dictionary directly.
        # Unpack the dictionary as keyword arguments to the target function.
        result_json_str = target_function(**params)
        
        # Validate if the result is indeed a JSON string (basic check)
        try:
            json.loads(result_json_str) # Try to parse it to ensure it's valid JSON
        except json.JSONDecodeError as je:
            # If the function didn't return a valid JSON string, wrap this error.
            error_detail = f"Function '{module_name}.{function_name}' did not return a valid JSON string. Error: {je}. Returned: {result_json_str[:200]}"
            return json.dumps({
                "success": False, 
                "message": error_detail,
                "traceback": traceback.format_exc(),
                "type": "InvalidReturnFormat"
            })
        except TypeError as te:
             # If result_json_str is not a string-like object (e.g. None)
            error_detail = f"Function '{module_name}.{function_name}' returned a non-string type. Error: {te}. Returned type: {type(result_json_str).__name__}"
            return json.dumps({
                "success": False, 
                "message": error_detail,
                "traceback": traceback.format_exc(),
                "type": "InvalidReturnType"
            })


        return result_json_str # Return the JSON string as is

    except ImportError:
        return json.dumps({
            "success": False, 
            "message": f"Could not import module '{module_name}'. Ensure it exists and is in Python path.",
            "traceback": traceback.format_exc(),
            "type": "ImportError"
        })
    except AttributeError:
        return json.dumps({
            "success": False, 
            "message": f"Function '{function_name}' not found in module '{module_name}'.",
            "traceback": traceback.format_exc(),
            "type": "AttributeError"
        })
    except ValueError as ve: # Catch specific ValueError from module name check
        return json.dumps({
            "success": False,
            "message": str(ve),
            "traceback": traceback.format_exc(),
            "type": "ValueError"
        })
    except Exception as e:
        # Catch all other exceptions during function execution
        return json.dumps({
            "success": False, 
            "message": f"Exception during execution of '{module_name}.{function_name}': {str(e)}",
            "traceback": traceback.format_exc(), # Include traceback for debugging
            "type": type(e).__name__
        })

# All specific ue_... action functions have been moved to their respective files:
# - util_actions.py
# - asset_actions.py
# - actor_actions.py
# - material_actions.py
