# POLLY — AI Marketing Platform for Financial Advisors

POLLY is a specialized AI marketing platform for financial product distribution. It helps financial advisors, product manufacturers, and distributors plan, create, and execute compliant marketing campaigns — with built-in MiFID II, PRIIPs, and FCA compliance guardrails.

![POLLY Demo](docs/demo_video.gif)

## Features

- **9 AI Agents, 54 Tools** — content, strategy, compliance, campaign, channels, social, CRO, SEO, ads
- **Compliance Built-In** — MiFID II, PRIIPs, FCA checks woven into every piece of content
- **Multi-Channel** — WhatsApp, Telegram, email, LinkedIn, X, Instagram, TikTok, CRM
- **RAG Document Search** — query financial product documents with natural language (95.8% accuracy)
- **Campaign Automation** — A/B testing, follow-ups, lead scoring, automated workflows
- **WYSIWYG Instructions Editor** — customize agent prompts per user with admin-controlled global defaults
- **Interactive Demo** — WhatsApp/Telegram device simulator with live scenario playback

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/predictivelabsai/ai-marketing.git
cd ai-marketing
cp .env.sample .env
# Edit .env — minimum: XAI_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the web app
python web/app.py          # FastHTML on port 5055

# Or launch the CLI
python polly.py            # Interactive REPL
```

## Web App Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page with feature cards |
| About | `/about` | Personas, document workflow, channels |
| Demo | `/demo` | Interactive WhatsApp/Telegram simulator |
| Chat | `/chat` | Conversational AI interface (login required) |
| Profile | `/profile` | API integrations and 39 marketing skills |
| Instructions | `/instructions` | WYSIWYG prompt editor per agent |
| Guide | `/guide` | Screenshot-based user guide |
| Login | `/signin` | Email + password authentication |
| Register | `/register` | Create account |

## Agents

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

## CLI Usage

```bash
# Interactive REPL
python polly.py

# Inside the REPL:
polly> help                                          # Show all agents
polly> content:faq product:"Gold-Linked Note"        # Generate FAQ
polly> content:teaser product:"FTSE Autocallable"    # Create teaser
polly> compliance:review content:"..."               # Check compliance
polly> campaign:create product:"Bond Fund"           # Create campaign
polly> campaign:warmup question:"Gold vs equities?"  # Test market appetite
polly> channels:report period:30d                    # Cross-channel report

# Single command mode
python polly.py test content:teaser product:"FTSE Autocallable"
```

## RAG Document Search

Vector search pipeline for querying financial product documents using natural language.

```bash
python tasks/create_rag.py                                    # Process docs → embeddings
python tests/query_docs.py -q "What is the XTCC Solar product?"  # Single query
python tests/query_docs.py                                    # Full evaluation
```

**Latest evaluation**: 8/8 passed, 95.8% accuracy, 0.818 mean similarity.

| Question | Score | Similarity |
|----------|-------|------------|
| What is the XTCC Solar structured product? | 1.0 | 0.810 |
| What is the maturity/term? | 1.0 | 0.837 |
| What currency denominations? | 1.0 | 0.842 |
| Principal protection level? | 1.0 | 0.803 |
| Who is the issuer? | 1.0 | 0.789 |
| Key risks? | 0.67 | 0.784 |
| What is the ISIN? | 1.0 | 0.813 |
| What are carbon credits? | 1.0 | 0.864 |

See [docs/rag_evaluation_report.md](docs/rag_evaluation_report.md) for detailed results with full answers and source citations.

## Compliance Workflow

1. Load product documents via `compliance:submit`
2. Review with `compliance:review`
3. Management approves via `compliance:approve`
4. Generate marketing content from approved docs
5. Execute campaigns with regulatory guardrails

## Architecture

```
Web App (FastHTML)        CLI (prompt_toolkit)
     │                         │
     └────── AgentRegistry ────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
 9 Agents    Integrations   Context
 (54 tools)  (XAI, Arcade,  (ProductContext,
              Playwright,    ComplianceDocSet,
              Composio)      PromptService)
                  │
            PostgreSQL
         ┌────────┼────────┐
      polly     polly_rag  polly.prompts
   (users,    (documents,  (editable
   products,   chunks,     system prompts
   campaigns)  embeddings) per user)
```

## Project Structure

```
polly/
├── polly.py                         # CLI entry point
├── web/app.py                       # FastHTML web app (port 5055)
├── agents/                          # 9 agent modules (54 tools)
│   ├── base.py                      # BaseAgent, ToolDefinition, ToolResult
│   ├── content/                     # FAQs, teasers, pitch decks
│   ├── strategy/                    # Market research, backtesting
│   ├── compliance/                  # MiFID/PRIIPs review, approvals
│   ├── campaign/                    # Campaigns, workflows, A/B testing
│   ├── channels/                    # Multi-channel analytics
│   ├── social/                      # X/LinkedIn/WhatsApp/Telegram
│   ├── cro/                         # Conversion optimization
│   ├── seo/                         # SEO audits, schema markup
│   └── ads/                         # Paid advertising
├── integrations/                    # XAI, Arcade, Playwright, Composio
├── context/session.py               # SessionContext, ComplianceDocSet
├── utils/
│   ├── auth.py                      # Bcrypt auth against polly.users
│   ├── db_pool.py                   # SQLAlchemy connection pool
│   └── prompt_service.py            # Editable prompt resolution
├── tasks/create_rag.py              # RAG document processing pipeline
├── tests/
│   ├── test_suite.py                # 52 tests, 135 assertions
│   ├── query_docs.py                # RAG evaluation (8 questions)
│   ├── capture_guide.py             # Screenshot capture (17 images)
│   └── capture_video.py             # Demo video capture (22 frames)
├── sql/                             # PostgreSQL migrations
│   ├── create_schema.sql            # polly schema (10 tables)
│   ├── 002_add_prompts.sql          # polly.prompts table
│   └── 003_create_rag_schema.sql    # polly_rag schema (pgvector)
├── doc-data/                        # Source financial documents
├── docs/
│   ├── demo_video.mp4               # 33s product demo
│   ├── demo_video.gif               # Animated demo for README
│   ├── POLLY_Platform_Overview.pptx # 16-slide presentation
│   ├── rag_evaluation_report.md     # RAG accuracy report
│   └── architecture_readme.md       # Mermaid.js diagrams
└── static/guide/                    # 17 auto-captured screenshots
```

## Configuration

Copy `.env.sample` to `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `XAI_API_KEY` | Yes | XAI/Grok API key |
| `XAI_MODEL` | No | Model name (default: `grok-3`) |
| `DB_URL` | For web/RAG | PostgreSQL connection string |
| `ARCADE_API_KEY` | For social | Arcade.dev API key |
| `COMPOSIO_API_KEY` | No | CRM/channel integrations |
| `SESSION_SECRET` | No | Cookie signing key |

## Regenerating Assets

```bash
# Screenshots (17 images for /guide page)
python tests/capture_guide.py --start-app

# Demo video (33s MP4 + GIF)
python tests/capture_video.py --start-app

# PowerPoint deck (16 slides)
python docs/generate_pptx.py

# RAG embeddings (934 chunks from 7 documents)
python tasks/create_rag.py
```

## License

Apache 2.0
