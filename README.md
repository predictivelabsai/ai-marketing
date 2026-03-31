# POLLY — AI Marketing CLI for Financial Advisors

POLLY is a specialized AI marketing assistant for financial product distribution. It helps financial advisors, product manufacturers, and distributors plan, create, and execute compliant marketing campaigns.

## Quick Start

```bash
# 1. Set up environment
cp .env.sample .env
# Edit .env with your XAI_API_KEY (minimum required)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch POLLY
python polly.py
```

## Agents (9 agents, 54 tools)

| Agent | Tools | Purpose |
|-------|------:|---------|
| **content** | 7 | FAQs, teasers, pitch decks, compliant copy |
| **strategy** | 6 | Market research, competitor analysis, backtesting |
| **compliance** | 6 | Document approval, regulatory review, MiFID/PRIIPs |
| **campaign** | 7 | Campaign lifecycle, workflows, A/B testing |
| **channels** | 9 | Multi-channel monitoring and analytics |
| **social** | 3 | Post to X/LinkedIn/WhatsApp/Telegram |
| **cro** | 8 | Conversion rate optimization |
| **seo** | 5 | SEO for financial content |
| **ads** | 3 | Paid advertising |

## Command Syntax

```
agent:tool key:value key:"multi word value"
```

## Usage Examples

```bash
# Interactive REPL
python polly.py

# Inside the REPL:
polly> help                                          # Show all agents
polly> help content                                  # Show content tools
polly> content:faq product:"Gold-Linked Note"        # Generate FAQ
polly> content:teaser product:"FTSE Autocallable"    # Create teaser
polly> compliance:review content:"..."               # Check compliance
polly> campaign:create product:"Bond Fund"           # Create campaign
polly> campaign:warmup question:"Gold vs equities?"  # Test market appetite
polly> channels:report period:30d                    # Cross-channel report
polly> strategy:backtesting product:"FTSE Note"      # Historical analysis

# Single command mode
python polly.py test content:teaser product:"FTSE Autocallable"
```

## Compliance Workflow

1. Load product documents via `compliance:submit`
2. Review with `compliance:review`
3. Management approves via `compliance:approve`
4. Generate marketing content from approved docs
5. Execute campaigns with regulatory guardrails

## Project Structure

```
polly/
├── polly.py                         # CLI entry point
├── tui_main.py                      # REPL launcher
├── tui/
│   ├── app.py                       # PollyApp — REPL, completer, routing
│   └── components/
│       └── command_processor.py     # agent:tool parser
├── agents/
│   ├── base.py                      # BaseAgent ABC, ToolResult, ToolDefinition
│   ├── registry.py                  # AgentRegistry singleton
│   ├── content/__init__.py          # ContentAgent (7 tools)
│   ├── strategy/__init__.py         # StrategyAgent (6 tools)
│   ├── compliance/__init__.py       # ComplianceAgent (6 tools)
│   ├── campaign/__init__.py         # CampaignAgent (7 tools)
│   ├── channels/__init__.py         # ChannelsAgent (9 tools)
│   ├── social/__init__.py           # SocialAgent (3 tools)
│   ├── cro/__init__.py              # CroAgent (8 tools)
│   ├── seo/__init__.py              # SeoAgent (5 tools)
│   └── ads/__init__.py              # AdsAgent (3 tools)
├── integrations/
│   ├── base.py                      # IntegrationBackend ABC
│   ├── xai_int.py                   # XAI/Grok (content generation)
│   ├── arcade_int.py                # Arcade.dev (social posting)
│   ├── playwright_int.py            # Playwright (page analysis)
│   └── composio_int.py              # Composio (CRM, channels)
├── context/
│   └── session.py                   # SessionContext, ComplianceDocSet, UserPersona
├── help/
│   └── renderer.py                  # Rich help renderer
└── docs/                            # Documentation
```

## Configuration

Copy `.env.sample` to `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `XAI_API_KEY` | Yes | XAI/Grok API key |
| `XAI_MODEL` | No | Model name (default: `grok-3`) |
| `ARCADE_API_KEY` | For social | Arcade.dev API key |
| `COMPOSIO_API_KEY` | No | CRM/channel integrations |

## License

Apache 2.0
