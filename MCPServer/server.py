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