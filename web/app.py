"""POLLY — FastHTML Web App for Financial Advisors."""
from fasthtml.common import *

app, rt = fast_app(
    pico=False,
    hdrs=(
        Meta(charset="UTF-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Link(rel="icon", href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>"),
    ),
)


# ---------------------------------------------------------------------------
# Shared styles / layout helpers
# ---------------------------------------------------------------------------

BRAND_CSS = """
:root {
    --polly-primary: #6366f1;
    --polly-secondary: #06b6d4;
    --polly-accent: #f59e0b;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --bg-dark: #0f172a;
    --bg-card: #1e293b;
    --border: #334155;
    --text-primary: #ffffff;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg-dark);
    color: white;
}

a { color: var(--polly-primary); text-decoration: none; }
a:hover { text-decoration: underline; }
"""

NAV_CSS = """
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
}
.top-nav .logo {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--polly-primary), var(--polly-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.top-nav .nav-links { display: flex; gap: 1.5rem; }
.top-nav .nav-links a {
    color: var(--text-secondary);
    font-size: 0.9375rem;
    transition: color 0.2s;
}
.top-nav .nav-links a:hover, .top-nav .nav-links a.active {
    color: white;
    text-decoration: none;
}
"""


def Navbar(active=""):
    return Nav(
        Span("POLLY", cls="logo"),
        Div(
            A("Home", href="/", cls="active" if active == "home" else ""),
            A("About", href="/about", cls="active" if active == "about" else ""),
            A("Demo", href="/demo", cls="active" if active == "demo" else ""),
            cls="nav-links",
        ),
        cls="top-nav",
    )


# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------

HOME_CSS = """
.hero {
    text-align: center;
    padding: 6rem 2rem 4rem;
    max-width: 800px;
    margin: 0 auto;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, var(--polly-primary), var(--polly-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p {
    font-size: 1.25rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 2rem;
}
.hero-cta {
    display: inline-block;
    padding: 0.875rem 2rem;
    background: var(--polly-primary);
    color: white;
    border-radius: 12px;
    font-size: 1.125rem;
    font-weight: 600;
    transition: transform 0.2s, box-shadow 0.2s;
}
.hero-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    text-decoration: none;
    color: white;
}
.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem;
}
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    transition: border-color 0.2s;
}
.feature-card:hover { border-color: var(--polly-primary); }
.feature-icon { font-size: 2rem; margin-bottom: 1rem; }
.feature-card h3 { font-size: 1.125rem; margin-bottom: 0.5rem; }
.feature-card p { font-size: 0.9375rem; color: var(--text-secondary); line-height: 1.5; }
"""


@rt("/")
def get():
    return Html(
        Head(
            Title("POLLY — AI Marketing for Financial Advisors"),
            Style(BRAND_CSS + NAV_CSS + HOME_CSS),
        ),
        Body(
            Navbar(active="home"),
            Section(
                H1("Your AI Marketing Team for Financial Products"),
                P(
                    "POLLY helps financial advisors and product distributors plan, create, "
                    "and execute compliant marketing campaigns across every channel."
                ),
                A("Try the Demo", href="/demo", cls="hero-cta"),
                cls="hero",
            ),
            Div(
                _feature("🛡️", "Compliance Built-In",
                         "MiFID II, PRIIPs, and FCA compliance checks woven into every piece of content. "
                         "Never worry about regulatory risk."),
                _feature("📱", "Multi-Channel Campaigns",
                         "Reach clients on WhatsApp, Telegram, email, LinkedIn, and more — "
                         "all from one conversation with POLLY."),
                _feature("📊", "Real-Time Analytics",
                         "Track opens, replies, and conversions across every channel. "
                         "POLLY tells you what's working and what to do next."),
                _feature("🚀", "Campaign Automation",
                         "Automated follow-ups, lead scoring, and A/B testing. "
                         "POLLY replaces 2-3 FTEs of campaign management."),
                _feature("📋", "Document Workflows",
                         "Submit, review, and approve product documents with four-eye checks. "
                         "Compliance-approved content drives every campaign."),
                _feature("🤖", "Natural Language Interface",
                         "Just tell POLLY what you need — in WhatsApp, Telegram, or the CLI. "
                         "No dashboards to learn, no buttons to find."),
                cls="features",
            ),
        ),
    )


def _feature(icon, title, desc):
    return Div(
        Div(icon, cls="feature-icon"),
        H3(title),
        P(desc),
        cls="feature-card",
    )


# ---------------------------------------------------------------------------
# About page
# ---------------------------------------------------------------------------

ABOUT_CSS = """
.about-hero {
    text-align: center;
    padding: 5rem 2rem 3rem;
    max-width: 800px;
    margin: 0 auto;
}
.about-hero h1 {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
}
.about-hero .subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.about-section {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 2rem 4rem;
}

.about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 3rem;
}

@media (max-width: 768px) {
    .about-grid { grid-template-columns: 1fr; }
}

.about-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
}
.about-card h3 {
    font-size: 1.125rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.about-card p, .about-card li {
    font-size: 0.9375rem;
    color: var(--text-secondary);
    line-height: 1.6;
}
.about-card ul {
    list-style: none;
    padding: 0;
}
.about-card li {
    padding: 0.375rem 0;
    padding-left: 1.5rem;
    position: relative;
}
.about-card li::before {
    content: '→';
    position: absolute;
    left: 0;
    color: var(--polly-primary);
}

.persona-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-bottom: 3rem;
}

@media (max-width: 900px) {
    .persona-row { grid-template-columns: 1fr; }
}

.persona-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}
.persona-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    margin: 0 auto 1rem;
}
.persona-card h4 { font-size: 1rem; margin-bottom: 0.5rem; }
.persona-card p { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5; }

.doc-flow {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 3rem;
}
.doc-flow h3 {
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    text-align: center;
}
.flow-steps {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.flow-step {
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    white-space: nowrap;
}
.flow-arrow {
    color: var(--text-muted);
    font-size: 1.25rem;
}

.channel-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.channel-chip {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem;
    text-align: center;
    font-size: 0.875rem;
}
.channel-chip .ch-icon { font-size: 1.5rem; display: block; margin-bottom: 0.25rem; }

.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-bottom: 3rem;
}

@media (max-width: 768px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}
.stat-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--polly-primary), var(--polly-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

.section-heading {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
}
.section-subheading {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.cta-banner {
    background: linear-gradient(135deg, var(--polly-primary), var(--polly-secondary));
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
}
.cta-banner h2 { font-size: 1.75rem; margin-bottom: 0.75rem; }
.cta-banner p { font-size: 1.125rem; opacity: 0.9; margin-bottom: 1.5rem; }
.cta-banner a {
    display: inline-block;
    padding: 0.75rem 2rem;
    background: white;
    color: var(--polly-primary);
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    transition: transform 0.2s;
}
.cta-banner a:hover { transform: translateY(-2px); text-decoration: none; }
"""


