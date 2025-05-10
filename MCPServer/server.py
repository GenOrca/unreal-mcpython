from fastmcp import FastMCP
import socket
import json

mcp = FastMCP("Unreal MCP Server")

@mcp.tool()
def run_unreal_print(message: str) -> dict:
    """
    언리얼 에디터에서 print(message)를 실행합니다.
    """
    sanitized_message = message.replace("'", "\'")  # Escape single quotes
    command = {
        "type": "python",
        "code": f"print('{sanitized_message}')"
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
            f"import unreal; "
            f"assets = unreal.EditorAssetLibrary.list_assets('/Game', recursive=True); "
            f"result = [asset for asset in assets if asset.endswith('{name}')];"
            f"print(result);"
            f"result;"
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
            f"import unreal; "
            f"actor_class = unreal.EditorAssetLibrary.load_blueprint_class('{asset_path}'); "
            f"if actor_class: "
            f"    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, unreal.Vector({location[0]}, {location[1]}, {location[2]})); "
            f"    result = {{'success': True, 'actor_name': actor.get_name()}} "
            f"else: "
            f"    result = {{'success': False, 'message': 'Failed to load actor class'}}"
        )
    }
    return send_to_unreal(command)

def send_to_unreal(command: dict) -> dict:
    """
    UnrealMCPython 소켓 서버(127.0.0.1:9001)로 JSON 명령을 보내고 결과를 반환합니다.
    """
    HOST = '127.0.0.1'
    PORT = 12029
    message = json.dumps(command).encode('utf-8')
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            sock.sendall(message)
            response = sock.recv(4096)
            return json.loads(response.decode('utf-8'))
    except Exception as e:
        return {"success": False, "message": f"연결/실행 오류: {e}"}

if __name__ == "__main__":
    mcp.run()