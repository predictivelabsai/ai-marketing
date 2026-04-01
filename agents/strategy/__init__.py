"""Strategy agent — Financial product distribution strategy."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are POLLY Strategy, an AI strategist for financial product distribution and marketing. "
    f"Today's date is {date.today()}. You help financial advisors and product manufacturers plan "
    "go-to-market strategies, distribution approaches, and marketing campaigns for financial products. "
    "All strategies must consider MiFID II product governance, target market requirements, "
    "and financial promotion regulations."
)


class StrategyAgent(BaseAgent):
    name = "strategy"
    description = "Distribution strategy, market research, competitor analysis, product positioning"

    def _get_default_prompt(self) -> str:
        return SYSTEM_PROMPT_BASE

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="launch",
                description="Financial product launch planning",
                long_help="Create a comprehensive financial product launch and distribution plan. "
                          "Includes pre-launch, launch day, post-launch, and distribution phases with channel strategies.",
                aliases=["go-to-market", "gtm"],
                examples=[
                    'strategy:launch product:"ESG Bond Fund" stage:pre-launch',
                    'strategy:launch product:"Autocallable Note" stage:distribution',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Product being launched", "required": True},
                    "stage": {"description": "Launch phase", "required": False, "default": "full", "options": ["pre-launch", "launch-day", "post-launch", "full", "distribution"]},
                    "channels": {"description": "Comma-separated launch channels", "required": False},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="market-research",
                description="Conduct market research for financial products",
                long_help="Analyze market conditions, investor appetite, competitive landscape, "
                          "and distribution opportunities for financial products.",
                aliases=["research"],
                examples=[
                    'strategy:market-research sector:"structured products" region:UK',
                    'strategy:research topic:"ESG investment trends"',
                ],
                required_integrations=["xai"],
                parameters={
                    "sector": {"description": "Financial sector/product type", "required": False},
                    "topic": {"description": "Research topic", "required": False},
                    "region": {"description": "Geographic focus", "required": False, "default": "UK/Europe"},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="competitor-matrix",
                description="Build competitor analysis matrix",
                long_help="Analyze competing financial products and their marketing approaches. "
                          "Compares terms, pricing, distribution channels, and market positioning.",
                aliases=["competitors", "comp"],
                examples=[
                    'strategy:competitor-matrix product:"Autocallable Note" competitors:"Issuer A,Issuer B"',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Your product for comparison", "required": True},
                    "competitors": {"description": "Comma-separated competitor products/issuers", "required": False},
                    "criteria": {"description": "Comparison criteria", "required": False, "default": "all",
                                 "options": ["terms", "pricing", "distribution", "marketing", "all"]},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="product-context",
                description="Set or view shared product context",
                long_help="Set or view the shared product context that all agents use for personalized output. "
                          "Use 'set' as first arg to update context, or omit to view current context.",
                aliases=["ctx"],
                examples=[
                    'strategy:product-context set company:"ABC Capital" product:"FTSE Autocallable" audience:"financial advisors"',
                    "strategy:product-context",
                ],
                required_integrations=[],
                parameters={
                    "set": {"description": "Action: include 'set' to update context", "required": False},
                    "company": {"description": "Company name", "required": False},
                    "product": {"description": "Product name/description", "required": False},
                    "audience": {"description": "Target audience", "required": False},
                    "tone": {"description": "Default tone", "required": False},
                    "industry": {"description": "Industry vertical", "required": False},
                    "website": {"description": "Company website", "required": False},
                    "competitors": {"description": "Comma-separated competitor names", "required": False},
                    "value-proposition": {"description": "Core value proposition", "required": False},
                },
                estimated_seconds=1,
            ),
            ToolDefinition(
                name="ideas",
                description="Generate financial marketing ideas",
                long_help="Brainstorm marketing ideas for financial products and distribution. "
                          "Generates actionable ideas across channels with effort/impact scoring.",
                aliases=["brainstorm"],
                examples=[
                    'strategy:ideas topic:"structured product distribution" count:10',
                    'strategy:ideas topic:"ESG fund marketing" channel:email',
                ],
                required_integrations=["xai"],
                parameters={
                    "topic": {"description": "Marketing area or challenge", "required": True},
                    "count": {"description": "Number of ideas", "required": False, "default": "10"},
                    "channel": {"description": "Focus on specific channel", "required": False},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="backtesting",
                description="Generate backtesting analysis content",
                long_help="Create backtesting analysis content showing historical product performance. "
                          "Includes required past-performance disclaimers and methodology disclosure.",
                aliases=["backtest"],
                examples=[
                    'strategy:backtesting product:"FTSE Autocallable" period:10y',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Product to backtest", "required": True},
                    "period": {"description": "Backtesting period", "required": False, "default": "5y"},
                    "underlying": {"description": "Underlying asset/index", "required": False},
                },
                estimated_seconds=20,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        # product-context is special — no XAI needed
        if tool_name == "product-context":
            return self._product_context(args, context)

        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured. Set XAI_API_KEY in .env")

        tool = self.resolve_tool(tool_name)
        for pname, pinfo in (tool.parameters if tool else {}).items():
            if pinfo.get("required") and pname not in args:
                return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt=f"Missing required parameter: {pname}")

        prompt_base = self._get_system_prompt(context)
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        if tool_name == "launch":
            return await self._launch(args, xai, product_block, prompt_base)
        elif tool_name == "market-research":
            return await self._market_research(args, xai, product_block, prompt_base)
        elif tool_name == "competitor-matrix":
            return await self._competitor_matrix(args, xai, product_block, prompt_base)
        elif tool_name == "ideas":
            return await self._ideas(args, xai, product_block, prompt_base)
        elif tool_name == "backtesting":
            return await self._backtesting(args, xai, product_block, prompt_base)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    def _product_context(self, args: dict[str, str], context) -> ToolResult:
        # If 'set' is present (as key or if any other context keys are present), update
        setting_keys = {"company", "product", "audience", "tone", "industry", "website", "competitors", "value-proposition"}
        context_args = {k: v for k, v in args.items() if k in setting_keys}

        if context_args or "set" in args:
            fields_set = context.product.set_from_args(context_args)
            if fields_set:
                output = f"Updated product context: {', '.join(fields_set)}\n\n{context.product.to_prompt_block()}"
            else:
                output = "No fields provided to set. Use: company:, product:, audience:, etc."
            return ToolResult(status=ToolStatus.SUCCESS, output=output)

        # View mode
        if context.product.is_set():
            return ToolResult(status=ToolStatus.SUCCESS, output=context.product.to_prompt_block())
        else:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="No product context set yet.\n\nSet it with:\n  strategy:product-context set company:YourCo product:\"Your Product\" audience:\"Target Audience\"",
            )

    async def _launch(self, args, xai, product_block, prompt_base) -> ToolResult:
        product = args["product"]
        stage = args.get("stage", "full")
        channels = args.get("channels", "")

        channel_note = f"Focus channels: {channels}" if channels else "Cover all relevant distribution channels."
        system = f"""{prompt_base}
{product_block}
Create a {stage} financial product launch and distribution plan. {channel_note}
Include: timeline, distribution channel strategies, advisor communications, regulatory considerations, KPIs, and risk mitigation."""

        output = await xai.generate(system, f"Launch plan for: {product}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _market_research(self, args, xai, product_block, prompt_base) -> ToolResult:
        sector = args.get("sector", "")
        topic = args.get("topic", "")
        region = args.get("region", "UK/Europe")

        system = f"""{prompt_base}
{product_block}
Conduct market research analysis for {region}.
{"Sector: " + sector if sector else ""}

