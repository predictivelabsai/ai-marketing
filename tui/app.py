"""POLLY Marketing CLI — interactive REPL with agent:tool interface."""
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console
from dotenv import load_dotenv

from agents.base import ToolStatus
from agents.registry import AgentRegistry
from context.session import SessionContext
from help.renderer import HelpRenderer
from tui.components.command_processor import parse_command, BUILTINS


class AgentCompleter(Completer):
    """3-level completer: agents → tools → param keys."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)

        # If we have a full agent:tool already plus a space, complete params
        parts = text.strip().split()
        if len(parts) >= 1 and ":" in parts[0] and len(parts) > 1:
            agent_name, tool_name = parts[0].split(":", 1)
            agent = self.registry.get_agent(agent_name)
            if agent:
                tool = agent.resolve_tool(tool_name)
                if tool:
                    for key in tool.parameters:
                        candidate = f"{key}:"
                        if candidate.startswith(word):
                            yield Completion(candidate, start_position=-len(word),
                                             display_meta=tool.parameters[key].get("description", ""))

        elif ":" in word:
            # Completing tool part of agent:tool
            prefix = word
            for comp in self.registry.all_completions():
                if comp.startswith(prefix):
                    yield Completion(comp, start_position=-len(word))
        else:
            # Completing agent name or builtin
            for comp in self.registry.all_completions():
                if comp.startswith(word):
                    yield Completion(comp, start_position=-len(word))
            for builtin in sorted(BUILTINS):
                if builtin.startswith(word):
                    yield Completion(builtin, start_position=-len(word))


class PollyApp:
    """Interactive marketing CLI REPL."""

    def __init__(self):
        self.console = Console(stderr=True)
        self.registry = AgentRegistry.get()
        self.context = SessionContext()
        self.help = HelpRenderer(self.registry)
        self.command_history: list[str] = []

        # Initialize integrations
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        self._init_integrations()
        self._register_agents()

        # Prompt session with file history + agent completer
        history_file = Path(__file__).parent.parent / ".polly_history"
        kb = KeyBindings()

        @kb.add("c-l")
        def _clear(event):
            event.app.renderer.clear()

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=AgentCompleter(self.registry),
            key_bindings=kb,
            complete_while_typing=False,
        )

    def _init_integrations(self) -> None:
        """Lazily initialize integration backends from env."""
        from integrations.xai_int import XaiIntegration
        from integrations.arcade_int import ArcadeIntegration
        from integrations.playwright_int import PlaywrightIntegration
        from integrations.composio_int import ComposioIntegration

        xai = XaiIntegration()
        arcade = ArcadeIntegration()
        playwright = PlaywrightIntegration()
        composio = ComposioIntegration()

        if xai.is_configured():
            self.context.set_integration("xai", xai)
        if arcade.is_configured():
            self.context.set_integration("arcade", arcade)
        if playwright.is_configured():
            self.context.set_integration("playwright", playwright)
        if composio.is_configured():
            self.context.set_integration("composio", composio)

    def _register_agents(self) -> None:
        """Register all agent implementations."""
        from agents.content import ContentAgent
        from agents.strategy import StrategyAgent
        from agents.social import SocialAgent
        from agents.cro import CroAgent
        from agents.seo import SeoAgent
        from agents.ads import AdsAgent
        from agents.compliance import ComplianceAgent
        from agents.campaign import CampaignAgent
        from agents.channels import ChannelsAgent

        for AgentClass in [ContentAgent, StrategyAgent, SocialAgent, CroAgent, SeoAgent, AdsAgent, ComplianceAgent, CampaignAgent, ChannelsAgent]:
            self.registry.register(AgentClass())

    def _display_welcome(self) -> None:
        agents = self.registry.all_agents()
        total_tools = sum(len(a.get_tools()) for a in agents)

        # Integration status
        integrations = []
        for name in ["xai", "arcade", "playwright", "composio"]:
            status = "[green]ready[/green]" if self.context.get_integration(name) else "[dim]not configured[/dim]"
            integrations.append(f"{name}: {status}")

        self.console.print(
            "\n[bold cyan]"
            "╔══════════════════════════════════════════════════╗\n"
            "║  POLLY -- AI Marketing CLI for Financial Advisors ║\n"
            "╚══════════════════════════════════════════════════╝"
            "[/bold cyan]\n"
            f"\n  {len(agents)} agents, {total_tools} tools loaded"
            f"\n  Integrations: {' | '.join(integrations)}"
            "\n"
            "\n  Type [cyan]help[/cyan] for commands, [cyan]help <agent>[/cyan] for tools"
            "\n  Tab for autocomplete, Ctrl+L to clear\n"
        )

    def _handle_builtin(self, builtin: str, arg: str) -> None:
        """Handle a builtin command."""
        if builtin == "help":
            if not arg:
                self.console.print(self.help.render_overview())
            elif ":" in arg:
                agent, tool = self.registry.resolve(arg)
                if agent and tool:
                    tool_def = agent.resolve_tool(tool)
                    self.console.print(self.help.render_tool(agent, tool_def))
                elif agent:
                    self.console.print(f"[red]Unknown tool '{arg}'. Available tools for {agent.name}:[/red]")
                    self.console.print(self.help.render_agent(agent))
                else:
                    self.console.print(f"[red]Unknown agent: '{arg.split(':')[0]}'[/red]")
            else:
                agent = self.registry.get_agent(arg)
                if agent:
                    self.console.print(self.help.render_agent(agent))
                else:
                    self.console.print(f"[red]Unknown agent: '{arg}'. Type 'help' for list.[/red]")

        elif builtin == "agents":
            for agent in self.registry.all_agents():
                tool_count = len(agent.get_tools())
                self.console.print(f"  [cyan]{agent.name:<12}[/cyan] {tool_count} tools — {agent.description}")

        elif builtin == "context":
            if self.context.product.is_set():
                self.console.print(self.context.product.to_prompt_block())
            else:
                self.console.print("[dim]No product context set. Use: strategy:product-context set company:... product:...[/dim]")

        elif builtin == "history":
            if self.command_history:
                self.console.print("[bold]Command History:[/bold]")
                for i, cmd in enumerate(self.command_history[-20:], 1):
                    self.console.print(f"  {i}. {cmd}")
            else:
                self.console.print("[dim]No command history yet.[/dim]")

        elif builtin == "clear":
            self.console.clear()

        elif builtin == "exit":
            raise EOFError

    async def _execute_agent_command(self, agent_name: str, tool_name: str, args: dict) -> None:
        """Route to the appropriate agent and execute."""
        import time

        agent, resolved_tool = self.registry.resolve(f"{agent_name}:{tool_name}")

        if not agent:
            self.console.print(f"[red]Unknown agent: '{agent_name}'. Type 'help' for list.[/red]")
            return
        if not resolved_tool:
            self.console.print(f"[red]Unknown tool: '{agent_name}:{tool_name}'. Type 'help {agent_name}' for tools.[/red]")
            return

        # Show ETA from tool definition
        tool_def = agent.resolve_tool(resolved_tool)
        eta = tool_def.estimated_seconds if tool_def else 10
        self.console.print(f"[cyan]Running {agent_name}:{resolved_tool}...[/cyan] [dim](~{eta}s)[/dim]")

        t0 = time.monotonic()
        result = await agent.execute(resolved_tool, args, self.context)
        elapsed = time.monotonic() - t0

        if result.status == ToolStatus.SUCCESS:
            self.console.print(f"[green]Success[/green] [dim]({elapsed:.1f}s)[/dim]")
            if result.output:
                self.console.print(result.output)
        elif result.status == ToolStatus.NEEDS_INPUT:
            self.console.print(f"[yellow]Needs input:[/yellow] {result.follow_up_prompt or result.output}")
        else:
            self.console.print(f"[red]Error:[/red] [dim]({elapsed:.1f}s)[/dim] {result.error or result.output}")

    async def _handle_input(self, user_input: str) -> None:
        text = user_input.strip()
        if not text:
            return

        self.command_history.append(text)
        cmd = parse_command(text)

        if not cmd.is_valid:
            self.console.print(f"[red]{cmd.error}[/red]")
            return

        if cmd.builtin:
            self._handle_builtin(cmd.builtin, cmd.builtin_arg)
            return

        await self._execute_agent_command(cmd.agent, cmd.tool, cmd.args)

    async def run(self) -> None:
        """Main REPL loop."""
        self._display_welcome()

        with patch_stdout():
            while True:
                try:
                    user_input = await self.session.prompt_async("polly> ")
                    await self._handle_input(user_input)
                except (EOFError, KeyboardInterrupt):
                    # Clean up playwright if used
                    pw = self.context.get_integration("playwright")
                    if pw and hasattr(pw, "close"):
                        await pw.close()
                    self.console.print("\nGoodbye!")
                    break


async def run_app():
    """Run the PollyApp."""
    app = PollyApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(run_app())
