from fastmcp import FastMCP
import socket
import json

mcp = FastMCP("Unreal MCP Server")

@mcp.tool()
def run_unreal_print(message: str) -> dict:
    """
    Executes print(message) in the Unreal Editor.
    """
    sanitized_message = message.replace("'", "\\'")  # Escape single quotes
    command = {
        "type": "python",
        "code": (
            f"print('{sanitized_message}');"
            f"{{'message': '{sanitized_message}', 'success': True}}"
        )
    }
    return send_to_unreal(command)

@mcp.tool()
def find_asset_by_name(name: str) -> str:
    """
    Returns the Unreal asset path based on the asset name.
    """
    command = {
        "type": "python",
        "code": (
            "import unreal\n"
            "assets = unreal.EditorAssetLibrary.list_assets('/Game', recursive=True)\n"
            "result = [asset for asset in assets if '" + name.replace("'", "\'") + "' in asset]\n"
            "print(result)\n"
        )
    }
    return send_to_unreal(command)

@mcp.tool()
def spawn_actor_from_object(asset_path: str, location: list[float]) -> dict:
    """
    Spawns an actor in Unreal based on the asset path and location.
    """
    command = {
        "type": "python",
        "code": (
            "import unreal\n"
            f"asset_data = unreal.EditorAssetLibrary.find_asset_data('{asset_path}')\n"
            "result = {}\n"
            "if asset_data:\n"
            f"    actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(asset_data.get_asset(), unreal.Vector({location[0]}, {location[1]}, {location[2]}))\n"
            "    if actor:\n"
            "        result = {'success': True, 'actor_label': actor.get_actor_label()}\n"
            "    else:\n"
            "        result = {'success': False, 'message': 'Failed to spawn actor'}\n"
            "else:\n"
            "    result = {'success': False, 'message': 'Asset not found'}\n"
            "print(result)"
        )
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
        message = json_str.encode('utf-8')
        
        print(f"Sending to Unreal: {json_str}")
        
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            sock.sendall(message)
            response = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            try:
                response_str = response.decode('utf-8')
                print(f"Raw response from Unreal: {response_str}")
                return json.loads(response_str)
            except json.JSONDecodeError as je:
                print(f"JSON decode error: {je}, Raw response: {response_str}")
                return {"success": False, "message": f"JSON decoding error: {je}"}
    except Exception as e:
        print(f"Error communicating with Unreal: {e}")
        return {"success": False, "message": f"Connection/Execution error: {e}"}

if __name__ == "__main__":
    mcp.run()