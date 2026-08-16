"""AI Agent integration module for ClaudeMark."""

from .tools import AGENT_TOOLS_MANIFEST, execute_agent_tool

__all__ = [
    "AGENT_TOOLS_MANIFEST",
    "execute_agent_tool",
]