@rt("/about")
def get():
    return Html(
        Head(
            Title("About POLLY — AI Marketing for Financial Advisors"),
            Style(BRAND_CSS + NAV_CSS + ABOUT_CSS),
        ),
        Body(
            Navbar(active="about"),

            # Hero
            Section(
                H1("About POLLY"),
                P(
                    "POLLY is your AI-powered marketing team built specifically for financial advisors "
                    "and product distributors. Compliant, multi-channel, always on.",
                    cls="subtitle",
                ),
                cls="about-hero",
            ),

            Div(
                # Stats
                Div(
                    _stat("9", "AI Agents"),
                    _stat("54", "Marketing Tools"),
                    _stat("7+", "Channels"),
                    _stat("24/7", "Always On"),
                    cls="stats-row",
                ),

                # What is POLLY
                Div("What is POLLY?", cls="section-heading"),
                Div(
                    Div(
                        H3("🤖 Sales & Marketing Support"),
                        P(
                            "POLLY's primary persona responds to instructions from your management team "
                            "via WhatsApp or Telegram. It creates campaigns, generates compliant content, "
                            "monitors responses across all channels, and provides real-time analytics — "
                            "replacing the work of 2-3 FTEs or contractors."
                        ),
                        cls="about-card",
                    ),
                    Div(
                        H3("🛡️ Compliance Guardian"),
                        P(
                            "POLLY's compliance persona receives all final versions of documents, "
                            "reviews content against MiFID II, PRIIPs, and FCA regulations, "
                            "and ensures every piece of marketing is fair, clear, and not misleading. "
                            "Management can approve documents with four-eye checks before they go live."
                        ),
                        cls="about-card",
                    ),
                    cls="about-grid",
                ),

                # Client Personas
                Div("Who Uses POLLY?", cls="section-heading"),
                Div(
                    _persona("👔", "var(--polly-primary)", "Management",
                             "Approves and finalises documentation. Authorises campaigns with four-eye checks. "
                             "Full oversight of compliance interactions."),
                    _persona("📞", "var(--polly-secondary)", "Sales Team",
                             "Main users for follow-up and post-campaign intelligence. "
                             "Authorise personal WhatsApp for response monitoring. Receive qualified leads."),
                    _persona("📣", "var(--polly-accent)", "Campaign Management",
                             "Drives campaign planning and execution. Defines target audiences, "
                             "channels, and timing. Monitors performance and optimises."),
                    cls="persona-row",
                ),

                # Document Workflow
                Div(
                    H3("Compliance Document Workflow"),
                    Div(
                        _flow_step("Product Docs"),
                        Span("→", cls="flow-arrow"),
                        _flow_step("Submit"),
                        Span("→", cls="flow-arrow"),
                        _flow_step("AI Review"),
                        Span("→", cls="flow-arrow"),
                        _flow_step("Management Approval"),
                        Span("→", cls="flow-arrow"),
                        _flow_step("Campaign Ready"),
                        cls="flow-steps",
                    ),
                    cls="doc-flow",
                ),

                # Model Data Elements
                Div("Compliance-Approved Document Set", cls="section-heading"),
                Div(
                    Div(
                        H3("📄 Product Foundation"),
                        Ul(
                            Li("Product Description"),
                            Li("Prospectus / Offering Document"),
                            Li("Term Sheet / Final Terms"),
                            Li("Terms & Conditions"),
                            Li("PRIIPs Key Information Document"),
                            Li("MiFID Disclosures"),
                        ),
                        cls="about-card",
                    ),
                    Div(
                        H3("📝 Marketing Materials"),
                        Ul(
                            Li("FAQ — generated from product docs"),
                            Li("Teaser — one-pager with risk warnings"),
                            Li("Pitch Deck — slide content for advisors"),
                            Li("Market Research — sector analysis"),
                            Li("Competitor Matrix — positioning"),
                            Li("Backtesting — historical performance"),
                        ),
                        cls="about-card",
                    ),
                    cls="about-grid",
                ),

                # Campaign Lifecycle
                Div("Campaign Lifecycle", cls="section-heading"),
                Div(
                    Div(
                        H3("🎯 Campaign Creation & Execution"),
                        Ul(
                            Li("Warmup campaigns to test market appetite before product launch"),
                            Li("AI-generated compliant copy for every channel"),
                            Li("A/B testing with statistical framework"),
                            Li("Automated workflows: FAQ responses, lead forwarding, follow-ups"),
                            Li("Calendly integration for interested leads"),
                        ),
                        cls="about-card",
                    ),
                    Div(
                        H3("📈 Monitoring & Intelligence"),
                        Ul(
                            Li("Cross-channel analytics consolidated in real-time"),
                            Li("Lead categorisation: hot, warm, questions, removal"),
                            Li("Automated follow-up for non-responders"),
                            Li("CRM integration for pipeline tracking"),
                            Li("GDPR removal requests flagged (compliance is CRM responsibility)"),
                        ),
                        cls="about-card",
                    ),
                    cls="about-grid",
                ),

                # Channels
                Div("Supported Channels", cls="section-heading"),
                Div(
                    _channel("💬", "WhatsApp"),
                    _channel("✈️", "Telegram"),
                    _channel("📧", "Email"),
                    _channel("💼", "LinkedIn"),
                    _channel("🐦", "X / Twitter"),
                    _channel("📸", "Instagram"),
                    _channel("🎵", "TikTok"),
                    _channel("📊", "CRM"),
                    cls="channel-grid",
                ),

                Br(), Br(),

                # CTA
                Div(
                    H2("Ready to meet POLLY?"),
                    P("See how POLLY handles campaigns, compliance, and channels in real-time."),
                    A("Try the Interactive Demo", href="/demo"),
                    cls="cta-banner",
                ),

                cls="about-section",
            ),
        ),
    )


