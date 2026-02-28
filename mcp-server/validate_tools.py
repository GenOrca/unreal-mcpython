#!/usr/bin/env python3
# Copyright (c) 2025 GenOrca. All Rights Reserved.

"""
Validates that MCP server router function names match plugin action function names.

Convention: router function 'foo_bar' must have a corresponding plugin function 'ue_foo_bar'.

Usage:
    python validate_tools.py [plugin_python_dir]

When run without arguments, auto-detects the plugin directory from the monorepo layout:
    <repo_root>/Content/Python/UnrealMCPython/
"""

import ast
import sys
import os
from pathlib import Path


# Router file → MODULE constant name → plugin file mapping
ROUTER_DIR = Path(__file__).parent / "src" / "unreal_mcp" / "tool_routers"


def _calls_send_unreal_action(func_node: ast.AsyncFunctionDef) -> bool:
    """Check if an async function body contains a call to send_unreal_action."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "send_unreal_action":
                return True
    return False


def extract_async_functions(filepath: Path) -> list[str]:
    """Extract async function names that use send_unreal_action from a Python file."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and _calls_send_unreal_action(node)
    ]


def extract_module_constant(filepath: Path) -> str | None:
    """Extract the *_ACTIONS_MODULE string constant from a router file."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id.endswith("_ACTIONS_MODULE")
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    return node.value.value
    return None


def extract_ue_functions(filepath: Path) -> set[str]:
    """Extract all function names starting with 'ue_' from a plugin action file."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("ue_")
    }


def module_to_filename(module_path: str) -> str:
    """Convert 'UnrealMCPython.actor_actions' → 'actor_actions.py'."""
    return module_path.split(".")[-1] + ".py"


def validate(plugin_dir: Path) -> bool:
    """Run validation and return True if all checks pass."""
    router_files = sorted(ROUTER_DIR.glob("*_router.py"))
    if not router_files:
        print(f"ERROR: No router files found in {ROUTER_DIR}")
        return False

    all_ok = True
    total_checked = 0

    for router_file in router_files:
        router_name = router_file.stem
        module_const = extract_module_constant(router_file)
        if not module_const:
            print(f"  WARN: No *_ACTIONS_MODULE constant found in {router_name}")
            continue

        plugin_filename = module_to_filename(module_const)
        plugin_file = plugin_dir / plugin_filename
        if not plugin_file.exists():
            print(f"  FAIL: Plugin file not found: {plugin_file}")
            all_ok = False
            continue

        router_functions = extract_async_functions(router_file)
        plugin_functions = extract_ue_functions(plugin_file)

        print(f"\n[{router_name}] → {plugin_filename}")
        print(f"  Router functions: {len(router_functions)}, Plugin ue_* functions: {len(plugin_functions)}")

        for func_name in router_functions:
            expected = f"ue_{func_name}"
            total_checked += 1
            if expected in plugin_functions:
                print(f"  OK   {func_name} → {expected}")
            else:
                print(f"  FAIL {func_name} → {expected} NOT FOUND in {plugin_filename}")
                all_ok = False

    print(f"\n{'='*60}")
    if all_ok:
        print(f"PASSED: All {total_checked} mappings verified successfully.")
    else:
        print(f"FAILED: Some mappings are missing. Fix the mismatches above.")
    print(f"{'='*60}")
    return all_ok


def main():
    if len(sys.argv) >= 2:
        plugin_dir = Path(sys.argv[1])
    else:
        # Auto-detect from monorepo layout: mcp-server/../Content/Python/UnrealMCPython
        plugin_dir = Path(__file__).parent.parent / "Content" / "Python" / "UnrealMCPython"

    if not plugin_dir.is_dir():
        print(f"ERROR: Plugin directory not found: {plugin_dir}")
        sys.exit(1)

    print(f"Router dir: {ROUTER_DIR}")
    print(f"Plugin dir: {plugin_dir}")

    ok = validate(plugin_dir)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
