"""
Defines Python action functions for material editing to be executed within Unreal Engine.
"""
import unreal
import json
import traceback
from typing import Optional

# --- Helper Functions for Material Editing ---

def _get_material_asset(material_path: str):
    """Helper to load a material asset."""
    if not material_path:
        raise ValueError("Material path cannot be empty.")
    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if not material:
        raise FileNotFoundError(f"Material asset not found at path: {material_path}")
    if not isinstance(material, unreal.Material):
        raise TypeError(f"Asset at {material_path} is not a Material, but {type(material).__name__}")
    return material

def _get_material_instance_asset(instance_path: str):
    """Helper to load a material instance constant asset."""
    if not instance_path:
        raise ValueError("Material instance path cannot be empty.")
    instance = unreal.EditorAssetLibrary.load_asset(instance_path)
    if not instance:
        raise FileNotFoundError(f"Material instance asset not found at path: {instance_path}")
    if not isinstance(instance, unreal.MaterialInstanceConstant):
        raise TypeError(f"Asset at {instance_path} is not a MaterialInstanceConstant, but {type(instance).__name__}")
    return instance

def _get_expression_class(class_name: str):
    """Helper to get an Unreal MaterialExpression class by name."""
    try:
        # Common prefix for many material expressions if not found directly
        if not hasattr(unreal, class_name) and not class_name.startswith("MaterialExpression"):
            full_class_name = f"MaterialExpression{class_name}"
        else:
            full_class_name = class_name
        
        expression_class = getattr(unreal, full_class_name)
        if not issubclass(expression_class, unreal.MaterialExpression):
            raise TypeError(f"{full_class_name} is not a MaterialExpression class.")
        return expression_class
    except AttributeError:
        raise ValueError(f"MaterialExpression class like '{class_name}' or '{full_class_name}' not found in 'unreal' module.")

def _find_material_expression_by_name_or_type(material, expression_identifier: str, expression_class_name: str = None):
    """
    Finds a material expression within a material by its description (name) or by its class type.
    If expression_identifier is a name (desc), it's prioritized.
    If expression_identifier is a class name and expression_class_name is not set, it tries to find by type.
    """
    if not material or not isinstance(material, unreal.Material):
        raise ValueError("Invalid material provided.")

    all_expressions = unreal.MaterialEditingLibrary.get_material_expressions(material)
    
    target_class = None
    if expression_class_name:
        try:
            target_class = _get_expression_class(expression_class_name)
        except (ValueError, TypeError):
            pass 

    for expr in all_expressions:
        if hasattr(expr, 'desc') and expr.desc == expression_identifier:
            if target_class and not isinstance(expr, target_class):
                continue 
            return expr

    if target_class:
        for expr in all_expressions:
            if isinstance(expr, target_class):
                if expression_identifier == expression_class_name or expression_identifier == target_class.__name__:
                    return expr 

    if not target_class: 
        try:
            potential_class_as_identifier = _get_expression_class(expression_identifier)
            for expr in all_expressions:
                if isinstance(expr, potential_class_as_identifier):
                    return expr 
        except (ValueError, TypeError):
            pass 

    raise ValueError(f"MaterialExpression identified by '{expression_identifier}' (intended class: {expression_class_name or 'any'}) not found in material '{material.get_name()}'. Ensure 'desc' property is set for unique identification or provide correct class name.")

# --- Material Editing Actions ---

def ue_create_material_expression(material_path: str = None, expression_class_name: str = None, node_pos_x: int = 0, node_pos_y: int = 0) -> str:
    """
    Creates a new material expression node within the supplied material.
    Returns JSON string.
    """
    if material_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'material_path' is missing."})
    if expression_class_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'expression_class_name' is missing."})

    transaction_description = "MCP: Create Material Expression"
    try:
        material = _get_material_asset(material_path)
        expression_class = _get_expression_class(expression_class_name)

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            new_expression = unreal.MaterialEditingLibrary.create_material_expression(
                material, expression_class, node_pos_x, node_pos_y
            )
            if not new_expression:
                return json.dumps({
                    "success": False,
                    "message": f"Failed to create MaterialExpression '{expression_class_name}' in '{material_path}'."
                })
            
            if hasattr(new_expression, 'desc') and not new_expression.desc:
                new_expression.desc = expression_class_name 

            unreal.MaterialEditingLibrary.recompile_material(material)
            unreal.EditorAssetLibrary.save_loaded_asset(material)
            
            return json.dumps({
                "success": True,
                "message": f"Successfully created MaterialExpression '{expression_class_name}' in '{material_path}'.",
                "expression_name": new_expression.get_name(), 
                "expression_desc": new_expression.desc if hasattr(new_expression, 'desc') else "N/A",
                "expression_class": new_expression.__class__.__name__
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error creating material expression: {str(e)}",
            "traceback": traceback.format_exc()
        })