Analyze:
1. Market size and growth trends
2. Investor appetite and sentiment
3. Regulatory environment and upcoming changes
4. Distribution channel landscape
5. Key market participants and market share
6. Opportunities and threats
7. Recommendations for product positioning"""

        prompt = topic or sector or "financial product market analysis"
        output = await xai.generate(system, f"Market research: {prompt}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _competitor_matrix(self, args, xai, product_block, prompt_base) -> ToolResult:
        product = args["product"]
        competitors = args.get("competitors", "")
        criteria = args.get("criteria", "all")

        comp_note = f"Compare against: {competitors}" if competitors else "Identify key competitors."
        system = f"""{prompt_base}
{product_block}
Build a competitor analysis matrix. {comp_note}
Focus: {criteria}

Matrix should cover:
1. Product terms comparison (coupon, maturity, barrier, underlying)
2. Pricing/fees comparison
3. Distribution channels used
4. Marketing approach and materials
5. Target market positioning
6. Strengths and weaknesses
7. Your competitive advantages and differentiation"""

        output = await xai.generate(system, f"Competitor matrix for: {product}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _ideas(self, args, xai, product_block, prompt_base) -> ToolResult:
        topic = args["topic"]
        count = args.get("count", "10")
        channel = args.get("channel", "")

        channel_note = f"Focus on {channel} channel." if channel else "Cover multiple distribution and marketing channels."
        system = f"""{prompt_base}
{product_block}
Generate {count} actionable financial product marketing and distribution ideas. {channel_note}
Consider regulatory constraints on financial promotions.
For each idea: title, description, effort (low/med/high), impact (low/med/high), channel."""

        output = await xai.generate(system, f"Marketing ideas for: {topic}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _backtesting(self, args, xai, product_block, prompt_base) -> ToolResult:
        product = args["product"]
        period = args.get("period", "5y")
        underlying = args.get("underlying", "")

        underlying_note = f"Underlying: {underlying}" if underlying else ""
        system = f"""{prompt_base}
{product_block}
Create backtesting analysis content for: {product}
Period: {period}. {underlying_note}

Include:
1. Methodology description
2. Historical performance scenarios
3. Key statistics (hit rate, average return, max drawdown)
4. Comparison vs direct underlying investment
5. Stress test scenarios
6. MANDATORY DISCLAIMERS:
   - Past performance is not a reliable indicator of future results
   - The value of investments can go down as well as up
   - Backtesting methodology and limitations
   - Not a guarantee of future performance"""

        output = await xai.generate(system, f"Backtesting for: {product}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
