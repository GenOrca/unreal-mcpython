# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Actor Tools

from typing import Annotated, Optional, List
from pydantic import Field
from fastmcp import FastMCP

from unreal_mcp.core import send_unreal_action, ToolInputError

ACTOR_ACTIONS_MODULE = "UnrealMCPython.actor_actions"

actor_mcp = FastMCP(name="ActorMCP", description="Tools for manipulating and querying actors in the Unreal Engine scene.")

@actor_mcp.tool(
    name="spawn_from_object",
    description="Spawns an actor in the Unreal Engine scene from a specified asset path at a given location.",
    tags={"unreal", "actor", "spawn", "level-editing"}
)
async def spawn_from_object(
    asset_path: Annotated[str, Field(description="Path to the asset in the Content Browser (e.g., '/Game/Meshes/MyMesh.MyMesh').")],
    location: Annotated[List[float], Field(description="List of 3 floats representing the [X, Y, Z] coordinates for the actor's spawn position.")]
) -> dict:
    """Spawns an actor from an asset path."""
    params = {"asset_path": asset_path, "location": location}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="duplicate_selected",
    description="Duplicates all currently selected actors in the Unreal Engine editor and applies a specified offset to each new duplicate.",
    tags={"unreal", "actor", "duplicate", "selection", "level-editing"}
)
async def duplicate_selected(
    offset: Annotated[List[float], Field(description="List of 3 floats representing the [X, Y, Z] offset to apply to each duplicated actor.")]
) -> dict:
    """Duplicates selected actors with an offset."""
    params = {"offset": offset}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="select_all",
    description="Selects all actors in the current Unreal Engine level.",
    tags={"unreal", "actor", "selection", "level-editing"}
)
async def select_all() -> dict:
    """Selects all actors in the level."""
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, {})

@actor_mcp.tool(
    name="invert_selection",
    description="Inverts the current actor selection in the Unreal Engine level. Selected actors become deselected, and deselected actors become selected.",
    tags={"unreal", "actor", "selection", "level-editing"}
)
async def invert_selection() -> dict:
    """Inverts the current actor selection."""
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, {})

@actor_mcp.tool(
    name="delete_by_label",
    description="Deletes an actor with the specified label from the current Unreal Engine level.",
    tags={"unreal", "actor", "delete", "level-editing"}
)
async def delete_by_label(
    actor_label: Annotated[str, Field(description="The label of the actor to delete (as seen in the World Outliner).")]
) -> dict:
    """Deletes an actor by its label."""
    params = {"actor_label": actor_label}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="list_all_with_locations",
    description="Lists all actors in the current Unreal Engine level along with their world locations.",
    tags={"unreal", "actor", "list", "query", "location"}
)
async def list_all_with_locations() -> dict:
    """Lists all actors and their locations."""
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, {})

@actor_mcp.tool(
    name="spawn_from_class",
    description="Spawns an actor in the Unreal Engine scene from a specified class path (e.g., Blueprint or C++ class) at a given location and rotation.",
    tags={"unreal", "actor", "spawn", "class", "blueprint", "level-editing"}
)
async def spawn_from_class(
    class_path: Annotated[str, Field(description="Path to the actor class (e.g., '/Game/Blueprints/MyActorBP.MyActorBP_C', '/Script/Engine.StaticMeshActor').")],
    location: Annotated[List[float], Field(description="List of 3 floats for the [X, Y, Z] spawn position.")],
    rotation: Annotated[List[float], Field(description="Optional list of 3 floats for [Pitch, Yaw, Roll] spawn rotation. Defaults to [0,0,0].")]
) -> dict:
    """Spawns an actor from a class path with optional rotation."""
    params = {"class_path": class_path, "location": location, "rotation": rotation}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="get_all_details",
    description="Retrieves detailed information for all actors in the current Unreal Engine level, including label, class, transform, and bounds.",
    tags={"unreal", "actor", "list", "query", "details"}
)
async def get_all_details() -> dict:
    """Gets detailed information for all actors."""
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, {})

