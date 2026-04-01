"""Channels agent — Multi-channel monitoring and analytics consolidation."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are POLLY Channel Analyst, an AI assistant that monitors and analyzes marketing performance "
    f"across multiple communication channels for financial product campaigns. Today's date is {date.today()}. "
    "You consolidate data from email, WhatsApp, Telegram, social media, and CRM systems."
)


class ChannelsAgent(BaseAgent):
    name = "channels"
    description = "Multi-channel monitoring, analytics, response consolidation"

    def _get_default_prompt(self) -> str:
        return SYSTEM_PROMPT_BASE

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="report",
                description="Generate consolidated cross-channel analytics report",
                long_help="Consolidate analytics from all channels into a unified report. "
                          "Covers Instagram insights, Twitter analytics, TikTok analytics, "
                          "email replies, WhatsApp/Telegram replies, and CRM metrics.",
                aliases=["dashboard"],
                examples=[
                    'channels:report period:7d campaign:"Q1 Gold Note"',
                    "channels:report period:30d format:summary",
                ],
                required_integrations=["xai"],
                parameters={
                    "period": {"description": "Reporting period (e.g. 7d, 30d, 1m)", "required": False, "default": "7d"},
                    "campaign": {"description": "Filter by campaign name", "required": False},
                    "format": {"description": "Report format", "required": False, "default": "detailed",
                              "options": ["summary", "detailed", "executive"]},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="email",
                description="Email channel analytics and response analysis",
                long_help="Analyze email campaign performance: opens, clicks, replies, "
                          "unsubscribes. Parse reply sentiment and categorize responses.",
                aliases=["mail"],
                examples=[
                    'channels:email campaign:"Q1 Gold Note" metric:replies',
                ],
                required_integrations=["xai"],
                parameters={
                    "campaign": {"description": "Campaign to analyze", "required": False, "default": "all"},
                    "metric": {"description": "Specific metric", "required": False,
                              "options": ["opens", "clicks", "replies", "unsubscribes", "all"]},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="whatsapp",
                description="WhatsApp channel monitoring and response analysis",
                long_help="Monitor WhatsApp Business responses to campaigns. "
                          "Track delivery, read receipts, and reply analysis. "
                          "Sales team members must authorize their WhatsApp for inclusion.",
                aliases=["wa"],
                examples=[
                    "channels:whatsapp campaign:all",
                    'channels:wa campaign:"Q1 Gold Note"',
                ],
                required_integrations=[],
                parameters={
                    "campaign": {"description": "Campaign to monitor", "required": False, "default": "all"},
                    "action": {"description": "What to do", "required": False, "default": "status",
                              "options": ["status", "replies", "authorize"]},
                },
                estimated_seconds=5,
            ),
            ToolDefinition(
                name="telegram",
                description="Telegram channel monitoring and response analysis",
                long_help="Monitor Telegram channel/group responses to campaigns. "
                          "Track message delivery and replies.",
                aliases=["tg"],
                examples=[
                    "channels:telegram campaign:all",
                ],
                required_integrations=[],
                parameters={
                    "campaign": {"description": "Campaign to monitor", "required": False, "default": "all"},
                    "action": {"description": "What to do", "required": False, "default": "status",
                              "options": ["status", "replies", "authorize"]},
                },
                estimated_seconds=5,
            ),
            ToolDefinition(
                name="instagram",
                description="Instagram insights and engagement analytics",
                long_help="Pull Instagram View Insights data including reach, "
                          "impressions, engagement rate, follower growth, and story/reel performance.",
                aliases=["insta", "ig"],
                examples=[
                    "channels:instagram period:7d",
                    "channels:ig metric:engagement",
                ],
                required_integrations=["composio"],
                parameters={
                    "period": {"description": "Analysis period", "required": False, "default": "7d"},
                    "metric": {"description": "Specific metric", "required": False,
                              "options": ["reach", "engagement", "followers", "stories", "reels", "all"]},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="twitter",
                description="Twitter/X analytics and engagement metrics",
                long_help="Pull Twitter/X analytics including impressions, engagements, "
                          "link clicks, profile visits, and mention monitoring.",
                aliases=["x"],
                examples=[
                    "channels:twitter period:7d",
                    "channels:x metric:engagement",
                ],
                required_integrations=["composio"],
                parameters={
                    "period": {"description": "Analysis period", "required": False, "default": "7d"},
                    "metric": {"description": "Specific metric", "required": False,
                              "options": ["impressions", "engagement", "clicks", "mentions", "all"]},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="tiktok",
                description="TikTok analytics and performance metrics",
                long_help="Pull TikTok analytics including video views, engagement, "
                          "follower growth, and content performance.",
                aliases=["tt"],
                examples=[
                    "channels:tiktok period:30d",
                ],
                required_integrations=["composio"],
                parameters={
                    "period": {"description": "Analysis period", "required": False, "default": "7d"},
                    "metric": {"description": "Specific metric", "required": False,
                              "options": ["views", "engagement", "followers", "all"]},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="crm",
                description="CRM system metrics and pipeline analytics",
                long_help="Pull CRM metrics including opens, unread, replies, "
                          "campaign metrics, pipeline movement, and lead status updates.",
                aliases=[],
                examples=[
                    "channels:crm campaign:all",
                    'channels:crm campaign:"Q1 Gold Note" metric:pipeline',
                ],
                required_integrations=["composio"],
                parameters={
                    "campaign": {"description": "Campaign to analyze", "required": False, "default": "all"},
                    "metric": {"description": "CRM metric to focus on", "required": False,
                              "options": ["opens", "unread", "replies", "pipeline", "leads", "all"]},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="compare",
                description="Compare channel performance for a campaign",
                long_help="Compare performance across channels for a specific campaign. "
                          "Identifies best-performing channels and suggests budget reallocation.",
                aliases=["benchmark"],
                examples=[
                    'channels:compare campaign:"Q1 Gold Note"',
                ],
                required_integrations=["xai"],
                parameters={
                    "campaign": {"description": "Campaign to compare across channels", "required": True},
                    "channels": {"description": "Specific channels to compare (comma-separated)", "required": False},
                },
                estimated_seconds=12,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        tool = self.resolve_tool(tool_name)
        for pname, pinfo in (tool.parameters if tool else {}).items():
            if pinfo.get("required") and pname not in args:
                return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt=f"Missing required parameter: {pname}")

        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        prompt_base = self._get_system_prompt(context)

        if tool_name == "report":
            return await self._report(args, context, product_block, prompt_base)
        elif tool_name in ("email", "instagram", "twitter", "tiktok", "crm"):
            return await self._channel_analytics(tool_name, args, context, product_block, prompt_base)
        elif tool_name in ("whatsapp", "telegram"):
            return self._messaging_channel(tool_name, args, context)
        elif tool_name == "compare":
            return await self._compare(args, context, product_block, prompt_base)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _report(self, args, context, product_block, prompt_base) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        period = args.get("period", "7d")
        campaign = args.get("campaign", "")
        fmt = args.get("format", "detailed")

        campaign_note = f"Campaign: {campaign}" if campaign else "All campaigns"
        system = f"""{prompt_base}
{product_block}
Generate a {fmt} cross-channel analytics report template.
Period: {period}. {campaign_note}

