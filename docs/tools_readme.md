# soco Tools & Integrations

Technical reference for soco's internal architecture, integration backends, and data flow.

## System Architecture

```mermaid
flowchart TB
    subgraph ENTRY["Entry Points"]
        SOCO_PY["python soco.py"]
        SOCO_CLI["python soco.py cli"]
        SOCO_LEGACY["python soco.py generate|review|post|pipeline|run"]
    end

    subgraph REPL["Marketing CLI REPL"]
        APP["SocoApp<br/>(tui/app.py)"]
        PROMPT["PromptSession<br/>FileHistory + AgentCompleter"]
        PARSER["parse_command()<br/>(tui/components/command_processor.py)"]
    end

    subgraph CORE["Core Framework"]
        REGISTRY["AgentRegistry<br/>(agents/registry.py)"]
        BASE["BaseAgent ABC<br/>(agents/base.py)"]
        CONTEXT["SessionContext<br/>(context/session.py)"]
        PRODUCT["ProductContext"]
        HELP_R["HelpRenderer<br/>(help/renderer.py)"]
    end

    subgraph AGENT_IMPL["Agent Implementations"]
        A_CONTENT["ContentAgent<br/>agents/content/"]
        A_STRATEGY["StrategyAgent<br/>agents/strategy/"]
        A_SOCIAL["SocialAgent<br/>agents/social/"]
        A_CRO["CroAgent<br/>agents/cro/"]
        A_SEO["SeoAgent<br/>agents/seo/"]
        A_ADS["AdsAgent<br/>agents/ads/"]
    end

    subgraph INTEGRATIONS["Integration Backends"]
        INT_XAI["XaiIntegration<br/>integrations/xai_int.py"]
        INT_ARCADE["ArcadeIntegration<br/>integrations/arcade_int.py"]
        INT_PW["PlaywrightIntegration<br/>integrations/playwright_int.py"]
        INT_COMP["ComposioIntegration<br/>integrations/composio_int.py"]
    end

    subgraph EXTERNAL["External Services"]
        XAI_API["XAI API<br/>api.x.ai/v1"]
        ARCADE_API["Arcade.dev API<br/>X.PostTweet<br/>Linkedin.CreateTextPost"]
        BROWSER["Headless Chromium"]
        COMP_API["Composio API<br/>GA4, Mailchimp, etc."]
    end

    subgraph LEGACY["Legacy Pipeline"]
        GEN["generate_content.py"]
        REV["review_content.py"]
        POST["post_content.py"]
        PIPE["run_pipeline.py"]
        INTER["interactive_pipeline.py"]
        UTILS_SP["utils/social_poster.py"]
        UTILS_SUM["utils/summarizer.py"]
    end

    SOCO_PY --> SOCO_CLI
    SOCO_CLI --> APP
    SOCO_LEGACY --> GEN & REV & POST & PIPE & INTER
    GEN & POST --> UTILS_SP & UTILS_SUM

    APP --> PROMPT --> PARSER
    PARSER --> REGISTRY
    REGISTRY --> A_CONTENT & A_STRATEGY & A_SOCIAL & A_CRO & A_SEO & A_ADS
    CONTEXT --> PRODUCT

    A_CONTENT & A_STRATEGY & A_ADS --> INT_XAI
    A_SOCIAL --> INT_ARCADE
    A_CRO & A_SEO --> INT_PW
    A_CRO & A_SEO --> INT_XAI

    INT_XAI --> XAI_API
    INT_ARCADE --> ARCADE_API
    INT_PW --> BROWSER
    INT_COMP --> COMP_API

    APP --> HELP_R
    CONTEXT -.-> A_CONTENT & A_STRATEGY & A_SOCIAL & A_CRO & A_SEO & A_ADS
```

## Request Lifecycle

```mermaid
sequenceDiagram
    participant U as User
    participant R as REPL (SocoApp)
    participant P as Parser
    participant Reg as Registry
    participant A as Agent
    participant I as Integration
    participant E as External API

    U->>R: content:copywriting topic:"SaaS hero" format:headline
    R->>P: parse_command(raw_input)
    P-->>R: ParsedCommand{agent:"content", tool:"copywriting", args:{...}}

    R->>Reg: resolve("content:copywriting")
    Reg-->>R: (ContentAgent, "copywriting")

    R->>A: execute("copywriting", args, context)
    A->>A: validate required params
    A->>A: inject ProductContext into prompt
    A->>I: xai.generate(system, user, temp, max_tokens)
    I->>E: POST api.x.ai/v1/chat/completions
    E-->>I: response
    I-->>A: generated text
    A-->>R: ToolResult(SUCCESS, output)

    R->>U: Render output with Rich
```

## Integration Backends

### XaiIntegration

Wraps the OpenAI Python client pointed at XAI's endpoint.