def _stat(value, label):
    return Div(
        Div(value, cls="stat-value"),
        Div(label, cls="stat-label"),
        cls="stat-card",
    )


def _persona(icon, color, name, desc):
    return Div(
        Div(icon, cls="persona-icon", style=f"background: {color}20; border: 2px solid {color};"),
        H4(name),
        P(desc),
        cls="persona-card",
    )


def _flow_step(text):
    return Span(text, cls="flow-step")


def _channel(icon, name):
    return Div(Span(icon, cls="ch-icon"), name, cls="channel-chip")


# ---------------------------------------------------------------------------
# Demo page (converted from demo.html)
# ---------------------------------------------------------------------------

DEMO_CSS = """
body { overflow: hidden; }

.demo-container {
    display: flex;
    height: calc(100vh - 57px);
    max-width: 1600px;
    margin: 0 auto;
}

/* Left Panel: Device Simulator */
.device-panel {
    flex: 0 0 400px;
    background: var(--bg-card);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
}
.device-header {
    padding: 1rem;
    background: var(--bg-dark);
    border-bottom: 1px solid var(--border);
}
.device-header h2 {
    font-size: 1rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.device-selector { display: flex; gap: 0.5rem; margin-top: 0.75rem; }
.device-btn {
    flex: 1; padding: 0.5rem; border: none; border-radius: 8px;
    color: white; font-size: 0.875rem; cursor: pointer; transition: all 0.2s;
}
.device-btn.whatsapp { background: #075e54; }
.device-btn.whatsapp.active { background: #128c7e; box-shadow: 0 0 0 2px #25d366; }
.device-btn.telegram { background: #5682a3; }
.device-btn.telegram.active { background: #2b9fd1; box-shadow: 0 0 0 2px #3bc9f6; }

/* Phone Frame */
.phone-frame {
    flex: 1; padding: 2rem; display: flex;
    justify-content: center; align-items: center; background: var(--bg-dark);
}
.phone {
    width: 375px; height: 750px; border-radius: 40px; overflow: hidden;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8); position: relative;
    border: 8px solid var(--bg-card); display: flex; flex-direction: column;
}
.phone.whatsapp { background: #e5ddd5; }
.phone.telegram { background: #ffffff; }

.phone-header {
    height: 60px; display: flex; align-items: center;
    padding: 0 1rem; gap: 0.75rem; border-bottom: 1px solid rgba(0,0,0,0.1);
}
.phone.whatsapp .phone-header { background: #075e54; }
.phone.telegram .phone-header { background: #5682a3; }

.back-btn { width: 24px; height: 24px; color: white; }
.chat-avatar {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--polly-primary), var(--polly-secondary));
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-weight: 700; font-size: 1.25rem; color: white;
}
.chat-info { flex: 1; }
.chat-name { font-weight: 600; font-size: 1rem; color: white; }
.chat-status { font-size: 0.75rem; color: rgba(255,255,255,0.8); display: flex; align-items: center; gap: 0.25rem; }
.online-dot { width: 8px; height: 8px; background: #25d366; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Chat Area */
.chat-area {
    flex: 1; overflow-y: auto; padding: 1rem;
    display: flex; flex-direction: column; gap: 0.5rem;
}
.phone.whatsapp .chat-area {
    background: #e5ddd5;
    background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h100v100H0z' fill='%23e5ddd5'/%3E%3Cpath d='M0 0h100v100H0z' fill='none' stroke='%23d1d1d1' stroke-width='0.5' opacity='0.3'/%3E%3C/svg%3E");
}
.phone.telegram .chat-area { background: #ffffff; }

.message {
    max-width: 85%; padding: 0.75rem 1rem; border-radius: 12px;
    font-size: 0.9375rem; line-height: 1.4; position: relative;
    animation: messageIn 0.3s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
@keyframes messageIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

.message.incoming {
    background: #ffffff; color: #303030;
    align-self: flex-start; border-bottom-left-radius: 4px;
}
.phone.telegram .message.incoming { border: 1px solid #e0e0e0; }
.message.outgoing {
    background: #dcf8c6; color: #303030;
    align-self: flex-end; border-bottom-right-radius: 4px;
}
.phone.telegram .message.outgoing { background: #effdde; border: 1px solid #c5e8a8; }
.message-time { font-size: 0.6875rem; color: #667781; margin-top: 0.25rem; text-align: right; }

.typing-indicator {
    display: flex; gap: 0.25rem; padding: 1rem; align-self: flex-start;
    background: #ffffff; border-radius: 12px; border-bottom-left-radius: 4px;
}
.phone.telegram .typing-indicator { border: 1px solid #e0e0e0; }
.typing-indicator span {
    width: 8px; height: 8px; background: #667781;
    border-radius: 50%; animation: typing 1.4s infinite;
}
.typing-indicator span:nth-child(2){animation-delay:0.2s}
.typing-indicator span:nth-child(3){animation-delay:0.4s}
@keyframes typing { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-10px)} }

/* Input Area */
.input-area {
    height: 80px; padding: 0.75rem 1rem;
    display: flex; gap: 0.75rem; align-items: center;
}
.phone.whatsapp .input-area { background: #f0f0f0; }
.phone.telegram .input-area { background: #f4f4f5; }
.input-wrapper {
    flex: 1; background: white; border-radius: 24px;
    padding: 0.5rem 1rem; display: flex; align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.message-input {
    flex: 1; background: transparent; border: none;
    color: #303030; font-size: 1rem; outline: none;
}
.message-input::placeholder { color: #667781; }
.send-btn {
    width: 40px; height: 40px; background: var(--polly-primary);
    border: none; border-radius: 50%; color: white;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: transform 0.2s;
    box-shadow: 0 2px 8px rgba(99,102,241,0.4);
}
.send-btn:hover { transform: scale(1.1); }

/* Right Panel */
.control-panel {
    flex: 1; background: var(--bg-dark);
    display: flex; flex-direction: column; overflow: hidden;
}
.panel-tabs {
    display: flex; background: var(--bg-card);
    border-bottom: 1px solid var(--border);
}
.panel-tab {
    flex: 1; padding: 1rem; background: transparent; border: none;
    color: var(--text-secondary); font-size: 0.875rem; font-weight: 500;
    cursor: pointer; transition: all 0.2s; border-bottom: 2px solid transparent;
}
.panel-tab.active {
    color: white; border-bottom-color: var(--polly-primary); background: var(--bg-dark);
}
.panel-content { flex: 1; overflow-y: auto; padding: 1.5rem; }

/* Scenarios */
.scenario-section { margin-bottom: 2rem; }
.section-title {
    font-size: 0.75rem; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 0.75rem;
}
.scenario-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 0.75rem; }
.scenario-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem; cursor: pointer; transition: all 0.2s;
}
.scenario-card:hover { border-color: var(--polly-primary); background: #252f47; }
.scenario-card.active { border-color: var(--polly-primary); background: rgba(99,102,241,0.1); }
.scenario-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
.scenario-name { font-weight: 600; font-size: 0.875rem; margin-bottom: 0.25rem; }
.scenario-desc { font-size: 0.75rem; color: var(--text-muted); }

/* Quick Actions */
.quick-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.action-btn {
    padding: 0.5rem 1rem; background: var(--bg-card);
    border: 1px solid var(--border); border-radius: 20px;
    color: white; font-size: 0.875rem; cursor: pointer; transition: all 0.2s;
}
.action-btn:hover { background: var(--polly-primary); border-color: var(--polly-primary); }

/* Analytics Dashboard */
.analytics-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.metric-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem;
}
.metric-label {
    font-size: 0.75rem; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;
}
.metric-value { font-size: 1.75rem; font-weight: 700; color: white; }
.metric-change { font-size: 0.875rem; margin-top: 0.25rem; }
.metric-change.positive { color: var(--success); }

/* Chart */
.chart-container {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem; height: 300px; position: relative;
}
.chart-title { font-size: 1rem; font-weight: 600; margin-bottom: 1rem; }
.chart-area {
    height: calc(100% - 3rem); display: flex; align-items: flex-end;
    justify-content: space-around; gap: 0.5rem; padding: 0 1rem;
}
.chart-bar {
    flex: 1; border-radius: 4px 4px 0 0; min-height: 20px;
    transition: height 0.5s ease; position: relative;
}
.chart-bar:hover { opacity: 0.8; }
.chart-bar.wa-bar { background: #25d366; }
.chart-bar.tg-bar { background: #3bc9f6; }
.chart-bar.em-bar { background: var(--polly-primary); }
.chart-bar.li-bar { background: var(--polly-secondary); }
.chart-label {
    position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%);
    font-size: 0.75rem; color: var(--text-muted); white-space: nowrap;
}

/* Campaign Preview */
.campaign-preview {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem;
}
.campaign-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;
}
.campaign-title { font-size: 1.125rem; font-weight: 600; }
.campaign-status {
    padding: 0.25rem 0.75rem; background: rgba(16,185,129,0.2);
    color: var(--success); border-radius: 20px; font-size: 0.75rem; font-weight: 600;
}
.variant-tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.variant-tab {
    padding: 0.5rem 1rem; background: transparent;
    border: 1px solid var(--border); border-radius: 8px;
    color: var(--text-secondary); font-size: 0.875rem; cursor: pointer;
}
.variant-tab.active {
    background: var(--polly-primary); border-color: var(--polly-primary); color: white;
}
.variant-content {
    background: var(--bg-dark); border-radius: 8px; padding: 1rem;
    font-size: 0.9375rem; line-height: 1.5; margin-bottom: 1rem;
}
.variant-metrics { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; }
.variant-metric { text-align: center; }
.variant-metric-value { font-size: 1.25rem; font-weight: 700; color: white; }
.variant-metric-label { font-size: 0.75rem; color: var(--text-muted); }

/* Campaign Cards in Chat */
.message.campaign-card {
    background: white; border: 1px solid #e0e0e0; width: 100%; color: #303030;
}
.campaign-card-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;
}
.campaign-card-title { font-weight: 600; color: var(--polly-primary); }
.campaign-card-badge {
    padding: 0.25rem 0.5rem; background: rgba(245,158,11,0.2);
    color: var(--polly-accent); border-radius: 4px; font-size: 0.75rem;
}
.campaign-card-preview {
    background: #f5f5f5; border-radius: 8px; padding: 0.75rem;
    margin-bottom: 0.75rem; font-size: 0.875rem;
}
.campaign-card-actions { display: flex; gap: 0.5rem; }
.campaign-btn {
    flex: 1; padding: 0.5rem; border: none; border-radius: 6px;
    font-size: 0.875rem; cursor: pointer; transition: all 0.2s;
}
.campaign-btn.primary { background: var(--polly-primary); color: white; }
.campaign-btn.secondary { background: transparent; border: 1px solid #ddd; color: #303030; }

.message.insight-card { background: white; border: 1px solid #e0e0e0; color: #303030; }
.insight-header {
    display: flex; align-items: center; gap: 0.5rem;
    margin-bottom: 0.75rem; color: var(--success); font-weight: 600;
}
.insight-list { list-style: none; }
.insight-list li {
    padding: 0.5rem 0; border-bottom: 1px solid #e0e0e0;
    display: flex; justify-content: space-between; align-items: center;
}
.insight-list li:last-child { border-bottom: none; }
.insight-name { font-size: 0.875rem; }
.insight-value { font-weight: 600; color: var(--polly-secondary); }

.platform-indicator {
    position: absolute; top: 12px; right: 12px; padding: 0.25rem 0.75rem;
    border-radius: 12px; font-size: 0.75rem; font-weight: 600; color: white;
}
.platform-indicator.whatsapp { background: #25d366; }
.platform-indicator.telegram { background: #3bc9f6; }

/* Toast */
.toast-container {
    position: fixed; top: 2rem; right: 2rem; z-index: 1000;
    display: flex; flex-direction: column; gap: 0.75rem;
}
.toast {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.5rem;
    display: flex; align-items: center; gap: 0.75rem;
    animation: slideIn 0.3s ease;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
@keyframes slideIn { from{transform:translateX(100%);opacity:0} to{transform:translateX(0);opacity:1} }
.toast-icon { font-size: 1.25rem; }
.toast-content { flex: 1; }
.toast-title { font-weight: 600; font-size: 0.9375rem; }
.toast-message { font-size: 0.875rem; color: var(--text-secondary); }

/* Responsive */
@media (max-width: 1200px) {
    .demo-container { flex-direction: column; }
    .device-panel { flex: 0 0 auto; height: 50vh; border-right: none; border-bottom: 1px solid var(--border); }
    .phone { transform: scale(0.8); }
}
"""

