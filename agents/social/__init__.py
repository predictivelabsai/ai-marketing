"""Social agent — Post to social media, WhatsApp, Telegram for financial product marketing."""
from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


class SocialAgent(BaseAgent):
    name = "social"
    description = "Post to X/LinkedIn/WhatsApp/Telegram, scheduling, analytics"

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="post",
                description="Post to X and/or LinkedIn",
                long_help="Post content to social media platforms via Arcade.dev. "
                          "Supports X (Twitter) and LinkedIn. Wraps the existing ArcadeSocialPoster.",
                aliases=["publish"],
                examples=[
                    'social:post channel:linkedin content:"New structured product alert - capital protected note linked to FTSE 100"',
                    'social:post channel:whatsapp content:"Hi, just sharing our latest market update on gold outlook"',
                    'social:post channel:x content:"Market insight: Why structured products in this environment? #fintech #investing"',
                ],
                required_integrations=["arcade"],
                parameters={
                    "channel": {"description": "Platform to post to", "required": True, "options": ["x", "linkedin", "whatsapp", "telegram", "all"]},
                    "content": {"description": "Text content to post", "required": True},
                    "url": {"description": "URL to include in the post", "required": False},
                    "dry-run": {"description": "Preview without posting", "required": False, "options": ["true", "false"]},
                },
                estimated_seconds=5,
            ),
            ToolDefinition(
                name="schedule",
                description="Queue posts for later",
                long_help="Schedule social media posts for future publication. "
                          "Future: integrate with Buffer via Composio.",
                aliases=["queue"],
                examples=[
                    'social:schedule channel:x content:"Monday motivation!" time:"2026-03-02 09:00"',
                ],
                required_integrations=["arcade"],
                parameters={
                    "channel": {"description": "Platform to schedule for", "required": True, "options": ["x", "linkedin", "whatsapp", "telegram", "all"]},
                    "content": {"description": "Text content to schedule", "required": True},
                    "time": {"description": "ISO datetime or relative time", "required": True},
                },
                estimated_seconds=1,
            ),
            ToolDefinition(
                name="analytics",
                description="View post performance metrics",
                long_help="View engagement metrics for recent social media posts. "
                          "Future: integrate with Buffer/native APIs via Composio.",
                aliases=["stats", "metrics"],
                examples=[
                    "social:analytics channel:x days:7",
                    "social:analytics channel:linkedin",
                ],
                required_integrations=["composio"],
                parameters={
                    "channel": {"description": "Platform to view analytics for", "required": False, "options": ["x", "linkedin", "whatsapp", "telegram", "all"], "default": "all"},
                    "days": {"description": "Number of days to look back", "required": False, "default": "7"},
                },
                estimated_seconds=1,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        if tool_name == "post":
            return await self._post(args, context)
        elif tool_name == "schedule":
            return self._schedule(args, context)
        elif tool_name == "analytics":
            return self._analytics(args, context)
        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _post(self, args: dict[str, str], context) -> ToolResult:
        channel = args.get("channel", "").lower()
        content = args.get("content", "")
        url = args.get("url")
        dry_run = args.get("dry-run", "").lower() in ("true", "1", "yes")

        if not channel:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Which channel? (x, linkedin, whatsapp, telegram, all)")
        if not content:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="What content to post?")

        arcade = context.get_integration("arcade")
        if not arcade:
            return ToolResult(status=ToolStatus.ERROR, error="Arcade integration not configured. Set ARCADE_API_KEY and ARCADE_USER_ID in .env")

        if dry_run:
            preview = f"[DRY RUN] Would post to {channel}:\n{content}"
            if url:
                preview += f"\nURL: {url}"
            return ToolResult(status=ToolStatus.SUCCESS, output=preview)

        results = []
        channels = ["x", "linkedin", "whatsapp", "telegram"] if channel == "all" else [channel]

        for ch in channels:
            if ch in ("x", "twitter"):
                full_content = f"{content}\n\n{url}" if url else content
                result = arcade.execute_tool("X.PostTweet", {"tweet_text": full_content})
                result["platform"] = "x"
            elif ch in ("li", "linkedin"):
                full_content = f"{content}\n\nLearn more: {url}" if url else content
                result = arcade.execute_tool("Linkedin.CreateTextPost", {"text": full_content})
                result["platform"] = "linkedin"
            elif ch == "whatsapp":
                full_content = f"{content}\n\n{url}" if url else content
                # WhatsApp Business API integration (future: via Composio or direct API)
                results.append(f"[yellow]WhatsApp posting queued — awaiting WhatsApp Business API integration[/yellow]\nContent: {full_content[:100]}...")
                continue
            elif ch == "telegram":
                full_content = f"{content}\n\n{url}" if url else content
                # Telegram Bot API integration (future: via Composio or direct API)
                results.append(f"[yellow]Telegram posting queued — awaiting Telegram Bot API integration[/yellow]\nContent: {full_content[:100]}...")
                continue
            else:
                results.append(f"Unknown channel: {ch}")
                continue

            if result.get("success"):
                results.append(f"[green]Posted to {result['platform']}[/green]")
            else:
                results.append(f"[red]Failed on {result.get('platform', ch)}: {result.get('error', 'unknown')}[/red]")

        return ToolResult(status=ToolStatus.SUCCESS, output="\n".join(results))

    def _schedule(self, args: dict[str, str], context) -> ToolResult:
        return ToolResult(
            status=ToolStatus.ERROR,
            error="Scheduling not yet implemented. Coming soon with Composio/Buffer integration.",
        )

    def _analytics(self, args: dict[str, str], context) -> ToolResult:
        return ToolResult(
            status=ToolStatus.ERROR,
            error="Analytics not yet implemented. Coming soon with Composio/Buffer integration.",
        )
