# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the interactive REPL
python polly.py              # or: python tui_main.py

# Run a single agent:tool command
python polly.py test content:teaser product:"FTSE Autocallable"

# Run the FastHTML web UI (port 5001)
python polly.py ui

# Run tests
pytest                              # all tests
pytest tests/test_social_poster.py  # single file
pytest -m "not slow"                # skip slow tests
pytest -m integration               # integration tests only

# Install dependencies
pip install -r requirements.txt
```

## Architecture

POLLY is an AI marketing CLI for financial advisors with 9 agents (54 tools) that generate compliant content via XAI/Grok, post via Arcade, and analyze pages via Playwright.

### Core flow

```
User Input ("agent:tool key:value")
    → parse_command() [tui/components/command_processor.py]
    → AgentRegistry.resolve() [agents/registry.py]
    → Agent.execute(tool_name, args, SessionContext) [async]
    → Integration call (XAI/Arcade/Playwright)
    → ToolResult (SUCCESS/ERROR/NEEDS_INPUT)
```

### Key abstractions (agents/base.py)

- **BaseAgent** — ABC with `get_tools() -> list[ToolDefinition]` and `async execute() -> ToolResult`
- **ToolDefinition** — Declares name, description, aliases, parameters (with required/default/options), examples, required_integrations, estimated_seconds
- **ToolResult** — Returns status (ToolStatus enum), output text, optional data dict, error, follow_up_prompt
- **AgentRegistry** — Singleton that resolves `"agent:tool"` strings to `(BaseAgent, tool_name)` tuples

### Session state (context/session.py)

`SessionContext` holds:
- **ProductContext** — Company/product info + financial fields (product_type, jurisdiction, target_market, negative_target, risk_level). `to_prompt_block()` renders it for LLM system prompt injection.
- **ComplianceDocSet** — 10 document slots (prospectus, term_sheet, priips, etc.) with `approved_docs` dict tracking approval status. `to_prompt_block()` injects approved doc snippets into LLM prompts.
- **UserPersona** — Enum: MANAGEMENT (can approve docs), SALES, CAMPAIGN (default)
- **Integrations** — Dict of initialized backends, accessed via `get_integration("xai")`

### Adding a new agent

1. Create `agents/youragent/__init__.py` with a class extending `BaseAgent`
2. Set `name` and `description` class attributes
3. Implement `get_tools()` returning `list[ToolDefinition]`
4. Implement `async execute()` — route by tool_name, build system prompt with `context.product.to_prompt_block()`, call `xai.generate(system, user)`
5. Register in `tui/app.py::_register_agents()` and `polly.py::run_test()`

### Integrations (integrations/)

All extend `IntegrationBackend` ABC with `is_configured() -> bool`. Initialized lazily in `PollyApp._init_integrations()` — only backends with valid env vars are added to the session.

| Backend | Config | Used by |
|---------|--------|---------|
| XAI/Grok | `XAI_API_KEY`, `XAI_MODEL` | All content-generating agents |
| Arcade | `ARCADE_API_KEY`, `ARCADE_USER_ID` | social agent (X/LinkedIn posting) |
| Playwright | (auto) | cro, seo agents (page analysis) |
| Composio | `COMPOSIO_API_KEY` | channels, ads agents (stub) |

### Web UI (web/app.py)

FastHTML app on port 5001 with three routes: `/` (home), `/about` (about page), `/demo` (interactive WhatsApp/Telegram simulator). Uses `fast_app(pico=False)` with custom CSS. No shared state with the CLI agents.

### TUI (tui/app.py)

`PollyApp` is a prompt_toolkit REPL with:
- `AgentCompleter` — 3-level tab completion (agent → tool → params)
- File-based history (`.polly_history`)
- Builtins: `help`, `agents`, `context`, `history`, `clear`, `exit`

## Regulatory rules for generated content

- Never guarantee investment returns or performance
- Always include risk warnings per jurisdiction (UK/EU/US/APAC) and channel
- All content must be fair, clear, and not misleading (FCA/MiFID II)
- Past performance disclaimers are mandatory when referencing historical data
- Respect target market restrictions — never market to negative target market
- All agent system prompts encode these rules; maintain them when modifying prompts

## Environment

- Python 3.12+, async/await throughout
- `.env` file for credentials (see `.env.sample`); minimum: `XAI_API_KEY`
- Tests use pytest with markers: `slow`, `integration`, `unit`
