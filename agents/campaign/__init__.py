"""Campaign agent — Campaign creation, workflows, monitoring, and follow-up for financial product marketing."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are POLLY Campaign Manager, an AI campaign management assistant for financial product marketing. "
    f"Today's date is {date.today()}. You help plan, execute, and monitor marketing campaigns "
    "for financial products while ensuring compliance with financial marketing regulations."
)


class CampaignAgent(BaseAgent):
    name = "campaign"
    description = "Campaign creation, workflows, monitoring, A/B testing"

    def _get_default_prompt(self) -> str:
        return SYSTEM_PROMPT_BASE

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="create",
                description="Create a new marketing campaign",
                long_help="Define a new marketing campaign with target audience, channels, timing, "
                          "messaging, and compliance requirements. Generates a campaign brief "
                          "including all parameters needed for execution.",
                aliases=["new"],
                examples=[
                    'campaign:create product:"Gold-Linked Note" audience:"HNW investors" channels:"email,whatsapp"',
                    'campaign:create type:warmup topic:"Gold vs Equities outlook"',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Financial product to campaign for", "required": False},
                    "audience": {"description": "Target audience description", "required": False},
                    "channels": {"description": "Comma-separated channels (email,whatsapp,telegram,linkedin,x,instagram,tiktok)", "required": False, "default": "email"},
                    "type": {"description": "Campaign type", "required": False, "default": "product",
                             "options": ["product", "warmup", "poll", "follow-up", "reactivation"]},
                    "topic": {"description": "Campaign topic or question (for warmup/poll types)", "required": False},
                    "duration": {"description": "Campaign duration (e.g. 2w, 1m)", "required": False, "default": "2w"},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="warmup",
                description="Create a market-testing warmup campaign",
                long_help="Create a lightweight warmup campaign to test market appetite. "
                          "Can be a simple poll, market question, or general interest gauge "
                          "before committing to a full product campaign. Per POLLY spec: "
                          "'Not all documents have to be completed to begin the marketing process.'",
                aliases=["poll", "test-market"],
                examples=[
                    'campaign:warmup question:"Do you think gold or equities will outperform in the next six months?"',
                    'campaign:warmup topic:"Interest in structured products linked to AI sector"',
                ],
                required_integrations=["xai"],
                parameters={
                    "question": {"description": "Poll question or warmup topic", "required": True},
                    "channels": {"description": "Channels to use", "required": False, "default": "email,whatsapp"},
                    "audience": {"description": "Target audience segment", "required": False},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="workflow",
                description="Design campaign workflow and automation rules",
                long_help="Define the campaign workflow including: automated responses for basic questions "
                          "(linked to FAQ/T&Cs), forwarding of interested leads with calendly links, "
                          "automated follow-up timing, and escalation rules.",
                aliases=["automation"],
                examples=[
                    'campaign:workflow campaign:"Q1 Gold Note" follow-up-days:3 auto-respond:true',
                ],
                required_integrations=["xai"],
                parameters={
                    "campaign": {"description": "Campaign name or ID", "required": True},
                    "follow-up-days": {"description": "Days before automated follow-up", "required": False, "default": "3"},
                    "auto-respond": {"description": "Enable auto-response for FAQ questions", "required": False, "default": "true", "options": ["true", "false"]},
                    "calendly-link": {"description": "Calendly or booking link for interested leads", "required": False},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="monitor",
                description="View campaign performance and response analytics",
                long_help="Monitor campaign performance across all channels. Shows opens, replies, "
                          "interested leads, removals, and engagement metrics. Consolidates data "
                          "from CRM, email, WhatsApp, Telegram, and social channels.",
                aliases=["status", "report"],
                examples=[
                    'campaign:monitor campaign:"Q1 Gold Note"',
                    "campaign:monitor summary:true",
                ],
                required_integrations=["xai"],
                parameters={
                    "campaign": {"description": "Campaign name to monitor (or 'all')", "required": False, "default": "all"},
                    "summary": {"description": "Show summary only", "required": False, "default": "false", "options": ["true", "false"]},
                    "metric": {"description": "Specific metric to focus on", "required": False,
                              "options": ["opens", "replies", "interested", "removals", "conversions"]},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="follow-up",
                description="Generate follow-up content for campaign non-responders",
                long_help="Generate follow-up messages for contacts who haven't responded within "
                          "the campaign's follow-up window. Adapts tone and urgency based on "
                          "the number of previous touches.",
                aliases=["nudge"],
                examples=[
                    'campaign:follow-up campaign:"Q1 Gold Note" touch:2 channel:email',
                ],
                required_integrations=["xai"],
                parameters={
                    "campaign": {"description": "Campaign to follow up on", "required": True},
                    "touch": {"description": "Which follow-up touch (1st, 2nd, 3rd)", "required": False, "default": "1"},
                    "channel": {"description": "Channel for follow-up", "required": False, "default": "email",
                               "options": ["email", "whatsapp", "telegram", "linkedin"]},
                },
                estimated_seconds=12,
            ),
            ToolDefinition(
                name="ab-test",
                description="Design A/B test for campaign elements",
                long_help="Design an A/B test for campaign messaging, subject lines, CTAs, "
                          "or creative. Provides statistical framework and variant generation.",
                aliases=["split-test"],
                examples=[
                    'campaign:ab-test element:subject-line campaign:"Q1 Gold Note" variants:3',
                ],
                required_integrations=["xai"],
                parameters={
                    "element": {"description": "What to test", "required": True,
                               "options": ["subject-line", "cta", "body-copy", "creative", "send-time", "channel"]},
                    "campaign": {"description": "Campaign context", "required": False},
                    "variants": {"description": "Number of variants", "required": False, "default": "2"},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="leads",
                description="Analyze and prioritize campaign leads",
                long_help="Analyze campaign responses to identify and prioritize leads. "
                          "Categorizes as: interested (forward to sales), questions (auto-respond), "
                          "removal requests (flag for CRM), and non-responders (schedule follow-up).",
                aliases=["qualify"],
                examples=[
                    'campaign:leads campaign:"Q1 Gold Note" action:prioritize',
                ],
                required_integrations=["xai"],
                parameters={
                    "campaign": {"description": "Campaign to analyze leads for", "required": True},
                    "action": {"description": "What to do with leads", "required": False, "default": "analyze",
                              "options": ["analyze", "prioritize", "assign", "export"]},
                },
                estimated_seconds=10,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        tool = self.resolve_tool(tool_name)
        for pname, pinfo in (tool.parameters if tool else {}).items():
            if pinfo.get("required") and pname not in args:
                return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt=f"Missing required parameter: {pname}")

        xai = context.get_integration("xai")
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""
        compliance_block = ""
        if hasattr(context, 'compliance_docs'):
            compliance_block = context.compliance_docs.to_prompt_block()

        prompt_base = self._get_system_prompt(context)

        if tool_name == "create":
            return await self._create(args, xai, product_block, compliance_block, prompt_base)
        elif tool_name == "warmup":
            return await self._warmup(args, xai, product_block, prompt_base)
        elif tool_name == "workflow":
            return await self._workflow(args, xai, product_block, compliance_block, prompt_base)
        elif tool_name == "monitor":
            return await self._monitor(args, xai, product_block, prompt_base)
        elif tool_name == "follow-up":
            return await self._follow_up(args, xai, product_block, prompt_base)
        elif tool_name == "ab-test":
            return await self._ab_test(args, xai, product_block, prompt_base)
        elif tool_name == "leads":
            return await self._leads(args, xai, product_block, prompt_base)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _create(self, args, xai, product_block, compliance_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        product = args.get("product", "")
        audience = args.get("audience", "")
        channels = args.get("channels", "email")
        campaign_type = args.get("type", "product")
        topic = args.get("topic", "")
        duration = args.get("duration", "2w")

        system = f"""{prompt_base}
{product_block}
{compliance_block}
Create a comprehensive {campaign_type} campaign brief for financial product marketing.

