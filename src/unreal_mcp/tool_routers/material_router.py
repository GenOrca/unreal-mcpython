# Copyright (c) 2025 GenOrca. All Rights Reserved.

"""
FastMCP sub-server for Material related tools.
"""
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any, Annotated

from unreal_mcp.core import send_unreal_action, ToolInputError

MATERIAL_ACTIONS_MODULE = "UnrealMCPython.material_actions"

material_mcp = FastMCP(name="MaterialMCP", description="Tools for managing and editing Unreal Engine materials and material instances.")

# --- Tool Endpoints for Materials (Refactored for FastMCP) ---

@material_mcp.tool(
    name="create_expression",
    description="Creates a new expression node within a specified material asset.",
    tags={"unreal", "material", "shader", "graph", "editor"}
)
async def create_expression(
    material_path: Annotated[str, Field(description="Path to the parent material asset (e.g., /Game/Materials/MyBaseMaterial.MyBaseMaterial)")],
    expression_class_name: Annotated[str, Field(description="Class name of the expression to create (e.g., MaterialExpressionTextureSample, MaterialExpressionScalarParameter)")],
    node_pos_x: Annotated[int, Field(description="X position for the new node in the material editor graph.")] = 0,
    node_pos_y: Annotated[int, Field(description="Y position for the new node in the material editor graph.")] = 0
) -> dict:
    params = {
        "material_path": material_path,
        "expression_class_name": expression_class_name,
        "node_pos_x": node_pos_x,
        "node_pos_y": node_pos_y
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="connect_expressions",
    description="Connects two expression nodes within a material asset.",
    tags={"unreal", "material", "shader", "graph", "editor"}
)
async def connect_expressions(
    material_path: Annotated[str, Field(description="Path to the material asset.")],
    from_expression_identifier: Annotated[str, Field(description="Name (desc) or class of the source expression node.")],
    from_output_name: Annotated[str, Field(description="Name of the output pin on the source expression (e.g., \"R\", \"G\", \"B\", \"A\", or empty for default).")],
    to_expression_identifier: Annotated[str, Field(description="Name (desc) or class of the destination expression node.")],
    to_input_name: Annotated[str, Field(description="Name of the input pin on the destination expression (e.g., \"BaseColor\", \"UVs\", or empty for default).")],
    from_expression_class_name: Annotated[Optional[str], Field(description="Optional: Specific class name of the source expression if identifier is ambiguous.")] = None,
    to_expression_class_name: Annotated[Optional[str], Field(description="Optional: Specific class name of the destination expression if identifier is ambiguous.")] = None
) -> dict:
    params = {
        "material_path": material_path,
        "from_expression_identifier": from_expression_identifier,
        "from_output_name": from_output_name,
        "to_expression_identifier": to_expression_identifier,
        "to_input_name": to_input_name,
        "from_expression_class_name": from_expression_class_name,
        "to_expression_class_name": to_expression_class_name
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="recompile",
    description="Recompiles a material or material instance asset.",
    tags={"unreal", "material", "shader", "compile"}
)
async def recompile(
    material_path: Annotated[str, Field(description="Path to the material or material instance asset to recompile (e.g., /Game/Materials/MyMaterial.MyMaterial).")]
) -> dict:
    params = {"material_path": material_path}
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="get_mi_scalar_param",
    description="Gets the value of a scalar parameter from a material instance.",
    tags={"unreal", "material", "instance", "parameter", "scalar", "query"}
)
async def get_mi_scalar_param(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the scalar parameter.")]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="set_mi_scalar_param",
    description="Sets the value of a scalar parameter in a material instance.",
    tags={"unreal", "material", "instance", "parameter", "scalar", "modify"}
)
async def set_mi_scalar_param(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the parameter.")],
    value: Annotated[float, Field(description="The float value to set for the scalar parameter.")]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name,
        "value": value
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="get_mi_vector_param",
    description="Gets the value of a vector parameter from a material instance.",
    tags={"unreal", "material", "instance", "parameter", "vector", "query"}
)
async def get_mi_vector_param(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the vector parameter.")]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="set_mi_vector_param",
    description="Sets the value of a vector parameter in a material instance.",
    tags={"unreal", "material", "instance", "parameter", "vector", "modify"}
)
async def set_mi_vector_param(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the parameter.")],
    value: Annotated[List[float], Field(description="The vector value [R, G, B, A] to set.", min_length=4, max_length=4)]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name,
        "value": value
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="get_mi_texture_param",
    description="Gets the texture asset assigned to a texture parameter in a material instance.",
    tags={"unreal", "material", "instance", "parameter", "texture", "query"}
)
async def get_mi_texture_param(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the texture parameter.")]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="set_mi_texture_param",
    description="Sets or clears a texture asset for a texture parameter in a material instance.",
    tags={"unreal", "material", "instance", "parameter", "texture", "modify"}
)
async def set_mi_texture_param(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the parameter.")],
    texture_path: Annotated[Optional[str], Field(description="Path to the texture asset to set. Set to null or empty string to clear.")] = None
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name,
        "texture_path": texture_path
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="get_mi_static_switch",
    description="Gets the value of a static switch parameter from a material instance.",
    tags={"unreal", "material", "instance", "parameter", "static", "switch", "query"}
)
async def get_mi_static_switch(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the static switch parameter.")]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)

@material_mcp.tool(
    name="set_mi_static_switch",
    description="Sets the value of a static switch parameter in a material instance.",
    tags={"unreal", "material", "instance", "parameter", "static", "switch", "modify"}
)
async def set_mi_static_switch(
    instance_path: Annotated[str, Field(description="Path to the Material Instance Constant asset.")],
    parameter_name: Annotated[str, Field(description="Name of the parameter.")],
    value: Annotated[bool, Field(description="The boolean value to set for the static switch parameter.")]
) -> dict:
    params = {
        "instance_path": instance_path,
        "parameter_name": parameter_name,
        "value": value
    }
    return await send_unreal_action(MATERIAL_ACTIONS_MODULE, params)
