"""Minimal dependency-free MCP stdio server for ClaudeMark agent tools."""

from __future__ import annotations

import json
import sys
from typing import Any

from .agent.tools import AGENT_TOOLS_MANIFEST, execute_agent_tool
from . import __version__


def _respond(request_id: Any, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result or {}
    print(json.dumps(payload), flush=True)


def serve_stdio() -> None:
    """Serve JSON-RPC MCP messages over stdin/stdout without network access."""
    tool_names = {tool["name"] for tool in AGENT_TOOLS_MANIFEST}
    for raw in sys.stdin:
        try:
            request = json.loads(raw)
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id")
            if method == "initialize":
                _respond(req_id, {"protocolVersion": "2024-11-05", "serverInfo": {"name": "claudemark", "version": __version__}, "capabilities": {"tools": {}}})
            elif method == "tools/list":
                _respond(req_id, {"tools": AGENT_TOOLS_MANIFEST})
            elif method == "tools/call":
                name = params.get("name")
                if name not in tool_names:
                    raise ValueError(f"Unknown tool: {name}")
                result = execute_agent_tool(name, params.get("arguments", {}))
                _respond(req_id, {"content": [{"type": "text", "text": json.dumps(result)}], "structuredContent": result})
            elif req_id is not None:
                _respond(req_id, error={"code": -32601, "message": f"Method not found: {method}"})
        except Exception as exc:
            _respond(request.get("id") if "request" in locals() else None, error={"code": -32602, "message": str(exc)})


if __name__ == "__main__":
    serve_stdio()
