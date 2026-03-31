#!/usr/bin/env python3
"""
polly -- AI Marketing CLI for Financial Advisors

Central entry point for all polly commands. Run `python polly.py help` to see
available commands, or `python polly.py <command> --help` for command-specific options.

Default (no args): launches the marketing CLI REPL.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
AGENTS = ROOT / "agents"

COMMANDS = {
    "cli": {
        "script": ROOT / "tui_main.py",
        "summary": "Launch the marketing CLI (interactive REPL with agent:tool interface)",
        "usage": "python polly.py [cli]",
        "options": [],
    },
    "test": {
        "summary": "Run a single agent:tool command and print the result",
        "usage": 'python polly.py test <agent:tool> [key:value ...]',
        "options": [
            ("agent:tool", "Tool to run, e.g. strategy:launch"),
            ("key:value", "Parameters, e.g. product:\"AI tool\" stage:pre-launch"),
        ],
        "builtin": "test",
    },
    "tui": {
        "script": ROOT / "tui_main.py",
        "summary": "Alias for 'cli' (launch the marketing CLI)",
        "usage": "python polly.py tui",
        "options": [],
    },
    "web": {
        "script": ROOT / "Home.py",
        "summary": "Launch the Streamlit web dashboard (legacy)",
        "usage": "python polly.py web",
        "runner": "streamlit",
        "options": [],
    },
    "ui": {
        "script": ROOT / "web" / "app.py",
        "summary": "Launch the FastHTML web UI",
        "usage": "python polly.py ui [--port PORT]",
        "options": [
            ("--port PORT", "Port to run on (default: 5001)"),
        ],
    },
}


def print_help():
    print("polly -- AI Marketing CLI for Financial Advisors\n")
    print("Usage: python polly.py [command] [options]\n")
    print("Commands:")
    max_name = max(len(name) for name in COMMANDS)
    for name, info in COMMANDS.items():
        print(f"  {name:<{max_name + 2}} {info['summary']}")
    print(f"\n  {'help':<{max_name + 2}} Show this help message")
    print(f"\nDefault (no args): launches the marketing CLI REPL.")
    print(f"Run 'python polly.py <command> --help' for command-specific options.")


def print_command_help(name: str):
    info = COMMANDS[name]
    print(f"{name} - {info['summary']}\n")
    print(f"Usage: {info['usage']}\n")
    if info["options"]:
        print("Options:")
        max_opt = max(len(opt) for opt, _ in info["options"])
        for opt, desc in info["options"]:
            print(f"  {opt:<{max_opt + 2}} {desc}")
    print()


def run_test(argv: list[str]):
    """Run a single agent:tool command directly — no REPL, no web."""
    import asyncio
    import time

    sys.path.insert(0, str(ROOT))
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    from agents.base import ToolStatus
    from agents.registry import AgentRegistry
    from context.session import SessionContext

    if not argv or ":" not in argv[0]:
        print("Usage: python polly.py test <agent:tool> [key:value ...]")
        print('Example: python polly.py test strategy:launch product:"AI analytics tool"')
        sys.exit(1)

    # Parse agent:tool and key:value args
    cmd = argv[0]
    agent_name, tool_name = cmd.split(":", 1)

    args = {}
    # Join remaining args and parse key:value pairs (supports quoted values)
    raw = " ".join(argv[1:])
    import shlex
    try:
        tokens = shlex.split(raw)
    except ValueError:
        tokens = raw.split()

    for token in tokens:
        if ":" in token:
            k, v = token.split(":", 1)
            args[k] = v

    # Boot
    AgentRegistry.reset()
    reg = AgentRegistry.get()
    ctx = SessionContext()

    from integrations.xai_int import XaiIntegration
    from integrations.arcade_int import ArcadeIntegration
    from integrations.playwright_int import PlaywrightIntegration
    from integrations.composio_int import ComposioIntegration
    from agents.content import ContentAgent
    from agents.strategy import StrategyAgent
    from agents.social import SocialAgent
    from agents.cro import CroAgent
    from agents.seo import SeoAgent
    from agents.ads import AdsAgent
    from agents.compliance import ComplianceAgent
    from agents.campaign import CampaignAgent
    from agents.channels import ChannelsAgent

    for Int in [XaiIntegration, ArcadeIntegration, PlaywrightIntegration, ComposioIntegration]:
        inst = Int()
        if inst.is_configured():
            ctx.set_integration(inst.name, inst)

    for Cls in [ContentAgent, StrategyAgent, SocialAgent, CroAgent, SeoAgent, AdsAgent, ComplianceAgent, CampaignAgent, ChannelsAgent]:
        reg.register(Cls())

    # Resolve
    agent = reg.get_agent(agent_name)
    if not agent:
        print(f"Unknown agent: {agent_name}")
        print(f"Available: {', '.join(a.name for a in reg.all_agents())}")
        sys.exit(1)

    tool_def = agent.resolve_tool(tool_name)
    if not tool_def:
        print(f"Unknown tool: {agent_name}:{tool_name}")
        tools = agent.get_tools()
        print(f"Available: {', '.join(t.name for t in tools)}")
        sys.exit(1)

    resolved = tool_def.name
    eta = tool_def.estimated_seconds
    print(f"Running {agent_name}:{resolved}... (~{eta}s)")
    if args:
        print(f"  args: {args}")

    # Execute
    t0 = time.monotonic()

    async def _run():
        return await agent.execute(resolved, args, ctx)

    result = asyncio.run(_run())
    elapsed = time.monotonic() - t0

    if result.status == ToolStatus.SUCCESS:
        print(f"\n--- SUCCESS ({elapsed:.1f}s) ---\n")
        print(result.output)
    elif result.status == ToolStatus.NEEDS_INPUT:
        print(f"\n--- NEEDS INPUT ({elapsed:.1f}s) ---")
        print(result.follow_up_prompt or result.output)
    else:
        print(f"\n--- ERROR ({elapsed:.1f}s) ---")
        print(result.error or result.output)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        cmd = "cli"
    elif sys.argv[1] in ("help", "--help", "-h"):
        print_help()
        return
    else:
        cmd = sys.argv[1]

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Run 'python polly.py help' for available commands.")
        sys.exit(1)

    info = COMMANDS[cmd]
    extra_args = sys.argv[2:]

    if "--help" in extra_args or "-h" in extra_args:
        print_command_help(cmd)
        return

    # Built-in commands (no subprocess)
    if info.get("builtin") == "test":
        run_test(extra_args)
        return

    runner = info.get("runner")
    if runner == "streamlit":
        run_cmd = [sys.executable, "-m", "streamlit", "run", str(info["script"])] + extra_args
    else:
        run_cmd = [sys.executable, str(info["script"])] + extra_args

    result = subprocess.run(run_cmd, cwd=ROOT)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
