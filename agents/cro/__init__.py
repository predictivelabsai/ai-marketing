"""CRO agent — Conversion rate optimization and page analysis."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are an expert conversion rate optimization (CRO) specialist. "
    f"Today's date is {date.today()}. "
    "Analyze the provided page data and give specific, actionable recommendations "
    "with priority ratings (high/medium/low) and expected impact. "
    "Reference current best practices and recent industry benchmarks."
)


class CroAgent(BaseAgent):
    name = "cro"
    description = "Conversion rate optimization & page analysis"

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="page-cro",
                description="Analyze any page for conversion optimization",
                long_help="Crawl a URL and analyze the page for conversion optimization opportunities. "
                          "Examines layout, CTAs, copy, trust signals, and user flow.",
                aliases=["analyze", "page"],
                examples=[
                    "cro:page-cro url:https://example.com",
                    'cro:page-cro url:https://example.com/pricing focus:"above the fold"',
                ],
                required_integrations=["playwright", "xai"],
                parameters={
                    "url": {"description": "Page URL to analyze", "required": True},
                    "focus": {"description": "Specific area to focus on", "required": False},
                },
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="signup-flow",
                description="Audit signup/registration flow",
                aliases=["signup"],
                examples=["cro:signup-flow url:https://example.com/signup"],
                required_integrations=["playwright", "xai"],
                parameters={"url": {"description": "Signup page URL", "required": True}},
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="onboarding",
                description="Evaluate post-signup onboarding experience",
                aliases=["onboard"],
                examples=["cro:onboarding url:https://app.example.com/welcome"],
                required_integrations=["playwright", "xai"],
                parameters={"url": {"description": "Onboarding page URL", "required": True}},
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="form-cro",
                description="Optimize forms (field count, labels, layout)",
                aliases=["form"],
                examples=["cro:form-cro url:https://example.com/contact"],
                required_integrations=["playwright", "xai"],
                parameters={"url": {"description": "Page URL containing the form", "required": True}},
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="popup-cro",
                description="Analyze popups/modals for conversion",
                aliases=["popup"],
                examples=["cro:popup-cro url:https://example.com"],
                required_integrations=["playwright", "xai"],
                parameters={"url": {"description": "Page URL to analyze for popups", "required": True}},
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="paywall-upgrade",
                description="Review upgrade/upsell screens",
                aliases=["paywall", "upsell"],
                examples=["cro:paywall-upgrade url:https://app.example.com/upgrade"],
                required_integrations=["playwright", "xai"],
                parameters={"url": {"description": "Upgrade/paywall page URL", "required": True}},
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="churn-prevention",
                description="Analyze cancel flow and retention hooks",
                aliases=["churn", "cancel"],
                examples=["cro:churn-prevention url:https://app.example.com/cancel"],
                required_integrations=["playwright", "xai"],
                parameters={"url": {"description": "Cancel/churn page URL", "required": True}},
                estimated_seconds=30,
            ),
            ToolDefinition(
                name="free-tool-strategy",
                description="Plan free tools for lead generation",
                long_help="Plan a free tool strategy for lead generation. "
                          "Does not require Playwright — uses XAI to brainstorm tool ideas.",
                aliases=["free-tool"],
                examples=[
                    'cro:free-tool-strategy industry:"SaaS" goal:"email signups"',
                ],
                required_integrations=["xai"],
                parameters={
                    "industry": {"description": "Your industry/niche", "required": True},
                    "goal": {"description": "Lead gen goal", "required": False, "default": "email signups"},
                },
                estimated_seconds=15,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured. Set XAI_API_KEY in .env")

        # free-tool-strategy doesn't need playwright
        if tool_name == "free-tool-strategy":
            return await self._free_tool_strategy(args, xai, context)

        playwright = context.get_integration("playwright")
        if not playwright:
            return ToolResult(status=ToolStatus.ERROR, error="Playwright integration not available. Install playwright: pip install playwright && playwright install chromium")

        url = args.get("url")
        if not url:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Which URL to analyze?")

        return await self._analyze_page(tool_name, url, args, xai, playwright, context)

    async def _analyze_page(self, tool_name, url, args, xai, playwright, context) -> ToolResult:
        """Common pattern: fetch page → analyze with XAI."""
        try:
            snapshot = await playwright.get_page_snapshot(url)
        except Exception as e:
            return ToolResult(status=ToolStatus.ERROR, error=f"Failed to load page: {e}")

        # Trim HTML to avoid token limits (keep first 15K chars)
        html_excerpt = snapshot["html"][:15000]
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        focus_map = {
            "page-cro": "comprehensive CRO audit covering: hero section, CTAs, social proof, trust signals, copy clarity, mobile responsiveness, page speed signals",
            "signup-flow": "signup flow analysis: form fields, friction points, social login options, password requirements, error handling, value proposition clarity",
            "onboarding": "onboarding experience: first-time user experience, progressive disclosure, time to value, activation milestones, help/guidance",
            "form-cro": "form optimization: field count, labels, placeholder text, validation, layout, multi-step potential, required vs optional",
            "popup-cro": "popup/modal analysis: timing, targeting, copy, design, exit-intent, frequency, value proposition",
            "paywall-upgrade": "upgrade/paywall screen: pricing clarity, feature comparison, urgency elements, social proof, objection handling",
            "churn-prevention": "cancel flow analysis: retention hooks, surveys, offers, ease of cancellation, win-back potential",
        }

        focus = focus_map.get(tool_name, "general CRO analysis")
        extra_focus = args.get("focus", "")
        if extra_focus:
            focus += f"\nAdditional focus: {extra_focus}"

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Perform a {focus}.
Structure your response with: Summary, Key Findings (with priority), Recommendations, Quick Wins."""

        user_prompt = f"""Analyze this page for conversion optimization:
URL: {url}
Title: {snapshot['title']}
Meta Description: {snapshot['meta_description']}

Page HTML (excerpt):
{html_excerpt}"""

        output = await xai.generate(system, user_prompt, max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _free_tool_strategy(self, args, xai, context) -> ToolResult:
        industry = args["industry"]
        goal = args.get("goal", "email signups")
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Plan a free tool strategy for lead generation.
Goal: {goal}. Industry: {industry}.
Include: 5-10 tool ideas, effort/impact matrix, tech stack suggestions, and distribution plan."""

        output = await xai.generate(system, f"Free tool strategy for {industry} targeting {goal}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