```mermaid
flowchart LR
    AGENT["Agent"] --> XAI["XaiIntegration"]
    XAI --> CLIENT["OpenAI Client<br/>base_url: api.x.ai/v1"]
    CLIENT --> API["XAI API"]

    subgraph Config
        KEY["XAI_API_KEY"]
        MODEL["XAI_MODEL<br/>default: grok-3"]
    end

    Config --> XAI
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `generate()` | `async (system, user, temperature, max_tokens) → str` | Generate text via chat completion |
| `is_configured()` | `() → bool` | True if API key is set |

**Used by**: content, strategy, cro, seo, ads

### ArcadeIntegration

Thin wrapper around the `arcadepy` SDK for social media posting.

```mermaid
flowchart LR
    AGENT["SocialAgent"] --> ARC["ArcadeIntegration"]
    ARC --> SDK["arcadepy.Arcade"]
    SDK --> API["Arcade.dev API"]

    subgraph Tools
        TW["X.PostTweet"]
        LI["Linkedin.CreateTextPost"]
    end

    API --> Tools
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute_tool()` | `(tool_name, inputs) → dict` | Execute an Arcade tool |
| `is_configured()` | `() → bool` | True if API key and user ID are set |

**Used by**: social

### PlaywrightIntegration

Async Playwright browser manager for page crawling and analysis.

```mermaid
flowchart LR
    AGENT["CRO / SEO Agent"] --> PW["PlaywrightIntegration"]
    PW --> BROWSER["Headless Chromium"]
    BROWSER --> PAGE["Target Page"]

    subgraph Methods
        SNAP["get_page_snapshot(url)<br/>→ html, title, meta"]
        META["extract_meta(url)<br/>→ meta tags, headings, JSON-LD"]
        EVAL["evaluate_page(url, js)<br/>→ JS result"]
    end

    PW --> Methods
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_page_snapshot()` | `async (url) → dict` | Full page HTML + title + meta description |
| `extract_meta()` | `async (url) → dict` | Meta tags, headings (h1-h3), JSON-LD blocks |
| `evaluate_page()` | `async (url, js) → str` | Run arbitrary JS on page |
| `close()` | `async ()` | Clean up browser resources |

**Used by**: cro, seo

### ComposioIntegration

Stub wrapper for Composio SDK (GA4, Mailchimp, Semrush, etc.). Activates when `COMPOSIO_API_KEY` is set.

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute_action()` | `async (action, params) → dict` | Execute a Composio action |

**Used by**: ads (analytics-tracking), seo (future), content (email-sequence via Mailchimp)

## Core Framework

### BaseAgent

Abstract base class that all agents implement.

```python
class BaseAgent(ABC):
    name: str                           # "content", "seo", etc.
    description: str                    # One-liner for help

    def get_tools() -> list[ToolDefinition]
    async def execute(tool_name, args, context) -> ToolResult
    def resolve_tool(tool_name) -> Optional[ToolDefinition]   # by name or alias
    def get_completions() -> list[str]                         # agent:tool strings
    def get_param_completions(tool_name) -> list[str]          # param keys
```

### ToolDefinition

```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    long_help: str
    aliases: list[str]
    examples: list[str]
    required_integrations: list[str]
    parameters: dict[str, dict]
    # parameter dict: {"description": str, "required": bool, "default": str, "options": list}
```

### ToolResult

```python
@dataclass
class ToolResult:
    status: ToolStatus    # SUCCESS | ERROR | NEEDS_INPUT
    output: str
    data: dict
    error: str
    follow_up_prompt: str
```

### AgentRegistry

Singleton that holds all agent instances and provides resolution.

```mermaid
flowchart TD
    REG["AgentRegistry (singleton)"]
    REG --> |"resolve('content:copy')"| FIND["Find ContentAgent<br/>Resolve alias 'copy' → 'copywriting'"]
    FIND --> RESULT["(ContentAgent, 'copywriting')"]

    REG --> |"all_completions()"| COMP["82 strings<br/>agents + tools + aliases"]
    REG --> |"all_agents()"| LIST["6 BaseAgent instances"]
```

| Method | Description |
|--------|-------------|
| `get()` | Get singleton instance |
| `register(agent)` | Register an agent |
| `resolve(command)` | Parse `agent:tool` → (agent, tool_name) |
| `get_agent(name)` | Get agent by name |
| `all_completions()` | All valid autocomplete strings |
| `all_agents()` | All registered agent instances |

### SessionContext

Holds integration clients and shared state for a REPL session.

```mermaid
flowchart LR
    SESSION["SessionContext"]

    SESSION --> PRODUCT["ProductContext<br/>company, product, audience,<br/>tone, industry, website,<br/>competitors, value_proposition"]
    SESSION --> SCRATCH["scratch dict<br/>temp data between commands"]
    SESSION --> INT["Integration Clients<br/>xai, arcade, playwright, composio"]

    PRODUCT --> |"to_prompt_block()"| INJECT["Injected into every<br/>LLM system prompt"]
```

