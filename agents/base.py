"""Base agent abstraction for the POLLY marketing CLI."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ToolStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    NEEDS_INPUT = "needs_input"


@dataclass
class ToolDefinition:
    """Definition of a single tool within an agent."""
    name: str
    description: str
    long_help: str = ""
    aliases: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    required_integrations: list[str] = field(default_factory=list)
    parameters: dict[str, dict[str, Any]] = field(default_factory=dict)
    # parameter format: {"name": {"description": str, "required": bool, "default": str|None, "options": list|None}}
    estimated_seconds: int = 10  # approx wall-clock time for user-facing ETA


@dataclass
class ToolResult:
    """Result returned from executing a tool."""
    status: ToolStatus
    output: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    follow_up_prompt: str = ""


class BaseAgent(ABC):
    """Abstract base class for all POLLY agents."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def get_tools(self) -> list[ToolDefinition]:
        """Return list of tool definitions this agent provides."""
        ...

    @abstractmethod
    async def execute(self, tool_name: str, args: dict[str, str], context: Any) -> ToolResult:
        """Execute a tool with the given arguments and session context."""
        ...

    def resolve_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Find a tool by name or alias."""
        for tool in self.get_tools():
            if tool.name == tool_name or tool_name in tool.aliases:
                return tool
        return None

    def get_completions(self) -> list[str]:
        """Return all valid agent:tool strings for autocomplete."""
        results = []
        for tool in self.get_tools():
            results.append(f"{self.name}:{tool.name}")
            for alias in tool.aliases:
                results.append(f"{self.name}:{alias}")
        return results

    def get_param_completions(self, tool_name: str) -> list[str]:
        """Return parameter key completions for a specific tool."""
        tool = self.resolve_tool(tool_name)
        if not tool:
            return []
        return [f"{k}:" for k in tool.parameters]
