# Copyright (c) 2025 GenOrca. All Rights Reserved.

import unreal
import json
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