def ue_connect_material_expressions(
    material_path: str = None, 
    from_expression_identifier: str = None, 
    from_output_name: str = None, 
    to_expression_identifier: str = None, 
    to_input_name: str = None,
    from_expression_class_name: str = None,
    to_expression_class_name: str = None
) -> str:
    """
    Creates a connection between two material expressions.
    Returns JSON string.
    """
    if material_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'material_path' is missing."})
    if from_expression_identifier is None:
        return json.dumps({"success": False, "message": "Required parameter 'from_expression_identifier' is missing."})
    if from_output_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'from_output_name' is missing."})
    if to_expression_identifier is None:
        return json.dumps({"success": False, "message": "Required parameter 'to_expression_identifier' is missing."})
    if to_input_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'to_input_name' is missing."})

    transaction_description = "MCP: Connect Material Expressions"
    try:
        material = _get_material_asset(material_path)
        
        from_expression = _find_material_expression_by_name_or_type(material, from_expression_identifier, from_expression_class_name)
        to_expression = _find_material_expression_by_name_or_type(material, to_expression_identifier, to_expression_class_name)

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            success = unreal.MaterialEditingLibrary.connect_material_expressions(
                from_expression, from_output_name, to_expression, to_input_name
            )
            if not success:
                return json.dumps({
                    "success": False,
                    "message": f"Failed to connect '{from_expression_identifier}(Output: {from_output_name})' to '{to_expression_identifier}(Input: {to_input_name})' in '{material_path}'. Check pin names and compatibility."
                })

            unreal.MaterialEditingLibrary.recompile_material(material)
            unreal.EditorAssetLibrary.save_loaded_asset(material)

            return json.dumps({
                "success": True,
                "message": f"Successfully connected '{from_expression_identifier}(Output: {from_output_name})' to '{to_expression_identifier}(Input: {to_input_name})' in '{material_path}'."
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error connecting material expressions: {str(e)}",
            "traceback": traceback.format_exc()
        })

def ue_recompile_material(material_path: str = None) -> str:
    """
    Triggers a recompile of a material or material instance's parent. Saves the asset.
    Returns JSON string.
    """
    if material_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'material_path' is missing."})
    try:
        asset_to_process = unreal.EditorAssetLibrary.load_asset(material_path)
        if not asset_to_process:
            raise FileNotFoundError(f"Asset not found at path: {material_path}")

        target_material_to_recompile = None
        asset_to_save = asset_to_process
        message_detail = ""

        if isinstance(asset_to_process, unreal.Material):
            target_material_to_recompile = asset_to_process
            message_detail = f"material '{material_path}'"
        elif isinstance(asset_to_process, unreal.MaterialInstance):
            parent_material = asset_to_process.parent 
            if parent_material: 
                target_material_to_recompile = parent_material
                message_detail = f"parent of material instance '{material_path}'"
            else: 
                 unreal.EditorAssetLibrary.save_loaded_asset(asset_to_process)
                 return json.dumps({
                    "success": True,
                    "message": f"Material instance '{material_path}' has no parent to recompile. Instance saved."
                 })
        else:
            raise TypeError(f"Asset at {material_path} is not a Material or MaterialInstance, but {type(asset_to_process).__name__}")

        if target_material_to_recompile:
            unreal.MaterialEditingLibrary.recompile_material(target_material_to_recompile)
            unreal.EditorAssetLibrary.save_loaded_asset(asset_to_save) 
        
        return json.dumps({
            "success": True,
            "message": f"Successfully recompiled {message_detail} and saved '{material_path}'."
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error processing {message_detail} '{material_path}' for recompile: {str(e)}",
            "traceback": traceback.format_exc()
        })