DEMO_JS = """
let currentDevice = 'whatsapp';
let currentScenario = null;
let campaigns = [];

const scenarios = {
    'campaign-creation': {
        icon: '🚀', name: 'Create Campaign',
        desc: 'Launch follow-up campaign with AI copy',
        steps: [
            { type: 'user', text: "Create a follow-up for people who opened last week's offer but didn't buy" },
            { type: 'typing', duration: 2000 },
            { type: 'campaign', data: {
                title: 'High-Intent Follow-Up',
                segment: '200 contacts (opened, no purchase)',
                variants: [
                    { type: 'Urgency', text: '⏰ Only 24 hours left... Your exclusive offer expires at midnight. Don\\'t miss out on 20% off.', predicted: '12% open rate' },
                    { type: 'Social Proof', text: '🔥 Join 500+ customers who chose [Product] this month. Your peers are already seeing results.', predicted: '15% open rate' },
                    { type: 'Exclusivity', text: '✨ Just for you: VIP early access ending soon. This price won\\'t be available to the general public.', predicted: '18% open rate' }
                ]
            }}
        ]
    },
    'customer-insights': {
        icon: '🔍', name: 'Get Insights',
        desc: 'Ask natural language questions about your data',
        steps: [
            { type: 'user', text: 'Who are my best customers this quarter?' },
            { type: 'typing', duration: 2500 },
            { type: 'insight', data: {
                title: 'Q1 2026 Top Customers',
                insights: [
                    { name: 'Acme Corp', value: '$15,420 spent' },
                    { name: 'TechStart Inc', value: '$12,890 spent' },
                    { name: 'BuildIt LLC', value: '$8,340 spent' },
                    { name: 'CloudFirst', value: '$7,120 spent' }
                ],
                pattern: 'All SaaS companies, renewed early, high engagement'
            }}
        ]
    },
    'missed-followups': {
        icon: '⚡', name: 'Recover Leads',
        desc: 'Find and re-engage forgotten contacts',
        steps: [
            { type: 'user', text: "Find leads I haven't followed up with in 3 months" },
            { type: 'typing', duration: 1800 },
            { type: 'polly', text: 'Found 15 contacts with no activity in 90+ days. 8 have engaged with recent content. 3 asked about pricing before going quiet.' },
            { type: 'typing', duration: 1500 },
            { type: 'campaign', data: {
                title: 'Re-engagement Campaign',
                segment: '15 dormant leads',
                variants: [
                    { type: 'Soft Touch', text: 'Hey [Name], noticed you checked out our latest update. Still exploring solutions for [Pain Point]?', predicted: '22% reply rate' }
                ]
            }}
        ]
    },
    'analytics-query': {
        icon: '📊', name: 'Check Performance',
        desc: 'Get instant campaign analytics',
        steps: [
            { type: 'user', text: "How did yesterday's campaign perform?" },
            { type: 'typing', duration: 1200 },
            { type: 'polly', text: "Yesterday's \\"Product Launch\\" campaign results:\\n\\n📤 Sent: 450\\n📖 Opened: 287 (64%)\\n👆 Clicked: 89 (20%)\\n💬 Replied: 34 (8%)\\n🎯 Converted: 12 (3%)\\n\\nBest performing channel: WhatsApp (72% open rate)\\nBest variant: \\"Exclusivity\\" (+23% vs others)" }
        ]
    }
};

document.addEventListener('DOMContentLoaded', () => {
    showToast('Demo Ready', 'Select a scenario or type your own message to POLLY', '👋');
});

function switchDevice(device) {
    currentDevice = device;
    document.querySelectorAll('.device-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.device-btn.' + device).forEach(btn => btn.classList.add('active'));
    const phone = document.getElementById('phone');
    const badge = document.getElementById('platform-badge');
    phone.className = 'phone ' + device;
    badge.className = 'platform-indicator ' + device;
    badge.textContent = device === 'whatsapp' ? 'WhatsApp' : 'Telegram';
    showToast('Device Switched', 'Now simulating ' + device, device === 'whatsapp' ? '💚' : '💙');
}

function switchTab(tab) {
    document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    const content = document.getElementById('panel-content');
    if (tab === 'scenarios') renderScenarioPanel();
    else if (tab === 'analytics') renderAnalyticsPanel();
    else if (tab === 'campaign') renderCampaignPanel();
}

function renderScenarioPanel() {
    const content = document.getElementById('panel-content');
    let html = '<div class="scenario-section"><div class="section-title">Choose a Demo Scenario</div><div class="scenario-grid">';
    for (const [key, s] of Object.entries(scenarios)) {
        html += '<div class="scenario-card ' + (currentScenario===key?'active':'') + '" onclick="runScenario(\\'' + key + '\\')">' +
            '<div class="scenario-icon">' + s.icon + '</div>' +
            '<div class="scenario-name">' + s.name + '</div>' +
            '<div class="scenario-desc">' + s.desc + '</div></div>';
    }
    html += '</div></div>';
    html += '<div class="scenario-section"><div class="section-title">Or Try These Quick Actions</div><div class="quick-actions">';
    ['Show warm leads','Referral campaign','Channel comparison','Daily priority'].forEach(a => {
        html += '<button class="action-btn" onclick="quickAction(\\'' + a.replace(/'/g,"\\\\'") + '\\')">' + a + '</button>';
    });
    html += '</div></div>';
    html += '<div class="scenario-section"><div class="section-title">Tips</div>' +
        '<p style="color:#64748b;font-size:0.875rem;line-height:1.6">' +
        '• Type naturally — POLLY understands context<br>' +
        '• Use voice notes for quick inputs<br>' +
        '• Forward any message to POLLY for instant analysis<br>' +
        '• Ask "Why?" to get reasoning behind recommendations</p></div>';
    content.innerHTML = html;
}

function renderAnalyticsPanel() {
    document.getElementById('panel-content').innerHTML =
        '<div class="analytics-grid">' +
        '<div class="metric-card"><div class="metric-label">Active Campaigns</div><div class="metric-value">3</div><div class="metric-change positive">+1 this week</div></div>' +
        '<div class="metric-card"><div class="metric-label">Total Reach</div><div class="metric-value">2,847</div><div class="metric-change positive">+12% vs last week</div></div>' +
        '<div class="metric-card"><div class="metric-label">Response Rate</div><div class="metric-value">18.4%</div><div class="metric-change positive">+3.2% vs benchmark</div></div>' +
        '</div>' +
        '<div class="chart-container"><div class="chart-title">Channel Performance (Last 30 Days)</div>' +
        '<div class="chart-area">' +
        '<div class="chart-bar wa-bar" style="height:85%"><span class="chart-label">WhatsApp</span></div>' +
        '<div class="chart-bar tg-bar" style="height:62%"><span class="chart-label">Telegram</span></div>' +
        '<div class="chart-bar em-bar" style="height:45%"><span class="chart-label">Email</span></div>' +
        '<div class="chart-bar li-bar" style="height:38%"><span class="chart-label">LinkedIn</span></div>' +
        '</div></div>' +
        '<div style="margin-top:1.5rem;background:#1e293b;border-radius:12px;padding:1rem">' +
        '<div style="font-size:0.875rem;color:#64748b;margin-bottom:0.5rem">AI Recommendation</div>' +
        '<div style="font-size:0.9375rem">📈 <strong>Shift 20% of email volume to WhatsApp</strong> — projected +15% overall response rate based on your audience behavior.</div></div>';
}

function renderCampaignPanel() {
    document.getElementById('panel-content').innerHTML =
        '<div class="campaign-preview">' +
        '<div class="campaign-header"><div class="campaign-title">Spring Follow-Up Campaign</div><div class="campaign-status">Active</div></div>' +
        '<div style="font-size:0.875rem;color:#64748b;margin-bottom:1rem">Target: 200 contacts • Started: Mar 24 • Channel: WhatsApp + Email</div>' +
        '<div class="variant-tabs"><button class="variant-tab active" onclick="switchVariant(0)">Variant A</button><button class="variant-tab" onclick="switchVariant(1)">Variant B</button><button class="variant-tab" onclick="switchVariant(2)">Variant C</button></div>' +
        '<div class="variant-content" id="variant-content"><strong>Urgency Angle:</strong><br><br>⏰ Only 24 hours left... Your exclusive offer expires at midnight. Don\\'t miss out on 20% off — this is your final reminder.</div>' +
        '<div class="variant-metrics"><div class="variant-metric"><div class="variant-metric-value">12%</div><div class="variant-metric-label">Open Rate</div></div>' +
        '<div class="variant-metric"><div class="variant-metric-value">4.2%</div><div class="variant-metric-label">Click Rate</div></div>' +
        '<div class="variant-metric"><div class="variant-metric-value">2.1%</div><div class="variant-metric-label">Conversion</div></div></div></div>' +
        '<div style="margin-top:1.5rem;display:grid;grid-template-columns:repeat(2,1fr);gap:1rem">' +
        '<div style="background:#1e293b;border-radius:12px;padding:1rem"><div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;margin-bottom:0.5rem">Best Performer</div><div style="font-size:1.125rem;font-weight:600;color:var(--success)">Variant C (+40%)</div><div style="font-size:0.875rem;color:#64748b;margin-top:0.25rem">Exclusivity angle wins</div></div>' +
        '<div style="background:#1e293b;border-radius:12px;padding:1rem"><div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;margin-bottom:0.5rem">Next Action</div><div style="font-size:1.125rem;font-weight:600">Send Variant C</div><div style="font-size:0.875rem;color:#64748b;margin-top:0.25rem">to non-responders</div></div></div>';
}

async function runScenario(key) {
    currentScenario = key;
    const scenario = scenarios[key];
    document.querySelectorAll('.scenario-card').forEach(c => c.classList.remove('active'));
    event.currentTarget.classList.add('active');
    document.getElementById('chat-area').innerHTML = '';
    for (const step of scenario.steps) {
        switch(step.type) {
            case 'user': addMessage('user', step.text); break;
            case 'typing': showTyping(); await sleep(step.duration); hideTyping(); break;
            case 'polly': addMessage('polly', step.text); break;
            case 'campaign': addCampaignCard(step.data); break;
            case 'insight': addInsightCard(step.data); break;
        }
        await sleep(500);
    }
    showToast('Scenario Complete', 'Try another or type your own message', '✨');
}

function quickAction(text) {
    document.getElementById('message-input').value = text;
    sendMessage();
}

function addMessage(sender, text) {
    const area = document.getElementById('chat-area');
    const div = document.createElement('div');
    div.className = 'message ' + (sender==='user' ? 'outgoing' : 'incoming');
    const time = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    div.innerHTML = text.replace(/\\n/g, '<br>') + '<div class="message-time">' + time + '</div>';
    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
}

function addCampaignCard(data) {
    const area = document.getElementById('chat-area');
    const div = document.createElement('div');
    div.className = 'message incoming campaign-card';
    div.innerHTML =
        '<div class="campaign-card-header"><div class="campaign-card-title">📊 ' + data.title + '</div><div class="campaign-card-badge">' + data.segment + '</div></div>' +
        '<div class="campaign-card-preview"><strong>Variant A (' + data.variants[0].type + '):</strong><br>' + data.variants[0].text + '<br><br><em>Predicted: ' + data.variants[0].predicted + '</em></div>' +
        '<div class="campaign-card-actions"><button class="campaign-btn primary" onclick="approveCampaign()">✓ Approve & Send</button><button class="campaign-btn secondary" onclick="showVariants(' + data.variants.length + ')">See all variants</button></div>';
    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
    campaigns.push(data);
}

function addInsightCard(data) {
    const area = document.getElementById('chat-area');
    const div = document.createElement('div');
    div.className = 'message incoming insight-card';
    div.innerHTML =
        '<div class="insight-header"><span>📈</span><span>' + data.title + '</span></div>' +
        '<ul class="insight-list">' + data.insights.map(i => '<li><span class="insight-name">' + i.name + '</span><span class="insight-value">' + i.value + '</span></li>').join('') + '</ul>' +
        '<div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #e0e0e0;font-size:0.875rem;color:#64748b">💡 Pattern detected: ' + data.pattern + '</div>';
    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
}

function showTyping() {
    const area = document.getElementById('chat-area');
    const div = document.createElement('div');
    div.className = 'typing-indicator'; div.id = 'typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
}
function hideTyping() { const t = document.getElementById('typing-indicator'); if(t) t.remove(); }

function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    if (!text) return;
    addMessage('user', text);
    input.value = '';
    setTimeout(() => {
        showTyping();
        setTimeout(() => {
            hideTyping();
            const lower = text.toLowerCase();
            if (lower.includes('campaign') || lower.includes('follow up')) {
                addCampaignCard({ title: 'Smart Follow-Up', segment: '150 high-intent contacts',
                    variants: [{ type: 'Personalized', text: "Hey [Name], noticed you checked out [Product]. Quick question: what's your biggest priority this quarter?", predicted: '25% reply rate' }] });
            } else if (lower.includes('best customer') || lower.includes('top') || lower.includes('warm')) {
                addInsightCard({ title: 'Customer Intelligence',
                    insights: [{ name: 'Sarah Chen', value: '$24,500 LTV' },{ name: 'Mike Ross', value: '18 referrals' },{ name: 'Emma Davis', value: 'Fastest responder' }],
                    pattern: 'Top customers engage within 2 hours of campaign send' });
            } else if (lower.includes('performance') || lower.includes('how did') || lower.includes('comparison') || lower.includes('compare')) {
                addMessage('polly', 'Recent performance snapshot:\\n\\n📊 Last 7 days:\\n• 3 campaigns sent\\n• 1,247 people reached\\n• 234 responses (18.8%)\\n• 47 meetings booked\\n• $12,400 attributed revenue\\n\\nTop channel: WhatsApp (72% open rate)\\nBest time: Tuesday 10 AM');
            } else {
                addMessage('polly', "I can help with that! Here are some things I can do:\\n\\n• Create campaigns with AI-generated copy\\n• Find and rank your best leads\\n• Track responses across all channels\\n• Analyze what's working (and what's not)\\n• Suggest next best actions\\n\\nWhat would you like to focus on?");
            }
        }, 2000);
    }, 500);
}

function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

function approveCampaign() {
    showToast('Campaign Approved', 'Scheduling for optimal send time...', '🚀');
    setTimeout(() => {
        addMessage('polly', "✅ Campaign scheduled! 150 messages will be sent Tuesday at 10 AM (optimal for your audience). I'll track responses and update you with results.");
    }, 1500);
}
function showVariants(count) { showToast('Variants', 'Showing all ' + count + ' copy variants with predicted performance...', '📝'); }

function switchVariant(index) {
    document.querySelectorAll('.variant-tab').forEach((t,i) => t.classList.toggle('active', i===index));
    const variants = [
        "⏰ Only 24 hours left... Your exclusive offer expires at midnight. Don't miss out on 20% off.",
        "🔥 Join 500+ customers who chose us this month. Your peers are already seeing results — here's how.",
        "✨ Just for you: VIP early access ending soon. This price won't be available to the general public."
    ];
    const types = ['Urgency','Social Proof','Exclusivity'];
    const metrics = [{open:'12%',click:'4.2%',conv:'2.1%'},{open:'15%',click:'5.8%',conv:'2.9%'},{open:'18%',click:'7.2%',conv:'3.4%'}];
    document.getElementById('variant-content').innerHTML = '<strong>' + types[index] + ' Angle:</strong><br><br>' + variants[index];
    const els = document.querySelectorAll('.variant-metric-value');
    els[0].textContent = metrics[index].open;
    els[1].textContent = metrics[index].click;
    els[2].textContent = metrics[index].conv;
}

function showToast(title, message, icon) {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = 'toast';
    t.innerHTML = '<div class="toast-icon">' + icon + '</div><div class="toast-content"><div class="toast-title">' + title + '</div><div class="toast-message">' + message + '</div></div>';
    c.appendChild(t);
    setTimeout(() => { t.style.animation = 'slideIn 0.3s ease reverse'; setTimeout(() => t.remove(), 300); }, 4000);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
"""