### ProductContext

Shared product context that all agents read for LLM prompt injection.

| Field | Type | Description |
|-------|------|-------------|
| `company` | str | Company name |
| `product` | str | Product name/description |
| `audience` | str | Target audience |
| `tone` | str | Default writing tone |
| `industry` | str | Industry vertical |
| `website` | str | Company website |
| `competitors` | list[str] | Competitor names |
| `value_proposition` | str | Core value proposition |
| `extra` | dict | Additional context |

Set via `strategy:product-context set company:... product:...` — persists for the session and is automatically injected into all LLM prompts.

## Command Parser

```mermaid
flowchart LR
    INPUT["'content:copy topic:\"SaaS hero\" format:headline'"]
    TOK["Tokenizer<br/>Respects quotes"]
    FIRST["First token<br/>content:copy"]
    REST["Remaining tokens<br/>key:value pairs"]
    CMD["ParsedCommand<br/>agent: content<br/>tool: copy<br/>args: {topic: SaaS hero, format: headline}"]

    INPUT --> TOK --> FIRST & REST --> CMD
```

The tokenizer handles:
- `key:value` — simple values
- `key:"multi word value"` — quoted strings
- `key:'single quoted'` — single quotes
- Builtin commands: `help`, `agents`, `context`, `history`, `clear`, `exit`

## Help System

Three levels of help, rendered with Rich markup:

```mermaid
flowchart TD
    HELP["help"]
    HELP --> |"help"| OVERVIEW["Overview<br/>All 6 agents with tool counts"]
    HELP --> |"help content"| AGENT["Agent Help<br/>All 7 content tools with aliases"]
    HELP --> |"help content:copywriting"| TOOL["Tool Help<br/>Parameters, integrations, examples"]
```

## Tab Completion

The `AgentCompleter` provides 3-level prompt_toolkit completion:

```mermaid
flowchart LR
    L1["Level 1: Agent Names<br/>content, strategy, social, ..."]
    L2["Level 2: Agent:Tool<br/>content:copywriting, content:edit, ..."]
    L3["Level 3: Parameters<br/>topic:, format:, tone:, ..."]

    L1 --> |"type :"| L2 --> |"type space"| L3
```

82 total completions including all agent names, `agent:tool` combinations, aliases, and builtin commands.

## Agent → Integration Mapping

```mermaid
graph LR
    subgraph Agents
        CONTENT["content"]
        STRATEGY["strategy"]
        SOCIAL["social"]
        CRO["cro"]
        SEO["seo"]
        ADS["ads"]
    end

    subgraph Integrations
        XAI["XAI/Grok"]
        ARCADE["Arcade.dev"]
        PW["Playwright"]
        COMP["Composio"]
    end

    CONTENT --> XAI
    STRATEGY --> XAI
    SOCIAL --> ARCADE
    CRO --> PW
    CRO --> XAI
    SEO --> PW
    SEO --> XAI
    ADS --> XAI
    ADS -.-> COMP

    style XAI fill:#4A90D9
    style ARCADE fill:#E91E63
    style PW fill:#FF9800
    style COMP fill:#9E9E9E
```

Solid lines = actively used. Dashed lines = planned (requires API key).

## File Reference

| File | Lines | Purpose |
|------|------:|---------|
| `agents/base.py` | ~70 | BaseAgent ABC, ToolResult, ToolDefinition, ToolStatus |
| `agents/registry.py` | ~60 | AgentRegistry singleton |
| `agents/content/__init__.py` | ~200 | ContentAgent — 7 XAI-powered tools |
| `agents/strategy/__init__.py` | ~200 | StrategyAgent — 6 tools (product-context is local) |
| `agents/social/__init__.py` | ~120 | SocialAgent — 3 tools wrapping Arcade |
| `agents/cro/__init__.py` | ~150 | CroAgent — 8 tools (Playwright + XAI) |
| `agents/seo/__init__.py` | ~220 | SeoAgent — 5 tools (Playwright + XAI) |
| `agents/ads/__init__.py` | ~130 | AdsAgent — 3 tools (XAI + Composio) |
| `integrations/xai_int.py` | ~45 | XAI wrapper (OpenAI client → x.ai) |
| `integrations/arcade_int.py` | ~45 | Arcade wrapper (arcadepy SDK) |
| `integrations/playwright_int.py` | ~90 | Async Playwright browser manager |
| `integrations/composio_int.py` | ~25 | Composio stub |
| `context/session.py` | ~90 | SessionContext + ProductContext |
| `help/renderer.py` | ~110 | 3-level Rich help renderer |
| `tui/app.py` | ~190 | SocoApp REPL + AgentCompleter |
| `tui/components/command_processor.py` | ~100 | agent:tool parser + tokenizer |