def ue_get_material_instance_scalar_parameter_value(instance_path: str = None, parameter_name: str = None) -> str:
    """
    Gets the current scalar (float) parameter value from a Material Instance Constant.
    Returns JSON string.
    """
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)
        
        param_value = instance.get_scalar_parameter_value(ue_parameter_name)

        if param_value is None:
             return json.dumps({
                "success": False, 
                "message": f"Scalar parameter '{parameter_name}' not found in instance '{instance_path}'.",
                "parameter_name": parameter_name,
                "instance_path": instance_path,
                "value": None 
            })
        
        return json.dumps({
            "success": True,
            "parameter_name": parameter_name,
            "value": param_value,
            "instance_path": instance_path
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error getting scalar parameter '{parameter_name}' from '{instance_path}': {str(e)}",
            "traceback": traceback.format_exc()
        })

def ue_set_material_instance_scalar_parameter_value(instance_path: str = None, parameter_name: str = None, value: float = None) -> str:
    """
    Sets the scalar (float) parameter value for a Material Instance Constant.
    Returns JSON string.
    """
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})

    transaction_description = "MCP: Set Material Instance Scalar Parameter"
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            _value_ignored, found = instance.get_scalar_parameter_value(ue_parameter_name)
            if not found:
                raise ValueError(f"Scalar parameter '{parameter_name}' does not exist on material instance '{instance_path}'.")

            instance.set_scalar_parameter_value(ue_parameter_name, float(value))
            unreal.MaterialEditingLibrary.update_material_instance(instance) 
            unreal.EditorAssetLibrary.save_loaded_asset(instance)

            return json.dumps({
                "success": True,
                "message": f"Successfully set scalar parameter '{parameter_name}' to {value} for instance '{instance_path}'.",
                "instance_path": instance_path,
                "parameter_name": parameter_name,
                "new_value": value
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error setting scalar parameter '{parameter_name}' for '{instance_path}': {str(e)}",
            "traceback": traceback.format_exc()
        })

def ue_get_material_instance_vector_parameter_value(instance_path: str = None, parameter_name: str = None) -> str:
    """Gets a vector parameter from a Material Instance. Returns JSON string."""
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)
        param_value, found = instance.get_vector_parameter_value(ue_parameter_name)
        if not found:
            return json.dumps({"success": False, "message": f"Vector parameter '{parameter_name}' not found.", "value": None})
        value_list = [param_value.r, param_value.g, param_value.b, param_value.a]
        return json.dumps({"success": True, "parameter_name": parameter_name, "value": value_list, "instance_path": instance_path})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_set_material_instance_vector_parameter_value(instance_path: str = None, parameter_name: str = None, value: list = None) -> str:
    """Sets a vector parameter on a Material Instance. Expects value as [R,G,B,A]. Returns JSON string."""
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})

    transaction_description = "MCP: Set Material Instance Vector Parameter"
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)
        if not isinstance(value, list) or len(value) != 4:
            raise ValueError("Vector value must be a list of 4 floats [R, G, B, A].")
        
        _v, found = instance.get_vector_parameter_value(ue_parameter_name)
        if not found:
            raise ValueError(f"Vector parameter '{parameter_name}' does not exist on material instance '{instance_path}'.")

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            linear_color_value = unreal.LinearColor(float(value[0]), float(value[1]), float(value[2]), float(value[3]))
            instance.set_vector_parameter_value(ue_parameter_name, linear_color_value)
            unreal.MaterialEditingLibrary.update_material_instance(instance)
            unreal.EditorAssetLibrary.save_loaded_asset(instance)
            return json.dumps({"success": True, "message": f"Vector parameter '{parameter_name}' set.", "new_value": value})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_get_material_instance_texture_parameter_value(instance_path: str = None, parameter_name: str = None) -> str:
    """Gets a texture parameter from a Material Instance. Returns JSON string with texture path."""
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)
        param_value, found = instance.get_texture_parameter_value(ue_parameter_name)
        if not found:
            return json.dumps({"success": False, "message": f"Texture parameter '{parameter_name}' not found.", "value": None})
        texture_path = param_value.get_path_name() if param_value else None
        return json.dumps({"success": True, "parameter_name": parameter_name, "value": texture_path, "instance_path": instance_path})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_set_material_instance_texture_parameter_value(instance_path: str = None, parameter_name: str = None, texture_path: Optional[str] = None) -> str:
    """Sets a texture parameter on a Material Instance. Provide texture asset path. Returns JSON string."""
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    # texture_path can be None to clear the texture, so no check for texture_path is None here.

    transaction_description = "MCP: Set Material Instance Texture Parameter"
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)

        _v, found = instance.get_texture_parameter_value(ue_parameter_name)
        if not found:
            raise ValueError(f"Texture parameter '{parameter_name}' does not exist on material instance '{instance_path}'.")
        
        texture_asset = None
        if texture_path: 
            texture_asset = unreal.EditorAssetLibrary.load_asset(texture_path)
            if not texture_asset:
                raise FileNotFoundError(f"Texture asset not found at path: {texture_path}")
            if not isinstance(texture_asset, unreal.Texture):
                raise TypeError(f"Asset at {texture_path} is not a Texture, but {type(texture_asset).__name__}")

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            instance.set_texture_parameter_value(ue_parameter_name, texture_asset)
            unreal.MaterialEditingLibrary.update_material_instance(instance)
            unreal.EditorAssetLibrary.save_loaded_asset(instance)
            return json.dumps({"success": True, "message": f"Texture parameter '{parameter_name}' set.", "new_value": texture_path})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})

