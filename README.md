# Unreal-MCPython
## AI-Powered Unreal Engine Automation with MCP Integration

**Unreal-MCPython** is a revolutionary **Unreal AI** tool that brings **MCP (Model Context Protocol)** capabilities directly into Unreal Engine. This **Unreal MCP** integration enables AI-assisted game development workflows, allowing developers and technical artists to leverage Claude AI for intelligent automation and smart production pipelines.

[![YouTube Demo](https://img.youtube.com/vi/V7KyjzFlBLk/hqdefault.jpg)](https://youtu.be/V7KyjzFlBLk?si=QaqVqmt6YL59DHg4)

**Keywords**: `unreal-mcp` `unreal-ai` `mcp-unreal` `ai-gamedev` `unreal-automation` `claude-integration`

## 🤖 What is Unreal-MCP Integration?

This project implements a **Model Context Protocol (MCP) server** specifically designed for Unreal Engine, creating the first **Unreal AI** solution that allows Claude to directly interact with your UE projects. Through **Unreal MCP**, you can now have intelligent conversations with AI about your game assets, automate complex workflows, and get context-aware assistance for technical art tasks.

## 🎯 Why Choose Unreal-MCPython?

<p align="center">
<img src="https://raw.githubusercontent.com/GenOrca/Screenshot/refs/heads/main/unreal-mcp/Screenshot%202025-06-02%20025106.png" width="400">
<img src="https://raw.githubusercontent.com/GenOrca/Screenshot/refs/heads/main/unreal-mcp/Screenshot%202025-06-02%20025111.png" width="400">
<img src="https://raw.githubusercontent.com/GenOrca/Screenshot/refs/heads/main/unreal-mcp/Screenshot%202025-06-02%20025115.png" width="400">
<img src="https://raw.githubusercontent.com/GenOrca/Screenshot/refs/heads/main/unreal-mcp/Screenshot%202025-06-02%20025120.png" width="400">
</p>

- 🧠 **Unreal AI integration** - Direct Claude AI assistance in Unreal Engine
- 🔗 **Native MCP protocol support** - Seamless communication between AI and UE
- 🎮 **Intelligent game development** - AI-powered asset management and scene manipulation  
- ⚡ **Smart automation** - Context-aware blueprint scripting with AI guidance
- 🎨 **Technical artist focused** - AI assistance for complex production pipelines


## Key Features

🎮 Actor Manipulation
- Actor placement and scene composition
- Actor duplication and transformation
- Surface placement via raycasting
- Scene analysis (actor listing and details)

🎨 Asset Management
- Asset search and filtering by name/type
- Static mesh details retrieval

🎭 Material System
- Material instance parameter management (scalar, vector, texture, static switch)
- Material recompilation

🔧 Editor Tools
- Asset selection management
- Material replacement on actors
- Mesh replacement on actors
- Blueprint node information retrieval

## 🚀 Installation Guide

### Prerequisites for Unreal-MCP Setup
This **Unreal AI** integration requires the Model Context Protocol setup. Please refer to the [MCP official documentation](https://modelcontextprotocol.io/quickstart/user) for comprehensive details.


### 1. Download Claude for Desktop

Download Claude for Desktop (choose either macOS or Windows).

Note: Linux is not yet supported for Claude for Desktop.


Follow the installation instructions.
If you already have Claude for Desktop, make sure it's on the latest version by clicking on the Claude menu on your computer and selecting "Check for Updates…"

### 2. Install from Fab


### 2. Install Unreal-MCPython Plugin

**Option 1: Install from Fab (Recommended)**

[Fab Link : Unreal-MCPython: AI Assistant Plugin for Unreal Editor using Python & MCP](https://fab.com/s/aed5f75d50b2)

After downloading the Unreal-MCPython plugin on Fab, find the plugin in your Library in the Epic Games Launcher.
Click "Install to Engine" and choose the appropriate version of Unreal Engine (5.6 or higher).


**Option 2: Manual Installation from GitHub**
Alternatively, you can clone the repository directly and place it in your project's plugins folder:
```bash
git clone https://github.com/GenOrca/unreal-mcpython.git
```
Copy the cloned folder to your Unreal Engine project's `Plugins` directory:
```
YourProject/
└── Plugins/
    └── unreal-mcpython/
        ├── Source/
        ├── Content/
        ├── mcp-server/        ← MCP server included
        └── UnrealMCPython.uplugin
```
If the `Plugins` folder doesn't exist in your project, create it manually.
Restart Unreal Engine and enable the plugin from Edit > Plugins menu.

### 3. MCP Server

The MCP server is included in this repository under `mcp-server/`.

Ensure you have Python 3.11+ and [uv](https://docs.astral.sh/uv/) installed.

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
                "C:\\absolute\\path\\to\\unreal-mcpython\\mcp-server",
                "run",
                "src/unreal_mcp/main.py"
            ]
        }
    }
}
```
Replace with the actual absolute path to the `mcp-server` folder inside your plugin directory.

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



# 🔍 Usage Examples
## Basic Unreal AI Commands
```
"Create 10 trees randomly placed on the terrain surface"  
```

### Troubleshooting

- MCP server not starting: Verify that Python 3.11+ and uv are properly installed.
- Path errors: Ensure the absolute path in the configuration file is correct.
- Plugin not visible: Restart Unreal Engine and verify the plugins are enabled.
- Slider icon not visible: Completely restart Claude for Desktop and verify the configuration file was saved correctly.

### References

- [Model Context Protocol Official Documentation](https://modelcontextprotocol.io/quickstart/user)
- [Unreal Python API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/?application_version=5.6)

# 🤝 Contributing to Unreal-MCP
Unreal-MCPython is an open-source project, and we welcome your contributions.

- 🐛 Report bugs and issues
- 💡 Suggest new features and workflows
- 🔧 Submit pull requests for Unreal MCPython enhancements
- 📚 Improve documentation and examples

Transform your Unreal Engine workflow with the power of AI through Unreal-MCPython - where Unreal MCP meets intelligent game development! 🚀🎮🤖