Include:
1. Campaign Objective & KPIs
2. Target Audience Definition (aligned with MiFID target market if applicable)
3. Channel Strategy: {channels}
4. Messaging Framework (compliant with financial regulations)
5. Content Calendar for {duration} duration
6. Automation Rules (auto-responses, follow-up timing, lead forwarding)
7. Compliance Checklist (required disclaimers per channel)
8. Success Metrics & Reporting Schedule

Important: All content must be suitable for financial promotion regulations."""

        topic_note = f"Topic: {topic}" if topic else ""
        prompt = f"Create campaign for: {product or topic or 'financial product'}\nAudience: {audience}\n{topic_note}"
        output = await xai.generate(system, prompt, max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _warmup(self, args, xai, product_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        question = args["question"]
        channels = args.get("channels", "email,whatsapp")
        audience = args.get("audience", "")

        audience_note = f"Target: {audience}" if audience else ""
        system = f"""{prompt_base}
{product_block}
Create a lightweight warmup/polling campaign to test market interest.
This is a pre-product-launch market test, not a financial promotion.
Channels: {channels}. {audience_note}

Generate:
1. Warmup message for each channel (adapted to channel format/length)
2. Response collection mechanism
3. Follow-up logic based on responses
4. How to segment responders for future targeting
5. Timeline (keep it short - 3-5 days)