Data sources to consolidate:
1. Instagram - View Insights (reach, impressions, engagement)
2. Twitter/X - Analytics (impressions, engagement, clicks)
3. TikTok - Analytics (views, engagement, followers)
4. Email - All replies, opens, clicks, unsubscribes
5. WhatsApp - Delivered, read, replies
6. Telegram - Delivered, read, replies
7. CRM - Opens, unread, replies, campaign metrics, pipeline

Report structure:
- Executive summary with top-line KPIs
- Channel-by-channel breakdown
- Response categorization (interested, questions, removals)
- Lead funnel: awareness → engagement → interest → conversion
- Top performing content/messaging
- Recommendations for next period
- GDPR compliance notes (removal requests processed)"""

        output = await xai.generate(system, f"Cross-channel report for {period}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _channel_analytics(self, channel, args, context, product_block, prompt_base) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        campaign = args.get("campaign", "all")
        period = args.get("period", "7d")
        metric = args.get("metric", "all")

        channel_metrics = {
            "email": "opens, clicks, replies, bounces, unsubscribes, spam reports",
            "instagram": "reach, impressions, engagement rate, follower growth, story views, reel plays",
            "twitter": "impressions, engagements, link clicks, retweets, quotes, profile visits",
            "tiktok": "video views, likes, comments, shares, follower growth, watch time",
            "crm": "pipeline value, lead count, stage progression, activities logged, meetings booked",
        }

        system = f"""{prompt_base}
{product_block}
Generate {channel} analytics report template.
Campaign: {campaign}. Period: {period}. Focus: {metric}
Metrics to track: {channel_metrics.get(channel, 'all available metrics')}

Provide:
1. KPI dashboard template
2. Trend analysis framework
3. Benchmark comparisons
4. Actionable insights template
5. Integration instructions for connecting live data"""

        output = await xai.generate(system, f"{channel.title()} analytics for {period}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    def _messaging_channel(self, channel, args, context) -> ToolResult:
        campaign = args.get("campaign", "all")
        action = args.get("action", "status")

        if action == "authorize":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"{channel.title()} Authorization\n\n"
                       f"To include your personal {channel.title()} in campaign response monitoring:\n"
                       f"1. Contact your administrator to initiate {channel.title()} Business API connection\n"
                       f"2. Authorize POLLY to read responses from your {channel.title()} number\n"
                       f"3. Sales team members must individually authorize their numbers\n\n"
                       f"Note: POLLY uses {channel.title()} as a SEND and RECEIVE mechanism only.\n"
                       f"Response data feeds into campaign analytics for reporting."
            )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"{channel.title()} Channel Status\n\n"
                   f"Campaign: {campaign}\n"
                   f"Status: Awaiting {channel.title()} Business API integration\n\n"
                   f"Once connected, POLLY will monitor:\n"
                   f"- Message delivery status\n"
                   f"- Read receipts\n"
                   f"- Reply analysis and categorization\n"
                   f"- Auto-response triggers (FAQ-linked)\n"
                   f"- Lead forwarding for 'interested' responses\n\n"
                   f"Run 'channels:{channel} action:authorize' to set up your number."
        )

    async def _compare(self, args, context, product_block, prompt_base) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        campaign = args["campaign"]
        channels = args.get("channels", "email,whatsapp,telegram,linkedin,x,instagram,tiktok")

        system = f"""{prompt_base}
{product_block}
Compare performance across channels for campaign: {campaign}
Channels: {channels}

Analysis framework:
1. Reach & Delivery Comparison
2. Engagement Rate Comparison (normalized across channels)
3. Response Quality (interested leads per channel)
4. Cost per Qualified Lead (if applicable)
5. Time to Response by Channel
6. Best channel for each campaign phase (awareness, consideration, conversion)
7. Channel synergy effects (multi-touch attribution)
8. Recommendations: budget reallocation and channel optimization"""

        output = await xai.generate(system, f"Channel comparison for campaign: {campaign}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
