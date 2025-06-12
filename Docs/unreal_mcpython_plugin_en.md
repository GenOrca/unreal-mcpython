# Unreal MCPython Plugin Technical Documentation

## Overview
Unreal MCPython is a plugin based on the Model Context Protocol (MCP) that enables automation of Unreal Engine editor tasks by integrating with external AI services (such as Claude). It allows control of various editor functionalities through Python scripting.

## System Architecture

### Overall Structure
- **MCP Server**: A FastAPI-based Python server that acts as a relay between external LLMs (such as Claude) and the Unreal Editor. The LLM sends API calls to the MCP server, which issues automation commands to the Unreal Editor.
- **Python API Wrapper**: Operates within Unreal’s Python plugin environment. It wraps Unreal's native functionalities and C++ UFUNCTIONs into Python-accessible functions, executing commands received from the MCP server.
- **C++ Helper Module**: Implements complex or performance-critical editor tasks natively (e.g., blueprint node querying, pin connections), exposing them as UFUNCTIONs callable from Python.

### Data Flow
1. **User / LLM (e.g., Claude)**: Sends requests to the MCP server via natural language or API calls.
2. **MCP Server**: Parses requests and delegates them to appropriate Python action functions.
3. **Python API Wrapper**: Executes the requested commands within Unreal Editor, calling C++ UFUNCTIONs if needed.
4. **C++ Helper Module**: Handles complex editor or blueprint operations and returns results to Python.
5. **Response**: Results propagate back through the chain to the LLM/user.

### Structural Notes and Considerations
- Claude (LLM) is a client of the MCP server and does not communicate with the Unreal Editor directly.
- The Python API Wrapper only works within the Unreal Python plugin environment.
- All C++ helper functions must be exposed as UFUNCTIONs to be callable from Python.
- Advanced features like blueprint automation are implemented through Python and C++ collaboration.

## Installation Guide

Before You Begin
This guide is based on the Model Context Protocol official documentation. Please refer to the official documentation for detailed information about MCP.

### 1. Download Claude for Desktop

Download Claude for Desktop (choose either macOS or Windows).

Note: Linux is not yet supported for Claude for Desktop.


Follow the installation instructions.
If you already have Claude for Desktop, make sure it's on the latest version by clicking on the Claude menu on your computer and selecting "Check for Updates…"

### 2. Install from Fab

After downloading the Unreal-MCPython plugin on Fab, find the plugin in your Library in the Epic Games Launcher.
Click "Install to Engine" and choose the appropriate version of Unreal Engine (5.6 or higher).

### 3. Install unreal-mcp-server

Clone the repository:
```bash
git clone https://github.com/genorca/unreal-mcp-server.git
cd unreal-mcp-server
```
Ensure you have Python 3.11+ and uv installed.

### 4. Configure Claude for Desktop

1. Open the Claude menu on your computer and select "Settings…"
    - Note: These are not the Claude Account Settings found in the app window itself.

2. Click on "Developer" in the left-hand bar of the Settings pane, and then click on "Edit Config".
3. This will create a configuration file at:
    - Windows: %APPDATA%\Claude\claude_desktop_config.json

4. Open the configuration file in any text editor and replace the file contents with:

```json
{
    "mcpServers": {
        "unreal-mcpython": {
            "command": "uv",
            "args": [
                "--directory",
                "C:\\absolute\\path\\to\\unreal-mcp-server",
                "run",
                "src/unreal_mcp/main.py"
            ]
        }
    }
}
```
Replace with the actual absolute path to your unreal-mcp-server folder.

### 5. Configure Unreal Engine

1. Create a new Unreal Engine project or load an existing project.
2. From the "Edit" menu, select "Plugins".
3. Enable these plugins: Unreal-MCPython and Python Editor Script Plugin.
4. Restart Unreal Engine.

### 6. Connect with Claude

1. Restart Claude for Desktop.
2. The MCP server will start automatically in the background.
3. Upon restarting, you should see a slider icon in the bottom left corner of the input box.
4. Click the slider icon to view and connect to available Unreal Engine tools.
5. Select the "unreal-mcpython" server to connect.
6. You can now ask Claude to perform automation tasks in your project using the UE Python API.

### Troubleshooting

- MCP server not starting: Verify that Python 3.11+ and uv are properly installed.
- Path errors: Ensure the absolute path in the configuration file is correct.
- Plugin not visible: Restart Unreal Engine and verify the plugins are enabled.
- Slider icon not visible: Completely restart Claude for Desktop and verify the configuration file was saved correctly.

### References

