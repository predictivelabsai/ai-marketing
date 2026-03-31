# POLLY Architecture

This document provides visual architecture diagrams for the POLLY AI Marketing CLI, rendered using Mermaid.js.

---

## 1. High-Level Architecture

```mermaid
flowchart TB
    subgraph Entry["Entry Points"]
        CLI["polly.py\n(CLI Dispatcher)"]
        TUI["tui_main.py\n(Interactive REPL)"]
        WEB["web/app.py\n(FastHTML, port 5001)"]
    end

    CLI --> CP["Command Parser\n(parse_command)"]
    TUI --> CP
    WEB --> CP

    CP --> AR["AgentRegistry\n(Singleton)"]

    AR --> A1["content\nCopywriting, blog posts,\nemail sequences"]
    AR --> A2["strategy\nLaunch plans, GTM,\nproduct context"]
    AR --> A3["compliance\nRegulatory review,\ndoc approval"]
    AR --> A4["campaign\nCreation, workflows,\nA/B testing"]
    AR --> A5["channels\nMulti-channel analytics,\nresponse consolidation"]
    AR --> A6["social\nSocial media posting\nand scheduling"]
    AR --> A7["cro\nConversion rate\noptimization"]
    AR --> A8["seo\nSearch engine\noptimization"]
    AR --> A9["ads\nPaid advertising\nand creatives"]

    subgraph Integrations["Integration Backends"]
        XAI["XAI / Grok\n(LLM Content Generation)"]
        ARC["Arcade\n(Social Posting)"]
        PW["Playwright\n(Page Analysis)"]
        COMP["Composio\n(CRM / Channels Stub)"]
    end

    A1 & A2 & A3 & A4 & A5 & A6 & A7 & A8 & A9 --> Integrations

    Integrations --> OUT["Output\n(Rich Console / JSON / HTML)"]
```

---

## 2. Session Context Model

```mermaid
classDiagram
    class SessionContext {
        +ProductContext product
        +ComplianceDocSet compliance_docs
        +UserPersona persona
        +dict campaigns
        +dict scratch
        -dict _integrations
        +get_integration(name) Any
        +set_integration(name, client)
        +xai : property
        +arcade : property
        +playwright : property
        +composio : property
    }

    class ProductContext {
        +str company
        +str product
        +str audience
        +str tone
        +str industry
        +str website
        +list~str~ competitors
        +str value_proposition
        +str product_type
        +str jurisdiction
        +str target_market
        +str negative_target
        +str distribution_strategy
        +str risk_level
        +dict extra
        +is_set() bool
        +to_prompt_block() str
        +set_from_args(args) list
    }

    class ComplianceDocSet {
        +str product_description
        +str prospectus
        +str term_sheet
        +str terms_conditions
        +str priips
        +str mifid_disclosures
        +str faq
        +str teaser
        +str pitch_deck
        +str market_research
        +dict approved_docs
        +to_prompt_block() str
    }

    class UserPersona {
        <<enumeration>>
        MANAGEMENT
        SALES
        CAMPAIGN
    }

    class IntegrationBackend {
        <<abstract>>
        +str name
        +is_configured()* bool
        +status_label() str
    }

    SessionContext --> ProductContext : product
    SessionContext --> ComplianceDocSet : compliance_docs
    SessionContext --> UserPersona : persona
    SessionContext o-- IntegrationBackend : _integrations dict
```

---

## 3. Agent Execution Flow

```mermaid
sequenceDiagram
    actor User
    participant TUI as TUI / PollyApp
    participant CP as CommandProcessor<br>(parse_command)
    participant AR as AgentRegistry<br>(singleton)
    participant Agent as Agent<br>(BaseAgent subclass)
    participant XAI as Integration<br>(XAI / Grok)

    User->>TUI: polly> content:copywriting topic:"gold ETF"
    TUI->>CP: parse_command(raw_input)
    CP-->>TUI: ParsedCommand(agent="content", tool="copywriting", args={...})

    TUI->>AR: resolve("content:copywriting")
    AR-->>TUI: (ContentAgent, "copywriting")

    TUI->>Agent: execute("copywriting", args, SessionContext)

    Note over Agent: Check required params<br>Build system prompt from<br>ProductContext + ComplianceDocSet

    Agent->>XAI: generate(system_prompt, user_prompt, max_tokens)
    XAI-->>Agent: LLM response text

    Agent-->>TUI: ToolResult(status=SUCCESS, output="...")

    TUI->>User: Rich Console display<br>(formatted output + timing)
```

---

## 4. Compliance Document Workflow

```mermaid
flowchart TD
    START(["Author creates document"]) --> SUBMIT["compliance:submit\ndoc-type:teaser\ncontent:'...'"]

    SUBMIT --> PENDING["PENDING REVIEW\n(stored in ComplianceDocSet)"]

    PENDING --> REVIEW["compliance:review\ncontent:'...'\ntype:teaser"]

    REVIEW --> VERDICT{AI Verdict}

    VERDICT -->|PASS| APPROVE["compliance:approve\ndoc-type:teaser\n(management persona required)"]
    VERDICT -->|NEEDS REVISION| REVISE["Revise Content"]
    VERDICT -->|FAIL| REVISE

    REVISE --> SUBMIT

    APPROVE --> APPROVED["APPROVED\n(added to approved_docs dict)"]

    APPROVED --> DOCSET["compliance:document-set\nView all 10 document slots\nand approval status"]

    DOCSET --> READY(["Campaign Ready\nApproved docs feed into\ncontent generation prompts"])

    style PENDING fill:#fff3cd,stroke:#ffc107
    style APPROVED fill:#d4edda,stroke:#28a745
    style READY fill:#cce5ff,stroke:#007bff
```

