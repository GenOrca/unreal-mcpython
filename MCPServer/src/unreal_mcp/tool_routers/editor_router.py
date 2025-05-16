from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any, Annotated

from unreal_mcp.core import send_to_unreal, ToolInputError, UnrealExecutionError

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
        params = {}  # 필요한 파라미터가 있다면 여기에 추가
        return await send_to_unreal(
            action_module="editor_actions",
            action_name="ue_get_selected_assets",
            params=params
        )
    except UnrealExecutionError as e:
        return {"success": False, "message": str(e), "details": e.details}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}