Keep the tone conversational and non-promotional. This is market research, not selling."""

        output = await xai.generate(system, f"Warmup question: {question}", max_tokens=2000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _workflow(self, args, xai, product_block, compliance_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        campaign = args["campaign"]
        follow_up_days = args.get("follow-up-days", "3")
        auto_respond = args.get("auto-respond", "true")
        calendly = args.get("calendly-link", "")

        calendly_note = f"Booking link for interested leads: {calendly}" if calendly else "Include placeholder for booking/calendly link."
        system = f"""{prompt_base}
{product_block}
{compliance_block}
Design a campaign automation workflow for: {campaign}

Workflow rules:
1. Auto-response: {'Enabled' if auto_respond == 'true' else 'Disabled'}
   - FAQ-linked responses for product questions
   - T&C queries answered from approved documents
2. Interest forwarding:
   - "Yes, interested" responses → forward to sales team
   - {calendly_note}
3. Follow-up automation:
   - Non-responders: follow up after {follow_up_days} days
   - Max 3 follow-up touches
4. Removal handling:
   - "Remove me" / unsubscribe → flag in CRM (GDPR compliance)
5. Escalation rules:
   - Complex queries → forward to relationship manager
   - Compliance concerns → flag to compliance team

Output as a clear workflow diagram (text-based) with decision points."""

        output = await xai.generate(system, f"Design workflow for campaign: {campaign}", max_tokens=2500)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _monitor(self, args, xai, product_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        campaign = args.get("campaign", "all")
        summary = args.get("summary", "false")
        metric = args.get("metric", "")

        system = f"""{prompt_base}
{product_block}
Generate a campaign monitoring report template for: {campaign}

Include these data points (to be populated from CRM/channel data):
- Email: opens, clicks, replies, unsubscribes
- WhatsApp: delivered, read, replied
- Telegram: delivered, read, replied
- LinkedIn: impressions, engagement, messages
- X/Twitter: impressions, engagement, clicks
- Instagram: reach, engagement, DMs
- TikTok: views, engagement
- CRM: pipeline movement, qualified leads, meetings booked

Provide:
1. Dashboard template with KPI summary
2. Channel comparison matrix
3. Lead funnel visualization
4. Recommendations for optimization
{"5. Focus on: " + metric if metric else ""}"""

        output = await xai.generate(system, f"Campaign report for: {campaign}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _follow_up(self, args, xai, product_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        campaign = args["campaign"]
        touch = args.get("touch", "1")
        channel = args.get("channel", "email")

        system = f"""{prompt_base}
{product_block}
Generate follow-up message #{touch} for non-responders in campaign: {campaign}
Channel: {channel}

Guidelines:
- Touch 1: Gentle reminder, add value (e.g., relevant market insight)
- Touch 2: Create soft urgency, reference what others are doing
- Touch 3: Final touch, direct ask, respect their decision

Must include appropriate financial disclaimers for the channel.
Adapt length and format to {channel} conventions."""

        output = await xai.generate(system, f"Follow-up #{touch} for {campaign} via {channel}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _ab_test(self, args, xai, product_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        element = args["element"]
        campaign = args.get("campaign", "")
        variants = args.get("variants", "2")

        campaign_note = f"Campaign: {campaign}" if campaign else ""
        system = f"""{prompt_base}
{product_block}
Design an A/B test for: {element}
{campaign_note}

Generate {variants} variants and provide:
1. Each variant with clear differentiation
2. Hypothesis for each variant
3. Required sample size for statistical significance (95% confidence)
4. Recommended test duration
5. Primary and secondary metrics
6. How to implement the test in CRM/email platform
7. Decision framework for selecting the winner

All variants must comply with financial marketing regulations."""

        output = await xai.generate(system, f"A/B test for {element}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _leads(self, args, xai, product_block, prompt_base) -> ToolResult:
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        campaign = args["campaign"]
        action = args.get("action", "analyze")

        system = f"""{prompt_base}
{product_block}
{action.title()} leads for campaign: {campaign}

Lead categorization framework:
1. HOT - Explicitly interested ("yes, tell me more", meeting request)
   → Forward to sales team immediately with context
2. WARM - Engaged but not committed (questions, clicked links)
   → Schedule follow-up, send additional materials
3. QUESTIONS - Asked about product details
   → Auto-respond if FAQ-covered, else forward to specialist
4. REMOVAL - Requested removal / unsubscribe
   → Flag in CRM, GDPR-compliant removal
5. COLD - No response after all touches
   → Park for future campaigns, analyze for patterns

Provide:
- Prioritization scoring methodology
- Handoff template for sales team
- CRM status update recommendations
- Next-best-action for each category"""

        output = await xai.generate(system, f"Lead {action} for campaign: {campaign}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