---

## 5. Campaign Lifecycle

```mermaid
flowchart LR
    subgraph Phase1["Phase 1: Pre-Launch"]
        WARMUP["campaign:warmup\nMarket-testing poll"]
        POLL["Collect Responses\n(gauge interest)"]
    end

    subgraph Phase2["Phase 2: Preparation"]
        LOAD["Load Compliance Docs\n(ComplianceDocSet)"]
        COMPLY["compliance:review\nRegulatory check"]
    end

    subgraph Phase3["Phase 3: Launch"]
        CREATE["campaign:create\nDefine campaign brief"]
        WORKFLOW["campaign:workflow\nAutomation rules"]
        EXECUTE["Execute via Channels\n(CRM, Email, WhatsApp,\nTelegram, Social)"]
    end

    subgraph Phase4["Phase 4: Optimize"]
        MONITOR["campaign:monitor\nPerformance analytics"]
        FOLLOWUP["campaign:follow-up\nNon-responder nudges"]
        LEADS["campaign:leads\nLead qualification\nand prioritization"]
        ABTEST["campaign:ab-test\nOptimize messaging"]
    end

    WARMUP --> POLL
    POLL --> LOAD
    LOAD --> COMPLY
    COMPLY --> CREATE
    CREATE --> WORKFLOW
    WORKFLOW --> EXECUTE
    EXECUTE --> MONITOR
    MONITOR --> FOLLOWUP
    MONITOR --> LEADS
    MONITOR --> ABTEST
    FOLLOWUP --> MONITOR
    ABTEST --> EXECUTE
```

---

## 6. Multi-Channel Architecture

```mermaid
flowchart TD
    POLLY(["POLLY\nAI Marketing CLI\n9 agents | 54 tools"])

    subgraph DirectMessaging["Direct Messaging"]
        EMAIL["Email"]
        WA["WhatsApp"]
        TG["Telegram"]
    end

    subgraph SocialMedia["Social Media"]
        LI["LinkedIn"]
        TW["X / Twitter"]
        IG["Instagram"]
        TT["TikTok"]
    end

    subgraph DataSystems["Data Systems"]
        CRM["CRM\n(Pipeline & Leads)"]
    end

    POLLY <-->|"Send / Receive\n(Composio)"| EMAIL
    POLLY <-->|"Send / Receive\n(Composio)"| WA
    POLLY <-->|"Send / Receive\n(Composio)"| TG

    POLLY <-->|"Post / Analytics\n(Arcade + Composio)"| LI
    POLLY <-->|"Post / Analytics\n(Arcade + Composio)"| TW
    POLLY <-->|"Post / Analytics\n(Composio)"| IG
    POLLY <-->|"Post / Analytics\n(Composio)"| TT

    POLLY <-->|"Read / Write\n(Composio)"| CRM

    style POLLY fill:#4a90d9,stroke:#2c5f8a,color:#fff
    style EMAIL fill:#f5f5f5,stroke:#999
    style WA fill:#dcf8c6,stroke:#25d366
    style TG fill:#e3f2fd,stroke:#0088cc
    style LI fill:#e8f0fe,stroke:#0077b5
    style TW fill:#f5f5f5,stroke:#1da1f2
    style IG fill:#fce4ec,stroke:#e4405f
    style TT fill:#f5f5f5,stroke:#000
    style CRM fill:#fff3e0,stroke:#ff9800
```

---

## Reference: Agent-Tool Map

| Agent | Tools | Integration |
|---|---|---|
| **content** | copywriting, blog posts, email sequences, ad copy | XAI |
| **strategy** | launch plans, GTM, product context, competitive analysis | XAI |
| **compliance** | review, submit, approve, document-set, target-market, risk-warnings | XAI |
| **campaign** | create, warmup, workflow, monitor, follow-up, ab-test, leads | XAI |
| **channels** | report, email, whatsapp, telegram, instagram, twitter, tiktok, crm, compare | XAI, Composio |
| **social** | social media posting, scheduling | XAI, Arcade |
| **cro** | conversion rate optimization | XAI, Playwright |
| **seo** | search engine optimization | XAI, Playwright |
| **ads** | paid ad creation, budget optimization | XAI |

## Reference: Command Syntax

```
agent:tool key:value key:"multi word value"
```

Examples:
```
content:copywriting topic:"structured product teaser" tone:professional
compliance:review content:"Capital at risk..." type:teaser jurisdiction:UK
campaign:warmup question:"Gold or equities in H2?"
channels:report period:7d format:summary
```

## Reference: Class Hierarchy

```
BaseAgent (ABC)
  +-- get_tools() -> list[ToolDefinition]
  +-- execute(tool_name, args, context) -> ToolResult
  +-- resolve_tool(tool_name) -> ToolDefinition | None
  +-- get_completions() -> list[str]

AgentRegistry (Singleton)
  +-- register(agent)
  +-- resolve("agent:tool") -> (agent, tool_name)
  +-- all_agents() -> list[BaseAgent]

IntegrationBackend (ABC)
  +-- XaiIntegration     (XAI_API_KEY)
  +-- ArcadeIntegration  (ARCADE_API_KEY)
  +-- PlaywrightIntegration (always available)
  +-- ComposioIntegration (COMPOSIO_API_KEY)
```
