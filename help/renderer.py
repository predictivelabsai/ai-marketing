"""Rich-based hierarchical help renderer for POLLY CLI."""
from agents.base import BaseAgent, ToolDefinition
from agents.registry import AgentRegistry


class HelpRenderer:
    """Renders help at three levels: overview, agent, and tool."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def render_overview(self) -> str:
        """Top-level help showing all agents."""
        agents = self.registry.all_agents()
        lines = [
            "",
            "[bold cyan]╔══════════════════════════════════════════════════╗[/bold cyan]",
            "[bold cyan]║  POLLY -- AI Marketing for Financial Advisors     ║[/bold cyan]",
            "[bold cyan]╚══════════════════════════════════════════════════╝[/bold cyan]",
            "",
        ]

        if agents:
            # Calculate column widths
            max_name = max(len(a.name) for a in agents)
            max_name = max(max_name, 6)  # minimum width

            lines.append(f"  [bold]{'AGENT':<{max_name}}  TOOLS  DESCRIPTION[/bold]")
            for agent in agents:
                tool_count = len(agent.get_tools())
                lines.append(f"  [cyan]{agent.name:<{max_name}}[/cyan]  {tool_count:<5}  {agent.description}")

        lines.append("")
        lines.append("  [bold]COMMANDS[/bold]")
        lines.append("  [cyan]help[/cyan] \\[agent|agent:tool]  Show help (overview, agent, or tool level)")
        lines.append("  [cyan]agents[/cyan]                    List all agents with tool counts")
        lines.append("  [cyan]context[/cyan]                   Show current product context")
        lines.append("  [cyan]history[/cyan]                   Show command history")
        lines.append("  [cyan]clear[/cyan]                     Clear screen")
        lines.append("  [cyan]exit[/cyan]                      Exit POLLY")
        lines.append("")
        return "\n".join(lines)

    def render_agent(self, agent: BaseAgent) -> str:
        """Agent-level help showing all tools in that agent."""
        tools = agent.get_tools()
        lines = [
            "",
            f"[bold cyan]╔══════════════════════════════════════════════════╗[/bold cyan]",
            f"[bold cyan]║  {agent.name} — {agent.description:<42}║[/bold cyan]",
            f"[bold cyan]╚══════════════════════════════════════════════════╝[/bold cyan]",
            "",
        ]

        if tools:
            max_name = max(len(t.name) for t in tools)
            max_name = max(max_name, 4)
            max_alias = max((len(", ".join(t.aliases)) if t.aliases else 0) for t in tools)
            max_alias = max(max_alias, 7)

            lines.append(f"  [bold]{'TOOL':<{max_name}}  {'ALIASES':<{max_alias}}  DESCRIPTION[/bold]")
            for tool in tools:
                alias_str = ", ".join(tool.aliases) if tool.aliases else "-"
                lines.append(f"  [cyan]{tool.name:<{max_name}}[/cyan]  {alias_str:<{max_alias}}  {tool.description}")

        # Show examples from tools
        examples = []
        for tool in tools:
            if tool.examples:
                examples.extend(tool.examples[:1])  # First example from each tool

        if examples:
            lines.append("")
            lines.append("  [bold]EXAMPLES[/bold]")
            for ex in examples[:5]:
                lines.append(f"  [dim]{ex}[/dim]")

        lines.append("")
        return "\n".join(lines)

    def render_tool(self, agent: BaseAgent, tool: ToolDefinition) -> str:
        """Tool-level help showing detailed info for a specific tool."""
        lines = [
            "",
            f"[bold cyan]╔══════════════════════════════════════════════════╗[/bold cyan]",
            f"[bold cyan]║  {agent.name}:{tool.name:<40}║[/bold cyan]",
            f"[bold cyan]╚══════════════════════════════════════════════════╝[/bold cyan]",
            "",
        ]

        # Description
        if tool.long_help:
            lines.append(f"  {tool.long_help}")
        else:
            lines.append(f"  {tool.description}")
        lines.append("")

        # Parameters
        if tool.parameters:
            lines.append("  [bold]PARAMETERS[/bold]")
            max_key = max(len(k) for k in tool.parameters)
            for key, info in tool.parameters.items():
                req = "(required)" if info.get("required") else ""
                default = f"(default: {info['default']})" if info.get("default") else ""
                options = f"  options: {', '.join(info['options'])}" if info.get("options") else ""
                desc = info.get("description", "")
                suffix = " ".join(filter(None, [req, default]))
                lines.append(f"  [cyan]{key + ':':<{max_key + 1}}[/cyan]  {desc} {suffix}")
                if options:
                    lines.append(f"  {' ' * (max_key + 3)}{options}")
            lines.append("")

        # Integrations
        if tool.required_integrations:
            lines.append("  [bold]INTEGRATIONS[/bold]")
            int_labels = {
                "xai": "XAI/Grok for content generation",
                "arcade": "Arcade.dev for social posting",
                "playwright": "Playwright for page analysis",
                "composio": "Composio for third-party APIs",
            }
            for integ in tool.required_integrations:
                label = int_labels.get(integ, integ)
                lines.append(f"  {label}")
            lines.append("")

        # Examples
        if tool.examples:
            lines.append("  [bold]EXAMPLES[/bold]")
            for ex in tool.examples:
                lines.append(f"  [dim]{ex}[/dim]")
            lines.append("")

        return "\n".join(lines)
