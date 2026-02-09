# Copyright (c) 2025 GenOrca. All Rights Reserved.

import socket
import json
import sys

# Custom Exception classes
class ToolInputError(Exception):
    pass

class UnrealExecutionError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details if details is not None else {}


async def send_unreal_action(action_module: str, params: dict) -> dict:
    """
    Convention-based wrapper for send_to_unreal.
    Auto-derives action_name from the calling function's name.
    Convention: caller 'foo_bar' → action 'ue_foo_bar'
    Also includes standard error handling.
    """
    caller_name = sys._getframe(1).f_code.co_name
    action_name = f"ue_{caller_name}"
    try:
        return await send_to_unreal(action_module, action_name, params)
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

# Core send_to_unreal function
async def send_to_unreal(action_module: str, action_name: str, params: dict) -> dict:
    """
    Sends a command to the Unreal Engine Python script via socket communication.
    Args:
        action_module (str): The Python module in Unreal (e.g., 'actor_actions').
        action_name (str): The function name in the module (e.g., 'ue_spawn_actor_from_class').
        params (dict): A dictionary of parameters for the action.
    Returns:
        dict: The JSON response from Unreal.
    Raises:
        UnrealExecutionError: If any error occurs during socket communication or JSON processing.
        ToolInputError: If there's an issue with the input that can be determined client-side (though less common here).
    """
    HOST = '127.0.0.1'
    PORT = 12029
    command = {
        "type": "python_call",
        "module": action_module,
        "function": action_name,
        "args": params
    }
    response_str = ""
    try:
        json_str = json.dumps(command, ensure_ascii=False)
        message_bytes = json_str.encode('utf-8')

        # Using asyncio for socket communication would be better for a fully async server,
        # but standard socket is used here as per existing structure.
        # If FastMCP's .run() uses an async server like uvicorn, this blocking call
        # will run in a thread pool.
        with socket.create_connection((HOST, PORT), timeout=30) as sock:
            sock.sendall(message_bytes)
            response_buffer = b''
            while True:
                chunk = sock.recv(16384) 
                if not chunk:
                    break
                response_buffer += chunk
            
            if not response_buffer:
                raise UnrealExecutionError("No response received from Unreal.", details={"host": HOST, "port": PORT})

            response_str = response_buffer.decode('utf-8')
            response_json = json.loads(response_str)
            
            # Standardize error propagation from Unreal
            if isinstance(response_json, dict) and response_json.get("success") is False:
                raise UnrealExecutionError(
                    response_json.get("message", "Unknown error from Unreal action."),
                    details=response_json.get("details")
                )
            return response_json

    except socket.timeout:
        raise UnrealExecutionError(f"Socket timeout ({HOST}:{PORT}): No response from Unreal.", details={"host": HOST, "port": PORT})
    except ConnectionRefusedError:
        raise UnrealExecutionError(f"Connection refused ({HOST}:{PORT}). Ensure Unreal MCPython TCP server is active.", details={"host": HOST, "port": PORT})
    except json.JSONDecodeError as je:
        raise UnrealExecutionError(f"Failed to decode JSON response from Unreal: {je}. Raw response: '{response_str}'", details={"host": HOST, "port": PORT, "raw_response": response_str})
    except socket.error as se:
        raise UnrealExecutionError(f"Socket error ({HOST}:{PORT}): {se}", details={"host": HOST, "port": PORT})
    except UnrealExecutionError: # Re-raise if it's already our specific error type
        raise
    except Exception as e: # Catch any other unexpected errors
        raise UnrealExecutionError(f"An unexpected error occurred in send_to_unreal ({HOST}:{PORT}): {type(e).__name__} - {e}", details={"host": HOST, "port": PORT, "error_type": type(e).__name__})