[Model Context Protocol Official Documentation](https://modelcontextprotocol.io/quickstart/user)

## Key Feature Categories

### 1. Asset Management Tools

#### Asset Search (`asset_unreal_find_asset`)
Search assets in the project by name or type.

**Parameters:**
- `name` (optional): Partial asset name (case-insensitive)
- `asset_type` (optional): Unreal class name (e.g., 'StaticMesh', 'Blueprint')

**Example:**
```python
# Search for assets containing 'cube'
find_asset(name="cube")

# Search for all static meshes
find_asset(asset_type="StaticMesh")
```

#### Static Mesh Details (`asset_unreal_get_static_mesh_details`)
Retrieve bounding box and size info for static meshes.

**Returns:**
- Bounding box min/max coordinates
- Actual size (X, Y, Z)

### 2. Actor Management Tools

#### Actor Spawning and Placement

- **Basic Spawn (`actor_unreal_spawn_actor_from_object`):**
```python
# Spawn a cube at a specific location
spawn_actor_from_object(
    asset_path="/Engine/BasicShapes/Cube.Cube",
    location=[100.0, 200.0, 50.0]
)
```

- **Surface-Based Spawn (`actor_unreal_spawn_actor_on_surface_raycast`):**
Spawns an actor on a surface using raycasting.
```python
# Raycast downward to place actor on ground
spawn_actor_on_surface_raycast(
    asset_or_class_path="/Script/Engine.PointLight",
    ray_start=[0.0, 0.0, 1000.0],
    ray_end=[0.0, 0.0, -1000.0],
    location_offset=[0.0, 0.0, 10.0]
)
```

#### Actor Manipulation

- Set location: `actor_unreal_set_actor_location`
- Set rotation: `actor_unreal_set_actor_rotation`
- Set scale: `actor_unreal_set_actor_scale`
- Set full transform: `actor_unreal_set_actor_transform`
- Duplicate: `actor_unreal_duplicate_selected_actors`
```python
# Duplicate selected actors with an X offset of 500
duplicate_selected_actors(offset=[500.0, 0.0, 0.0])
```

#### Actor Query

- List all actors: `actor_unreal_list_all_actors_with_locations`
- Get actor details: `actor_unreal_get_all_actors_details`

**Returned Information:**
- Label (display name in scene)
- Class path
- Location and rotation
- World bounding box
- Asset path (for static meshes)

#### Selection Management

- Select all: `actor_unreal_select_all_actors`
- Invert selection: `actor_unreal_invert_actor_selection`
- Actors in view: `actor_unreal_get_actors_in_view_frustum`

### 3. Editor Integration Tools

#### Asset Replacement

- **Material Replacement:**
  - Selected actors: `editor_unreal_replace_materials_on_selected_actors_components`
  - Specific actors: `editor_unreal_replace_materials_on_specified_actors_components`

- **Mesh Replacement:**
  - Selected actors: `editor_unreal_replace_meshes_on_selected_actors_components`
  - Specific actors: `editor_unreal_replace_meshes_on_specified_actors_components`

- **Blueprint Replacement:** `editor_unreal_replace_selected_actors_with_blueprint`

#### Selected Asset Query

- `editor_unreal_get_selected_assets`: Returns info about assets currently selected in the Content Browser.

### 4. Material System

#### Material Expression Creation

- `material_create_material_expression`: Adds a new node in the material editor.

**Supported Expression Types:**
- `MaterialExpressionTextureSample`
- `MaterialExpressionScalarParameter`
- `MaterialExpressionVectorParameter`
- And any other material expression class

#### Node Connection

- `material_connect_material_expressions`: Connects pins between material nodes.

#### Material Instance Parameter Control

- **Scalar Parameter:**
  - Get: `material_get_material_instance_scalar_parameter`
  - Set: `material_set_material_instance_scalar_parameter`

- **Vector Parameter:**
  - Get: `material_get_material_instance_vector_parameter`
  - Set: `material_set_material_instance_vector_parameter`

- **Texture Parameter:**
  - Get: `material_get_material_instance_texture_parameter`
  - Set: `material_set_material_instance_texture_parameter`

- **Static Switch:**
  - Get: `material_get_material_instance_static_switch_parameter`
  - Set: `material_set_material_instance_static_switch_parameter`

#### Material Compilation

- `material_recompile_material`: Recompiles a material or material instance.

### 5. Blueprint

#### Node Information Query

- Selected nodes: `editor_unreal_get_selected_blueprint_nodes`
- Node details: `editor_unreal_get_selected_blueprint_node_infos`

## Claude Integration Setup

### 1. Environment Setup

**Required Software:**
- Unreal Engine 5.4+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/guides/install-python/)
- Claude Desktop App

### 2. MCP Server Configuration

Add the following to your Claude config file (`claude_desktop_config.json`):
```json
{
    "mcpServers": {
        "unreal-mcpython": {
            "command": "uv",
            "args": [
                "--directory",
                "($Project_Path)/Plugins/UnrealMCPython/MCPServer",
                "run",
                "src/unreal_mcp/main.py"
            ]
        }
    }
}
```

### 3. Usage Example

Control the Unreal Editor through natural language with Claude:
- “Move all cubes in the current scene 100 units along the Y-axis.”
- “Create a new point light at position (500, 500, 200).”
- “Replace the materials of selected actors with the default material.”

## Coordinate System and Units

**Unreal Coordinate System:**
- X-axis: Forward/Backward
- Y-axis: Right/Left
- Z-axis: Up/Down
- Unit: cm (centimeters)

**Rotations:**
- Pitch: Rotation around Y (look up/down)
- Yaw: Rotation around Z (turn left/right)
- Roll: Rotation around X (tilt)
- Unit: degrees

## Troubleshooting

### Connection Failure:
- Ensure Unreal Editor is running
- Verify Python plugin is enabled
- Check for MCP server port conflicts

### Functional Errors:
- Confirm asset path is correct
- Ensure actor labels exist
- Check for error messages in the Python console

With this plugin, complex Unreal Editor tasks can be conveniently automated using natural language conversations with Claude.