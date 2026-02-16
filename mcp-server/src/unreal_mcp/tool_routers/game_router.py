# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Game Settings Tools

from typing import Annotated, Optional
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action, ToolInputError

GAME_ACTIONS_MODULE = "UnrealMCPython.game_actions"

game_mcp = FastMCP(
    name="GameMCP",
    description="Tools for configuring game settings such as GameMode, input actions, and input mappings."
)

@game_mcp.tool(
    name="set_game_mode",
    description=(
        "Sets the GameMode Override for the current level via World Settings. "
        "Accepts a Blueprint class path (e.g., '/Game/Blueprints/BP_MyGameMode.BP_MyGameMode_C') "
        "or a C++ class path (e.g., '/Script/Engine.GameModeBase'). "
        "Pass an empty string or null to clear the override."
    ),
    tags={"unreal", "game", "gamemode", "settings", "level"}
)
async def set_game_mode(
    game_mode_class_path: Annotated[Optional[str], Field(
        description="Full class path to the GameMode Blueprint or C++ class. "
                    "Use '/Game/..._C' suffix for Blueprints. "
                    "Pass empty string or null to clear the GameMode Override."
    )] = None
) -> dict:
    """Sets the GameMode Override for the current level."""
    params = {"game_mode_class_path": game_mode_class_path}
    return await send_unreal_action(GAME_ACTIONS_MODULE, params)


@game_mcp.tool(
    name="add_input_action",
    description=(
        "Creates a new Enhanced Input Action asset. "
        "The value_type determines what kind of input data the action produces: "
        "'Bool' (button press), 'Axis1D' (single float), 'Axis2D' (2D vector, e.g. mouse), 'Axis3D' (3D vector)."
    ),
    tags={"unreal", "game", "input", "action", "enhanced-input", "create", "asset"}
)
async def add_input_action(
    asset_path: Annotated[str, Field(
        description="Path for the new InputAction asset (e.g., '/Game/Input/IA_Jump')."
    )],
    value_type: Annotated[str, Field(
        description="Input value type. One of: 'Bool', 'Axis1D', 'Axis2D', 'Axis3D'. Defaults to 'Bool'."
    )] = "Bool"
) -> dict:
    """Creates a new Enhanced Input Action asset."""
    valid_types = ["Bool", "Axis1D", "Axis2D", "Axis3D"]
    if value_type not in valid_types:
        raise ToolInputError(f"Invalid value_type '{value_type}'. Must be one of: {', '.join(valid_types)}")
    params = {"asset_path": asset_path, "value_type": value_type}
    return await send_unreal_action(GAME_ACTIONS_MODULE, params)


@game_mcp.tool(
    name="add_input_mapping",
    description=(
        "Creates an InputMappingContext asset and/or adds a key-to-action mapping to it. "
        "If the IMC asset does not exist, it will be created. "
        "Then maps a physical key to an InputAction within that context. "
        "The key_name should be a UE key name (e.g., 'SpaceBar', 'W', 'Gamepad_FaceButton_Bottom', 'LeftMouseButton')."
    ),
    tags={"unreal", "game", "input", "mapping", "enhanced-input", "create", "asset"}
)
async def add_input_mapping(
    mapping_context_path: Annotated[str, Field(
        description="Path to the InputMappingContext asset (e.g., '/Game/Input/IMC_Default'). "
                    "Created if it doesn't exist."
    )],
    action_path: Annotated[str, Field(
        description="Path to the InputAction asset to map (e.g., '/Game/Input/IA_Jump')."
    )],
    key_name: Annotated[str, Field(
        description="UE key name to bind (e.g., 'SpaceBar', 'W', 'LeftMouseButton', "
                    "'Gamepad_FaceButton_Bottom')."
    )]
) -> dict:
    """Creates/updates an InputMappingContext with a key-to-action mapping."""
    params = {
        "mapping_context_path": mapping_context_path,
        "action_path": action_path,
        "key_name": key_name
    }
    return await send_unreal_action(GAME_ACTIONS_MODULE, params)
