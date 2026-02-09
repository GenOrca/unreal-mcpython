# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Asset Tools

from typing import Annotated, Optional, List
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action, ToolInputError

ASSET_ACTIONS_MODULE = "UnrealMCPython.asset_actions"

asset_mcp = FastMCP(name="AssetMCP", description="Tools for managing and querying Unreal Engine assets.")

@asset_mcp.tool(
    name="find",
    description="Finds Unreal Engine assets by name and/or type within the project's /Game directory. At least one of name or asset_type must be provided.",
    tags={"unreal", "asset", "search", "content-browser"}
)
async def find_by_query(
    name: Annotated[Optional[str], Field(description="Substring to match in asset names. Case-insensitive.", min_length=1)] = None,
    asset_type: Annotated[Optional[str], Field(description="Unreal class name of the asset type to filter by (e.g., 'StaticMesh', 'Blueprint').", min_length=1)] = None
) -> dict:
    """Finds Unreal Engine assets by name and/or type."""
    if name is None and asset_type is None:
        raise ToolInputError("At least one of 'name' or 'asset_type' must be provided.")

    params = {"name": name, "asset_type": asset_type}
    return await send_unreal_action(ASSET_ACTIONS_MODULE, params)

@asset_mcp.tool(
    name="get_static_mesh_details",
    description="Retrieves details for a static mesh asset, including its bounding box and dimensions.",
    tags={"unreal", "asset", "staticmesh", "details", "geometry"}
)
async def get_static_mesh_details(
    asset_path: Annotated[str, Field(description="Path to the static mesh asset (e.g., '/Game/Meshes/MyCube.MyCube').", min_length=1)]
) -> dict:
    """Retrieves details for a static mesh asset."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(ASSET_ACTIONS_MODULE, params)
