# Copyright (c) 2025 GenOrca. All Rights Reserved.

import unreal
import json
import os
import glob
import traceback

def ue_print_message(message: str = None) -> str:
    """
    Logs a message to the Unreal log and returns a JSON success response.
    """
    if message is None:
        return json.dumps({"success": False, "message": "Required parameter 'message' is missing."})

    unreal.log(f"MCP Message: {message}")
    return json.dumps({
        "received_message": message,
        "success": True,
        "source": "ue_print_message"
    })

def ue_get_output_log(line_count: int = 50, keyword: str = None) -> str:
    """Returns recent lines from the Unreal Engine output log file."""
    try:
        log_dir = unreal.Paths.project_log_dir()
        log_files = glob.glob(os.path.join(log_dir, "*.log"))
        if not log_files:
            return json.dumps({"success": False, "message": "No log files found"})

        latest_log = max(log_files, key=os.path.getmtime)

        with open(latest_log, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()

        if keyword:
            lines = [l for l in all_lines if keyword.lower() in l.lower()]
            lines = lines[-line_count:]
        else:
            lines = all_lines[-line_count:]

        return json.dumps({
            "success": True,
            "log_file": os.path.basename(latest_log),
            "total_lines": len(all_lines),
            "returned_lines": len(lines),
            "log": "".join(l.rstrip('\r') for l in lines)
        })
    except Exception as e:
        return json.dumps({"success": False, "message": str(e), "traceback": traceback.format_exc()})
