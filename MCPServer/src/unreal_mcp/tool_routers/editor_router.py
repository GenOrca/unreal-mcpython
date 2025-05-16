from fastmcp import FastMCP
from unreal_mcp.core import send_to_unreal, UnrealExecutionError
from typing import List # Added List

EDITOR_ACTIONS_MODULE = "editor_actions"

editor_mcp = FastMCP(name="EditorMCP", description="Tools for managing and querying Unreal Engine editor functionalities.")

@editor_mcp.tool(
    name="unreal_get_selected_assets",
    description="Gets the set of currently selected assets.",
    tags={"unreal", "editor", "asset", "selection", "assets"}
)
async def get_selected_assets() -> dict:
    """Gets the set of currently selected assets."""
    try:
        params = {}
        return await send_to_unreal(
            action_module="editor_actions",
            action_name="ue_get_selected_assets",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

@editor_mcp.tool(
    name="unreal_replace_materials_on_selected_actors_components",
    description="Replaces a specified material with a new material on all mesh components of the currently selected actors.",
    tags={"unreal", "editor", "actor", "material", "replace", "selected"}
)
async def replace_materials_on_selected_actors_components(
    material_to_be_replaced_path: str, 
    new_material_path: str
) -> dict:
    """Replaces materials on mesh components of selected actors."""
    try:
        params = {
            "material_to_be_replaced_path": material_to_be_replaced_path,
            "new_material_path": new_material_path
        }
        return await send_to_unreal(
            action_module=EDITOR_ACTIONS_MODULE,
            action_name="ue_replace_materials_on_selected_actors_components",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

@editor_mcp.tool(
    name="unreal_replace_materials_on_specified_actors_components",
    description="Replaces a specified material with a new material on all mesh components of actors specified by their paths.",
    tags={"unreal", "editor", "actor", "material", "replace", "specified"}
)
async def replace_materials_on_specified_actors_components(
    actor_paths: List[str], 
    material_to_be_replaced_path: str, 
    new_material_path: str
) -> dict:
    """Replaces materials on mesh components of specified actors."""
    try:
        params = {
            "actor_paths": actor_paths,
            "material_to_be_replaced_path": material_to_be_replaced_path,
            "new_material_path": new_material_path
        }
        return await send_to_unreal(
            action_module=EDITOR_ACTIONS_MODULE,
            action_name="ue_replace_materials_on_specified_actors_components",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

@editor_mcp.tool(
    name="unreal_replace_meshes_on_selected_actors_components",
    description="Replaces a specified static mesh with a new static mesh on all static mesh components of the currently selected actors.",
    tags={"unreal", "editor", "actor", "mesh", "staticmesh", "replace", "selected"}
)
async def replace_meshes_on_selected_actors_components(
    mesh_to_be_replaced_path: str, 
    new_mesh_path: str
) -> dict:
    """Replaces static meshes on components of selected actors."""
    try:
        params = {
            "mesh_to_be_replaced_path": mesh_to_be_replaced_path,
            "new_mesh_path": new_mesh_path
        }
        return await send_to_unreal(
            action_module=EDITOR_ACTIONS_MODULE,
            action_name="ue_replace_meshes_on_selected_actors_components",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

@editor_mcp.tool(
    name="unreal_replace_meshes_on_specified_actors_components",
    description="Replaces a specified static mesh with a new static mesh on all static mesh components of actors specified by their paths.",
    tags={"unreal", "editor", "actor", "mesh", "staticmesh", "replace", "specified"}
)
async def replace_meshes_on_specified_actors_components(
    actor_paths: List[str], 
    mesh_to_be_replaced_path: str, 
    new_mesh_path: str
) -> dict:
    """Replaces static meshes on components of specified actors."""
    try:
        params = {
            "actor_paths": actor_paths,
            "mesh_to_be_replaced_path": mesh_to_be_replaced_path,
            "new_mesh_path": new_mesh_path
        }
        return await send_to_unreal(
            action_module=EDITOR_ACTIONS_MODULE,
            action_name="ue_replace_meshes_on_specified_actors_components",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

@editor_mcp.tool(
    name="unreal_replace_selected_actors_with_blueprint",
    description="Replaces the currently selected actors with new actors spawned from a specified Blueprint asset path.",
    tags={"unreal", "editor", "actor", "blueprint", "replace", "spawn", "selected"}
)
async def replace_selected_actors_with_blueprint(
    blueprint_asset_path: str
) -> dict:
    """Replaces selected actors with instances of a Blueprint."""
    try:
        params = {
            "blueprint_asset_path": blueprint_asset_path
        }
        return await send_to_unreal(
            action_module=EDITOR_ACTIONS_MODULE,
            action_name="ue_replace_selected_actors_with_blueprint",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}
