from fastmcp import FastMCP
from unreal_mcp.tool_routers.util_router import util_mcp
from unreal_mcp.tool_routers.asset_router import asset_mcp
from unreal_mcp.tool_routers.actor_router import actor_mcp
from unreal_mcp.tool_routers.material_router import material_mcp

main_mcp = FastMCP(
    name="Unreal MCP Server",
    description="Main MCP server for Unreal Engine integration, providing categorized tools for utility, asset, actor, and material operations.",
    version="1.0.0"
)

# Mount the FastMCP sub-servers
main_mcp.mount("utils", util_mcp)
main_mcp.mount("assets", asset_mcp)
main_mcp.mount("actors", actor_mcp)
main_mcp.mount("materials", material_mcp)

def run_server():
    """Entry point function for the Unreal MCP Server"""
    main_mcp.run(transport="stdio")

if __name__ == "__main__":
    # Explicitly set transport to "stdio" for testing local inter-process communication
    run_server()