@actor_mcp.tool(
    name="set_transform",
    description="Sets the transform (location, rotation, and/or scale) of a specified actor in the Unreal Engine scene.",
    tags={"unreal", "actor", "transform", "location", "rotation", "scale", "level-editing"}
)
async def set_transform(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.")],
    location: Annotated[List[float], Field(description="Optional new location [X, Y, Z].")] = None,
    rotation: Annotated[List[float], Field(description="Optional new rotation [Pitch, Yaw, Roll].")] = None,
    scale: Annotated[List[float], Field(description="Optional new scale [X, Y, Z].")] = None
) -> dict:
    """Sets the transform of an actor. At least one transform component must be provided."""
    if location is None and rotation is None and scale is None:
        raise ToolInputError("At least one of location, rotation, or scale must be provided.")

    params = {"actor_label": actor_label, "location": location, "rotation": rotation, "scale": scale}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="set_location",
    description="Sets the location of a specified actor in the Unreal Engine scene.",
    tags={"unreal", "actor", "location", "transform", "level-editing"}
)
async def set_location(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.")],
    location: Annotated[List[float], Field(description="New location [X, Y, Z].")]
) -> dict:
    """Sets the location of an actor."""
    params = {"actor_label": actor_label, "location": location}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="set_rotation",
    description="Sets the rotation of a specified actor in the Unreal Engine scene.",
    tags={"unreal", "actor", "rotation", "transform", "level-editing"}
)
async def set_rotation(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.")],
    rotation: Annotated[List[float], Field(description="New rotation [Pitch, Yaw, Roll].")]
) -> dict:
    """Sets the rotation of an actor."""
    params = {"actor_label": actor_label, "rotation": rotation}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="set_scale",
    description="Sets the scale of a specified actor in the Unreal Engine scene.",
    tags={"unreal", "actor", "scale", "transform", "level-editing"}
)
async def set_scale(
    actor_label: Annotated[str, Field(description="The label of the actor to modify.")],
    scale: Annotated[List[float], Field(description="New scale [X, Y, Z].")]
) -> dict:
    """Sets the scale of an actor."""
    params = {"actor_label": actor_label, "scale": scale}
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="spawn_on_surface_raycast",
    description="Spawns an actor on a surface detected by a raycast in Unreal. Can spawn from an asset or class path, align to surface normal, apply a location offset, and ignore specified actors.",
    tags={"unreal", "actor", "spawn", "raycast", "surface", "level-editing"}
)
async def spawn_on_surface_raycast(
    asset_or_class_path: Annotated[str, Field(description="Path to the asset (e.g., '/Game/Meshes/MyMesh.MyMesh') or class (e.g., '/Script/Engine.PointLight') to spawn.")],
    ray_start: Annotated[List[float], Field(description="List of 3 floats for ray start location [X, Y, Z].")],
    ray_end: Annotated[List[float], Field(description="List of 3 floats for ray end location [X, Y, Z].")],
    is_class_path: Annotated[bool, Field(description="True if asset_or_class_path is a class path, False if it's an asset path.")] = True,
    desired_rotation: Annotated[List[float], Field(description="Optional list of 3 floats for desired actor rotation [Pitch, Yaw, Roll]. Defaults to [0,0,0].")] = None,
    location_offset: Annotated[List[float], Field(description="Optional list of 3 floats for location offset [X, Y, Z] from the hit point. Defaults to [0,0,0].")] = None,
    trace_channel: Annotated[str, Field(description="Trace channel for raycast (e.g., 'Visibility', 'Camera'). Defaults to 'Visibility'.")] = 'Visibility',
    actors_to_ignore_labels: Annotated[Optional[List[str]], Field(description="Optional list of actor labels to ignore during the raycast.")] = None,
) -> dict:
    """Spawns an actor on a surface via raycast."""
    actual_desired_rotation = desired_rotation if desired_rotation is not None else [0.0, 0.0, 0.0]
    actual_location_offset = location_offset if location_offset is not None else [0.0, 0.0, 0.0]

    params = {
        "asset_or_class_path": asset_or_class_path,
        "ray_start": ray_start,
        "ray_end": ray_end,
        "is_class_path": is_class_path,
        "desired_rotation": actual_desired_rotation,
        "location_offset": actual_location_offset,
        "trace_channel": trace_channel,
        "actors_to_ignore_labels": actors_to_ignore_labels
    }
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, params)

@actor_mcp.tool(
    name="get_in_view_frustum",
    description="Estimates and lists actors potentially visible within the active Unreal Engine editor viewport's frustum. This is an approximation.",
    tags={"unreal", "actor", "query", "visibility", "frustum", "camera"}
)
async def get_in_view_frustum() -> dict:
    """Gets actors estimated to be in the editor view frustum."""
    return await send_unreal_action(ACTOR_ACTIONS_MODULE, {})