def ue_get_material_instance_static_switch_parameter_value(instance_path: str = None, parameter_name: str = None) -> str:
    """Gets a static switch parameter from a Material Instance. Returns JSON string."""
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)
        param_value, found = unreal.MaterialEditingLibrary.get_material_instance_static_switch_parameter_value(instance, ue_parameter_name)
        if not found:
            return json.dumps({"success": False, "message": f"Static switch parameter '{parameter_name}' not found.", "value": None})
        return json.dumps({"success": True, "parameter_name": parameter_name, "value": param_value, "instance_path": instance_path})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error getting static switch parameter '{parameter_name}': {str(e)}", "traceback": traceback.format_exc()})

def ue_set_material_instance_static_switch_parameter_value(instance_path: str = None, parameter_name: str = None, value: bool = None) -> str:
    """Sets a static switch parameter on a Material Instance. Returns JSON string."""
    if instance_path is None:
        return json.dumps({"success": False, "message": "Required parameter 'instance_path' is missing."})
    if parameter_name is None:
        return json.dumps({"success": False, "message": "Required parameter 'parameter_name' is missing."})
    if value is None:
        return json.dumps({"success": False, "message": "Required parameter 'value' is missing."})

    transaction_description = "MCP: Set Material Instance Static Switch Parameter"
    try:
        instance = _get_material_instance_asset(instance_path)
        ue_parameter_name = unreal.Name(parameter_name)
        
        static_params_editor = instance.get_editor_property('static_parameters')
        found_param_info = None
        if static_params_editor:
            for switch_param_group in static_params_editor.static_switch_parameters:
                if switch_param_group.parameter_info.name == ue_parameter_name:
                    found_param_info = switch_param_group
                    break
        
        if not found_param_info:
            with unreal.ScopedEditorTransaction(transaction_description) as trans:
                success = unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(instance, ue_parameter_name, bool(value), unreal.Guid()) # Using a default/empty Guid
                if not success:
                    raise ValueError(f"Failed to set static switch '{parameter_name}' using MaterialEditingLibrary. Parameter might not exist or GUID issue.")
                unreal.MaterialEditingLibrary.update_material_instance(instance)
                unreal.EditorAssetLibrary.save_loaded_asset(instance)
                return json.dumps({"success": True, "message": f"Static switch '{parameter_name}' set to {value} via lib.", "new_value": value})

        with unreal.ScopedEditorTransaction(transaction_description) as trans:
            found_param_info.value = bool(value)
            found_param_info.override = True
            instance.update_static_permutation(static_params_editor)
            unreal.MaterialEditingLibrary.update_material_instance(instance) 
            unreal.EditorAssetLibrary.save_loaded_asset(instance)
            return json.dumps({"success": True, "message": f"Static switch parameter '{parameter_name}' set to {value} via prop. Instance updated and saved.", "new_value": value})
            
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error setting static switch parameter '{parameter_name}': {str(e)}", "traceback": traceback.format_exc()})
