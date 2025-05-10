import asyncio
from fastmcp import Client

async def main():
    # Connect to the server
    async with Client("MCPServer/server.py") as client:
        # Test run_unreal_print
        response = await client.call_tool("run_unreal_print", {"message": 'Hello from test client'})
        print("run_unreal_print Response:", response)

        # Test find_asset_by_name
        response = await client.call_tool("find_asset_by_name", {"name": "NS_WallPortal"})
        print("find_asset_by_name Response:", response)

        # Test run_unreal_print
        response = await client.call_tool("run_unreal_print", {"message": "Hello from test client!"})
        print("run_unreal_print Response:", response)

if __name__ == "__main__":
    asyncio.run(main())