@rt("/demo")
def get():
    return Html(
        Head(
            Title("POLLY - Interactive Demo"),
            Style(BRAND_CSS + NAV_CSS + DEMO_CSS),
        ),
        Body(
            Navbar(active="demo"),
            Div(
                # Left: Device Simulator
                Div(
                    Div(
                        H2("Device Simulator"),
                        Div(
                            Button("WhatsApp", cls="device-btn whatsapp active", onclick="switchDevice('whatsapp')"),
                            Button("Telegram", cls="device-btn telegram", onclick="switchDevice('telegram')"),
                            cls="device-selector",
                        ),
                        cls="device-header",
                    ),
                    Div(
                        Div(
                            Div("WhatsApp", id="platform-badge", cls="platform-indicator whatsapp"),
                            # Phone header
                            Div(
                                NotStr('<svg class="back-btn" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>'),
                                Div("P", cls="chat-avatar"),
                                Div(
                                    Div("POLLY", cls="chat-name"),
                                    Div(Span(cls="online-dot"), " Online now", cls="chat-status"),
                                    cls="chat-info",
                                ),
                                cls="phone-header",
                            ),
                            # Chat area
                            Div(
                                Div(
                                    NotStr("Hi! I'm POLLY, your AI marketing team. I can help you:<br><br>"
                                           "• Create campaigns in minutes<br>"
                                           "• Find your best customers<br>"
                                           "• Track responses across all channels<br>"
                                           "• Never miss a follow-up<br><br>"
                                           "What would you like to do today?"),
                                    Div("03:58 PM", cls="message-time"),
                                    cls="message incoming",
                                ),
                                id="chat-area", cls="chat-area",
                            ),
                            # Input
                            Div(
                                Div(
                                    Input(type="text", cls="message-input", id="message-input",
                                          placeholder="Message POLLY...", onkeypress="handleKeyPress(event)"),
                                    cls="input-wrapper",
                                ),
                                Button(
                                    NotStr('<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
                                           '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>'),
                                    cls="send-btn", onclick="sendMessage()",
                                ),
                                cls="input-area",
                            ),
                            id="phone", cls="phone whatsapp",
                        ),
                        cls="phone-frame",
                    ),
                    cls="device-panel",
                ),
                # Right: Control Panel
                Div(
                    Div(
                        Button("Demo Scenarios", cls="panel-tab active", onclick="switchTab('scenarios')"),
                        Button("Live Analytics", cls="panel-tab", onclick="switchTab('analytics')"),
                        Button("Campaign Preview", cls="panel-tab", onclick="switchTab('campaign')"),
                        cls="panel-tabs",
                    ),
                    Div(
                        # Scenarios (default view)
                        Div(
                            Div("Choose a Demo Scenario", cls="section-title"),
                            Div(
                                *[_scenario_card(key, s) for key, s in [
                                    ("campaign-creation", {"icon": "🚀", "name": "Create Campaign", "desc": "Launch follow-up campaign with AI copy"}),
                                    ("customer-insights", {"icon": "🔍", "name": "Get Insights", "desc": "Ask natural language questions about your data"}),
                                    ("missed-followups", {"icon": "⚡", "name": "Recover Leads", "desc": "Find and re-engage forgotten contacts"}),
                                    ("analytics-query", {"icon": "📊", "name": "Check Performance", "desc": "Get instant campaign analytics"}),
                                ]],
                                cls="scenario-grid",
                            ),
                            cls="scenario-section",
                        ),
                        Div(
                            Div("Or Try These Quick Actions", cls="section-title"),
                            Div(
                                Button("Show warm leads", cls="action-btn", onclick="quickAction('Show me my warmest leads')"),
                                Button("Referral campaign", cls="action-btn", onclick="quickAction('Draft a referral campaign')"),
                                Button("Channel comparison", cls="action-btn", onclick="quickAction('Compare email vs WhatsApp performance')"),
                                Button("Daily priority", cls="action-btn", onclick="quickAction('What should I do today?')"),
                                cls="quick-actions",
                            ),
                            cls="scenario-section",
                        ),
                        Div(
                            Div("Tips", cls="section-title"),
                            P(
                                NotStr(
                                    "• Type naturally — POLLY understands context<br>"
                                    "• Use voice notes for quick inputs<br>"
                                    "• Forward any message to POLLY for instant analysis<br>"
                                    '• Ask "Why?" to get reasoning behind recommendations'
                                ),
                                style="color: #64748b; font-size: 0.875rem; line-height: 1.6;",
                            ),
                            cls="scenario-section",
                        ),
                        id="panel-content", cls="panel-content",
                    ),
                    cls="control-panel",
                ),
                cls="demo-container",
            ),
            # Toast container
            Div(id="toast-container", cls="toast-container"),
            Script(DEMO_JS),
        ),
    )


def _scenario_card(key, s):
    return Div(
        Div(s["icon"], cls="scenario-icon"),
        Div(s["name"], cls="scenario-name"),
        Div(s["desc"], cls="scenario-desc"),
        cls="scenario-card",
        onclick=f"runScenario('{key}')",
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

serve(port=5001)
