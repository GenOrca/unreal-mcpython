from fastmcp import FastMCP
import socket
import json

mcp = FastMCP("Unreal MCP Server")

@mcp.tool()
def run_unreal_print(message: str) -> dict:
    """
    언리얼 에디터에서 print(message)를 실행합니다.
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
    에셋 이름을 기반으로 Unreal 에셋 경로를 반환합니다.
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
    에셋 경로와 위치를 기반으로 Unreal에서 액터를 스폰합니다.
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
    UnrealMCPython 소켓 서버(127.0.0.1:12029)로 JSON 명령을 보내고 결과를 반환합니다.
    """
    HOST = '127.0.0.1'
    PORT = 12029
    try:
        # JSON 직렬화 - ensure_ascii=False로 비ASCII 문자 그대로 유지
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
                return {"success": False, "message": f"JSON 디코딩 오류: {je}"}
    except Exception as e:
        print(f"Error communicating with Unreal: {e}")
        return {"success": False, "message": f"연결/실행 오류: {e}"}

if __name__ == "__main__":
    mcp.run()