"""Agent registry singleton for POLLY marketing CLI."""
from typing import Optional

from .base import BaseAgent, ToolDefinition


class AgentRegistry:
    """Singleton registry holding all agent instances."""

    _instance: Optional["AgentRegistry"] = None

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    @classmethod
    def get(cls) -> "AgentRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def resolve(self, command: str) -> tuple[Optional[BaseAgent], Optional[str]]:
        """
        Resolve 'agent:tool' string to (agent_instance, tool_name).
        Returns (None, None) if agent not found.
        Returns (agent, None) if agent found but tool not found.
        """
        if ":" not in command:
            agent = self._agents.get(command)
            return (agent, None)

        agent_name, tool_name = command.split(":", 1)
        agent = self._agents.get(agent_name)
        if not agent:
            return (None, None)

        tool = agent.resolve_tool(tool_name)
        if not tool:
            return (agent, None)

        return (agent, tool.name)

    def all_agents(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def all_completions(self) -> list[str]:
        """Return every valid agent:tool string for autocomplete."""
        results = list(self._agents.keys())
        for agent in self._agents.values():
            results.extend(agent.get_completions())
        return results

    def all_tool_definitions(self) -> list[tuple[str, ToolDefinition]]:
        """Return (agent_name, tool_def) for every registered tool."""
        results = []
        for agent in self._agents.values():
            for tool in agent.get_tools():
                results.append((agent.name, tool))
        return results
