"""Command processor for POLLY agent:tool CLI."""
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedCommand:
    """Result of parsing user input."""
    agent: str = ""
    tool: str = ""
    args: dict[str, str] = field(default_factory=dict)
    raw: str = ""
    builtin: str = ""          # non-empty for builtins like "help", "exit"
    builtin_arg: str = ""      # e.g. "content" in "help content"
    is_valid: bool = False
    error: str = ""


# Builtins that are not agent:tool commands
BUILTINS = {"help", "agents", "history", "context", "clear", "exit", "quit"}


def parse_command(raw_input: str) -> ParsedCommand:
    """
    Parse user input into a ParsedCommand.

    Syntax:
        agent:tool key:value key:"multi word value" ...
        help [agent|agent:tool]
        agents | history | context | clear | exit
    """
    cmd = ParsedCommand(raw=raw_input)
    text = raw_input.strip()
    if not text:
        cmd.error = "Empty input"
        return cmd

    tokens = _tokenize(text)
    if not tokens:
        cmd.error = "Could not parse input"
        return cmd

    first = tokens[0]

    # Check if first token is a builtin
    first_lower = first.lower()
    if first_lower in BUILTINS:
        cmd.builtin = first_lower
        if first_lower == "quit":
            cmd.builtin = "exit"
        # Builtin argument (e.g. "help content" or "help content:copywriting")
        if len(tokens) > 1:
            cmd.builtin_arg = tokens[1]
        cmd.is_valid = True
        return cmd

    # Expect agent:tool as first token
    if ":" not in first:
        cmd.error = f"Expected agent:tool format, got '{first}'. Type 'help' for usage."
        return cmd

    parts = first.split(":", 1)
    cmd.agent = parts[0]
    cmd.tool = parts[1]

    if not cmd.agent or not cmd.tool:
        cmd.error = f"Invalid command '{first}'. Use agent:tool format (e.g. content:copywriting)"
        return cmd

    # Parse remaining tokens as key:value args
    for token in tokens[1:]:
        if ":" in token:
            key, _, value = token.partition(":")
            if key:
                cmd.args[key] = value
            else:
                cmd.error = f"Invalid argument: '{token}'"
                return cmd
        else:
            # Positional arg — treat as value for implicit 'input' key
            if "input" not in cmd.args:
                cmd.args["input"] = token
            else:
                cmd.args["input"] += " " + token

    cmd.is_valid = True
    return cmd


def _tokenize(text: str) -> list[str]:
    """
    Tokenize input respecting quoted strings.

    Handles:
        key:"multi word value"
        key:'multi word value'
        key:value
        bare_word
    """
    tokens = []
    # Match key:"quoted value", key:'quoted value', or non-space sequences
    pattern = r'''(\S+?:"[^"]*"|\S+?:'[^']*'|\S+)'''
    for match in re.finditer(pattern, text):
        token = match.group(1)
        # Strip quotes from values
        if ':"' in token:
            key, _, val = token.partition(':"')
            val = val.rstrip('"')
            token = f"{key}:{val}"
        elif ":'" in token:
            key, _, val = token.partition(":'")
            val = val.rstrip("'")
            token = f"{key}:{val}"
        tokens.append(token)
    return tokens
