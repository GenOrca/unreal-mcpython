from setuptools import setup, find_packages

setup(
    name="unreal-mcp",
    version="1.0.0",
    description="MCP Server for Unreal Engine integration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "unreal-mcp=unreal_mcp.server:run_server",
            "unreal-mcp-test=main:test_server"
        ],
    },
)