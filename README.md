# Unreal-MCPython

## Project Introduction

Unreal-MCPython is a powerful production tool that leverages Python within the Unreal Engine environment. This project is designed to help game developers and technical artists automate complex tasks, optimize production pipelines, and dedicate more time to creative work.

## Key Features

### Asset Management
- Search and filter assets within the project
- Retrieve detailed information about static meshes
- Access asset location and size information

### Actor Manipulation
- Create and place actors in scenes
- Duplicate selected actors
- Adjust actor transformations (location, rotation, scale)
- Place actors on surfaces via raycasting
- Retrieve information about all actors in a scene

### Editor Integration
- View information about selected assets
- Batch replace materials and meshes on selected actors
- Context-aware explanations for Blueprint elements

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

# Contributing
Unreal-MCPython is an open-source project, and we welcome your contributions.

You can help improve the project through bug reports, feature requests, pull requests, and more.