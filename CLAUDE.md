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

FastHTML app on port 5055 with session-based auth (bcrypt passwords, `polly.users` table via `utils/auth.py` and `utils/db_pool.py`).

**Routes:**
- `/` — Landing page with feature cards
- `/about` — About page with personas, document workflow, channels
- `/demo` — Interactive WhatsApp/Telegram device simulator
- `/chat` — Main chat interface (requires login). Vertical 3-zone layout: 6 starter skill buttons (shown initially) → scrollable message area → large textarea input at bottom. Starter buttons hide when first message is sent.
- `/profile` — User profile with API integrations (status badges for XAI, Arcade, Playwright, Composio, WhatsApp, Telegram) and 39 marketing skills grid grouped by agent
- `/signin`, `/register`, `/logout` — Authentication

**Layout pattern (chat page):** Follows the alpatrade vertical 3-zone pattern — top nav, expanding middle content (starter grid or messages), fixed input bar at bottom. Uses `flex-direction: column` with `flex: 1` on the message area.

**Auth flow:** `utils/auth.py` handles bcrypt hashing and `polly.users` queries. Session stored via FastHTML `secret_key` cookie. `DB_URL` env var for PostgreSQL connection via `utils/db_pool.py` singleton.

### TUI (tui/app.py)

`PollyApp` is a prompt_toolkit REPL with:
- `AgentCompleter` — 3-level tab completion (agent → tool → params)
- File-based history (`.polly_history`)
- Builtins: `help`, `agents`, `context`, `history`, `clear`, `exit`

## User Guide Generation

The in-app User Guide (`/guide`) displays screenshots from `static/guide/`.
To regenerate all screenshots after UI changes:

```bash
# Option 1: App already running
python tests/capture_guide.py

# Option 2: Auto-start app
python tests/capture_guide.py --start-app
```

This launches a headless Playwright browser, registers/logs in, navigates every page,
captures 17 screenshots to `static/guide/`, and captures chat command responses.
The `/guide` route serves them as `<img src="/static/guide/...">`.

When the user says "regenerate guide" or "update screenshots", run `python tests/capture_guide.py`.

## Demo Video Generation

```bash
# Capture frames and build MP4 + GIF (~33s, 22 frames)
python tests/capture_video.py --start-app

# Output: docs/demo_video.mp4 (1MB), docs/demo_video.gif (0.8MB), docs/frames/*.png
```

Walks through: home → about → login → chat (starters, campaign, compliance, analytics) → profile → instructions editor → demo (WhatsApp, Telegram, analytics, campaign preview) → home.
When the user says "regenerate video" or "update demo", run `python tests/capture_video.py`.

## Slide Deck Generation

```bash
# Generate the PowerPoint presentation
python docs/generate_pptx.py

# Output: docs/POLLY_Platform_Overview.pptx (16 slides)
# Uses screenshots from static/guide/ for slide visuals
# Upload to Google Slides or open in PowerPoint
```

To regenerate after changes: update screenshots first (see User Guide Generation above), then run the script.

## RAG Document Pipeline

```bash
# Process all documents in doc-data/ into vector embeddings
python tasks/create_rag.py

# Query the document knowledge base (single question)
python tests/query_docs.py -q "What is the XTCC Solar product?"

# Run full RAG evaluation (8 test queries, writes test-results/rag_evaluation.json)
python tests/query_docs.py
```

Schema: `polly_rag` (separate from main `polly` schema). Tables: `documents`, `chunks` (pgvector 384d), `query_log`.
Embedding model: `BAAI/bge-small-en-v1.5` (local via fastembed, no API key needed).
Text extraction: `pymupdf4llm` (PDF), `python-pptx` (PPTX), `python-docx` (DOCX).

## Prompt Management

System prompts are stored in `polly.prompts` table. `PromptService` (`utils/prompt_service.py`) resolves prompts with chain: user override → global DB default → hardcoded fallback. Template var `{{today}}` is replaced at resolve time. The `/instructions` route provides a per-agent editor with admin-only global prompt editing.

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
