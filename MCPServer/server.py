from fastmcp import FastMCP
import socket
import json

mcp = FastMCP("Unreal MCP Server")

@mcp.tool()
def run_unreal_print(message: str) -> dict:
    """
    언리얼 에디터에서 print(message)를 실행합니다.
    """
    command = {
        "type": "python",
        "code": f"print('{message}')"
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
        with socket.create_connection((HOST, PORT), timeout=300) as sock:
            sock.sendall(message)
            response = sock.recv(4096)
            return json.loads(response.decode('utf-8'))
    except Exception as e:
        return {"success": False, "message": f"연결/실행 오류: {e}"}

if __name__ == "__main__":
    mcp.run() 