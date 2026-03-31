"""Ads agent — Paid advertising, A/B testing, analytics tracking."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are an expert paid advertising and growth marketing specialist. "
    f"Today's date is {date.today()}. "
    "Provide data-driven, actionable recommendations using current platform features and recent benchmarks."
)


class AdsAgent(BaseAgent):
    name = "ads"
    description = "Paid advertising, A/B testing, analytics"

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="paid-ads",
                description="Campaign strategy for Google/Meta/LinkedIn/TikTok Ads",
                long_help="Develop paid advertising campaign strategies including targeting, "
                          "bidding, creative guidelines, and budget allocation.",
                aliases=["campaign", "ppc"],
                examples=[
                    'ads:paid-ads platform:google product:"analytics tool" budget:5000',
                    'ads:paid-ads platform:meta audience:"startup founders" goal:signups',
                ],
                required_integrations=["xai"],
                parameters={
                    "platform": {"description": "Ad platform", "required": True, "options": ["google", "meta", "linkedin", "tiktok", "all"]},
                    "product": {"description": "Product to advertise", "required": False},
                    "budget": {"description": "Monthly budget in USD", "required": False},
                    "goal": {"description": "Campaign goal", "required": False, "default": "conversions", "options": ["awareness", "traffic", "signups", "conversions", "revenue"]},
                    "audience": {"description": "Target audience description", "required": False},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="ab-test",
                description="Design A/B experiments with statistical rigor",
                long_help="Design A/B test experiments with proper hypothesis, sample size calculations, "
                          "success metrics, and statistical analysis plan.",
                aliases=["experiment", "split-test"],
                examples=[
                    'ads:ab-test page:"pricing page" hypothesis:"Showing annual savings increases conversions"',
                    'ads:ab-test element:"CTA button" variants:3 metric:click-rate',
                ],
                required_integrations=["xai"],
                parameters={
                    "page": {"description": "Page or feature to test", "required": False},
                    "element": {"description": "Specific element to test", "required": False},
                    "hypothesis": {"description": "Test hypothesis", "required": False},
                    "variants": {"description": "Number of variants", "required": False, "default": "2"},
                    "metric": {"description": "Primary success metric", "required": False, "default": "conversion-rate"},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="analytics-tracking",
                description="Set up GA4 events, UTM params, GTM config",
                long_help="Design analytics tracking plans including GA4 event schemas, "
                          "UTM parameter conventions, and Google Tag Manager configurations.",
                aliases=["tracking", "ga4"],
                examples=[
                    'ads:analytics-tracking scope:"full funnel" platform:ga4',
                    'ads:tracking scope:"signup flow" events:custom',
                ],
                required_integrations=["xai"],
                parameters={
                    "scope": {"description": "What to track", "required": True},
                    "platform": {"description": "Analytics platform", "required": False, "default": "ga4", "options": ["ga4", "mixpanel", "amplitude", "posthog"]},
                    "events": {"description": "Event type focus", "required": False, "default": "recommended", "options": ["recommended", "custom", "ecommerce", "all"]},
                },
                estimated_seconds=20,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured. Set XAI_API_KEY in .env")

        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        if tool_name == "paid-ads":
            return await self._paid_ads(args, xai, product_block)
        elif tool_name == "ab-test":
            return await self._ab_test(args, xai, product_block)
        elif tool_name == "analytics-tracking":
            return await self._analytics_tracking(args, xai, product_block)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _paid_ads(self, args, xai, product_block) -> ToolResult:
        platform = args.get("platform", "")
        if not platform:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Which ad platform? (google, meta, linkedin, tiktok, all)")

        product = args.get("product", "")
        budget = args.get("budget", "")
        goal = args.get("goal", "conversions")
        audience = args.get("audience", "")

        budget_note = f"Monthly budget: ${budget}" if budget else ""
        audience_note = f"Target audience: {audience}" if audience else ""
        product_note = f"Product: {product}" if product else ""

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Design a {platform} ads campaign strategy. Goal: {goal}.
{budget_note} {audience_note} {product_note}
Include: campaign structure, ad groups, targeting, bidding strategy, creative guidelines, budget allocation, KPIs."""

        output = await xai.generate(system, f"Paid ads strategy for {platform}. {product_note}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _ab_test(self, args, xai, product_block) -> ToolResult:
        page = args.get("page", "")
        element = args.get("element", "")
        hypothesis = args.get("hypothesis", "")
        variants = args.get("variants", "2")
        metric = args.get("metric", "conversion-rate")

        if not page and not element and not hypothesis:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="What to A/B test? Provide page:, element:, or hypothesis:")

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Design an A/B test experiment with {variants} variants. Primary metric: {metric}.
Include: hypothesis, control vs variant(s), sample size calculation, test duration estimate,
success criteria, statistical significance threshold, and analysis plan."""

        test_desc = " ".join(filter(None, [
            f"Page: {page}" if page else "",
            f"Element: {element}" if element else "",
            f"Hypothesis: {hypothesis}" if hypothesis else "",
        ]))

        output = await xai.generate(system, f"Design A/B test: {test_desc}", max_tokens=2000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _analytics_tracking(self, args, xai, product_block) -> ToolResult:
        scope = args.get("scope", "")
        if not scope:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="What scope to track? (e.g., 'full funnel', 'signup flow', 'checkout')")

        platform = args.get("platform", "ga4")
        events = args.get("events", "recommended")

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Design an analytics tracking plan for {platform}. Scope: {scope}. Event type: {events}.
Include: event names, parameters, triggers, UTM conventions, data layer specifications,
and implementation code snippets (GTM or direct)."""

        output = await xai.generate(system, f"Analytics tracking plan for: {scope}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
