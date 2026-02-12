# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Behavior Tree Tools

from typing import Annotated, Optional
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action, ToolInputError

BT_ACTIONS_MODULE = "UnrealMCPython.behavior_tree_actions"

behavior_tree_mcp = FastMCP(
    name="BehaviorTreeMCP",
    description="Tools for reading and creating Unreal Engine Behavior Tree and Blackboard assets."
)

# ─── Read Tools ───────────────────────────────────────────────────────────────

@behavior_tree_mcp.tool(
    name="list_behavior_trees",
    description="Lists all Behavior Tree assets in the project's /Game directory. Returns asset paths and associated Blackboard info.",
    tags={"unreal", "ai", "behavior-tree", "list", "asset"}
)
async def list_behavior_trees() -> dict:
    """Lists all Behavior Tree assets in the project."""
    return await send_unreal_action(BT_ACTIONS_MODULE, {})


@behavior_tree_mcp.tool(
    name="get_behavior_tree_structure",
    description="Returns the full tree structure of a Behavior Tree asset as JSON. Includes root node, composites, tasks, decorators, and services in a hierarchical format.",
    tags={"unreal", "ai", "behavior-tree", "structure", "read"}
)
async def get_behavior_tree_structure(
    asset_path: Annotated[str, Field(description="Path to the Behavior Tree asset (e.g., '/Game/AI/BT_Enemy.BT_Enemy').")]
) -> dict:
    """Returns the full tree structure of a Behavior Tree asset."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="get_blackboard_data",
    description="Reads all keys from a Blackboard asset, including key names, types, and instance-synced settings.",
    tags={"unreal", "ai", "blackboard", "read"}
)
async def get_blackboard_data(
    asset_path: Annotated[str, Field(description="Path to the Blackboard asset (e.g., '/Game/AI/BB_Enemy.BB_Enemy').")]
) -> dict:
    """Reads all keys from a Blackboard asset."""
    params = {"asset_path": asset_path}
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="get_bt_node_details",
    description="Retrieves detailed properties of a specific node in a Behavior Tree, identified by node name. Returns class, decorators, services, and editable properties.",
    tags={"unreal", "ai", "behavior-tree", "node", "details"}
)
async def get_bt_node_details(
    asset_path: Annotated[str, Field(description="Path to the Behavior Tree asset.")],
    node_name: Annotated[str, Field(description="Name of the node to inspect (as shown in get_behavior_tree_structure output).")]
) -> dict:
    """Retrieves detailed properties of a specific BT node."""
    params = {"asset_path": asset_path, "node_name": node_name}
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="get_selected_bt_nodes",
    description="Returns details of the currently selected nodes in the open Behavior Tree editor. No parameters needed. Returns node names, classes, types (composite/task/decorator/service), and editable properties.",
    tags={"unreal", "ai", "behavior-tree", "selection", "read"}
)
async def get_selected_bt_nodes() -> dict:
    """Returns details of selected nodes in the BT editor."""
    return await send_unreal_action(BT_ACTIONS_MODULE, {})


# ─── Write Tools ──────────────────────────────────────────────────────────────

@behavior_tree_mcp.tool(
    name="create_behavior_tree",
    description="Creates a new empty Behavior Tree asset. Optionally links it to an existing Blackboard asset.",
    tags={"unreal", "ai", "behavior-tree", "create", "asset"}
)
async def create_behavior_tree(
    asset_path: Annotated[str, Field(description="Path for the new Behavior Tree asset (e.g., '/Game/AI/BT_NewEnemy').")],
    blackboard_path: Annotated[Optional[str], Field(description="Optional path to a Blackboard asset to link.")] = None
) -> dict:
    """Creates a new empty Behavior Tree asset."""
    params = {"asset_path": asset_path}
    if blackboard_path is not None:
        params["blackboard_path"] = blackboard_path
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="create_blackboard",
    description="Creates a new Blackboard Data asset. Optionally sets a parent Blackboard for key inheritance.",
    tags={"unreal", "ai", "blackboard", "create", "asset"}
)
async def create_blackboard(
    asset_path: Annotated[str, Field(description="Path for the new Blackboard asset (e.g., '/Game/AI/BB_NewEnemy').")],
    parent_path: Annotated[Optional[str], Field(description="Optional path to a parent Blackboard asset for key inheritance.")] = None
) -> dict:
    """Creates a new Blackboard Data asset."""
    params = {"asset_path": asset_path}
    if parent_path is not None:
        params["parent_path"] = parent_path
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="add_blackboard_key",
    description="Adds a new key to a Blackboard asset. Supported key types: Bool, Int, Float, String, Name, Vector, Rotator, Object, Class, Enum.",
    tags={"unreal", "ai", "blackboard", "key", "write"}
)
async def add_blackboard_key(
    asset_path: Annotated[str, Field(description="Path to the Blackboard asset.")],
    key_name: Annotated[str, Field(description="Name of the new key to add.")],
    key_type: Annotated[str, Field(description="Type of the key. One of: Bool, Int, Float, String, Name, Vector, Rotator, Object, Class, Enum.")],
    instance_synced: Annotated[bool, Field(description="Whether the key is instance-synced across Blackboard instances.")] = False
) -> dict:
    """Adds a new key to a Blackboard asset."""
    params = {
        "asset_path": asset_path,
        "key_name": key_name,
        "key_type": key_type,
        "instance_synced": instance_synced
    }
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="remove_blackboard_key",
    description="Removes a key from a Blackboard asset by name.",
    tags={"unreal", "ai", "blackboard", "key", "delete"}
)
async def remove_blackboard_key(
    asset_path: Annotated[str, Field(description="Path to the Blackboard asset.")],
    key_name: Annotated[str, Field(description="Name of the key to remove.")]
) -> dict:
    """Removes a key from a Blackboard asset."""
    params = {"asset_path": asset_path, "key_name": key_name}
    return await send_unreal_action(BT_ACTIONS_MODULE, params)


@behavior_tree_mcp.tool(
    name="set_blackboard_to_behavior_tree",
    description="Links a Blackboard asset to a Behavior Tree. The BT will use this Blackboard for its AI data.",
    tags={"unreal", "ai", "behavior-tree", "blackboard", "link"}
)
async def set_blackboard_to_behavior_tree(
    bt_path: Annotated[str, Field(description="Path to the Behavior Tree asset.")],
    bb_path: Annotated[str, Field(description="Path to the Blackboard asset to link.")]
) -> dict:
    """Links a Blackboard asset to a Behavior Tree."""
    params = {"bt_path": bt_path, "bb_path": bb_path}
    return await send_unreal_action(BT_ACTIONS_MODULE, params)
