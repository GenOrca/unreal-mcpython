# Copyright (c) 2025 GenOrca. All Rights Reserved.

# MCP Router for Utility Tools

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from unreal_mcp.core import send_unreal_action, send_livecoding_compile, send_python_exec, ToolInputError

util_mcp = FastMCP(name="UtilityMCP", description="Utility tools for Unreal Engine logging and diagnostics.")

UTIL_ACTIONS_MODULE = "UnrealMCPython.util_actions"

@util_mcp.tool(
    name="get_output_log",
    description="Retrieves recent lines from the Unreal Engine output log. Supports filtering by keyword to find specific errors or warnings.",
    tags={"unreal", "log", "debug", "diagnostics"}
)
async def get_output_log(
    line_count: Annotated[int, Field(description="Number of recent log lines to retrieve.", ge=1, le=500)] = 50,
    keyword: Annotated[Optional[str], Field(description="Filter log lines containing this keyword (case-insensitive). e.g. 'Error', 'Warning', 'LogBlueprintUserMessages'.")] = None
) -> dict:
    """Retrieves recent lines from the Unreal Engine output log."""
    params = {"line_count": line_count}
    if keyword is not None:
        params["keyword"] = keyword
    return await send_unreal_action(UTIL_ACTIONS_MODULE, params)

@util_mcp.tool(
    name="execute_python",
    description=(
        "Executes arbitrary Python code in the Unreal Engine editor's Python environment. "
        "The code runs on the game thread with full access to the 'unreal' module. "
        "Use print() to return results — if the output is valid JSON (starts with { or [), "
        "it will be parsed as structured data in the 'result' field. Otherwise raw text is returned. "
        "Useful for one-off operations, prototyping, or accessing UE APIs not covered by other tools. "
        "Example: print(json.dumps({'world': unreal.EditorLevelLibrary.get_editor_world().get_name()}))"
    ),
    tags={"unreal", "python", "execute", "utility", "scripting"}
)
async def execute_python(
    code: Annotated[str, Field(
        description="Python code to execute in UE editor. Use print() to return output. "
                    "The 'unreal' module is available. For structured results, use print(json.dumps(...))."
    )]
) -> dict:
    """Executes arbitrary Python code in the Unreal Engine editor."""
    if not code or not code.strip():
        raise ToolInputError("The 'code' parameter must not be empty.")
    try:
        return await send_python_exec(code)
    except Exception as e:
        return {"success": False, "message": str(e)}

@util_mcp.tool(
    name="livecoding_compile",
    description="Triggers a LiveCoding (C++ hot-reload) compile in Unreal Engine. "
                "This recompiles changed C++ code and patches it into the running editor "
                "without requiring a restart. The tool waits for compilation to complete "
                "and returns the result. May take up to 2 minutes depending on the scope of changes. "
                "If compilation fails, use Build.bat or msbuild-mcp-server to check detailed error messages.",
    tags={"unreal", "livecoding", "compile", "hotreload", "cpp"}
)
async def livecoding_compile() -> dict:
    """Triggers LiveCoding C++ hot-reload compilation in the running Unreal Editor."""
    try:
        return await send_livecoding_compile()
    except Exception as e:
        return {"success": False, "message": str(e)}
