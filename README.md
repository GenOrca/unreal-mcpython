# Unreal-MCPython
## AI-Powered Unreal Engine Automation with MCP Integration

**Unreal-MCPython** is a revolutionary **Unreal AI** tool that brings **MCP (Model Context Protocol)** capabilities directly into Unreal Engine. This **Unreal MCP** integration enables AI-assisted game development workflows, allowing developers and technical artists to leverage Claude AI for intelligent automation and smart production pipelines.

**Keywords**: `unreal-mcp` `unreal-ai` `mcp-unreal` `ai-gamedev` `unreal-automation` `claude-integration`

## 🤖 What is Unreal-MCP Integration?

This project implements a **Model Context Protocol (MCP) server** specifically designed for Unreal Engine, creating the first **Unreal AI** solution that allows Claude to directly interact with your UE projects. Through **Unreal MCP**, you can now have intelligent conversations with AI about your game assets, automate complex workflows, and get context-aware assistance for technical art tasks.

## 🎯 Why Choose Unreal-MCPython?

- 🧠 **Unreal AI integration** - Direct Claude AI assistance in Unreal Engine
- 🔗 **Native MCP protocol support** - Seamless communication between AI and UE
- 🎮 **Intelligent game development** - AI-powered asset management and scene manipulation  
- ⚡ **Smart automation** - Context-aware blueprint scripting with AI guidance
- 🎨 **Technical artist focused** - AI assistance for complex production pipelines



## Key Features

### 🤖 AI-Enhanced Asset Management
- asset search and filtering
- Intelligent asset recommendations and organization
- AI-assisted metadata analysis and tagging
- Smart asset dependency mapping

### 🎮 Intelligent Actor Manipulation  
- AI-guided actor placement and scene composition
- Context-aware duplication and transformation
- Smart surface placement via AI-enhanced raycasting
- Intelligent scene analysis and optimization suggestions

### 🧠 Claude AI Integration
- Natural language commands for Unreal Engine operations
- AI-powered Blueprint analysis and explanations
- Intelligent workflow suggestions and optimizations
- Context-aware technical documentation generation

### 🔧 MCP-Powered Editor Tools
- **Unreal MCP** server for real-time AI communication
- Batch operations with AI guidance
- Smart material and mesh replacement workflows
- AI-assisted debugging and troubleshooting

## 🚀 Installation Guide

### Prerequisites for Unreal-MCP Setup
This **Unreal AI** integration requires the Model Context Protocol setup. Please refer to the [MCP official documentation](https://modelcontextprotocol.io/quickstart/user) for comprehensive details.


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