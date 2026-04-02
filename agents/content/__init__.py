"""Content agent — Financial marketing content, copywriting, email sequences."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are POLLY Content, an AI content specialist for financial product marketing. "
    f"Today's date is {date.today()}. You create compliant marketing content for financial "
    "advisors and product distributors. All content must be fair, clear, and not misleading "
    "per FCA/MiFID II guidelines. Never make guarantees about returns or performance. "
    "Always include appropriate risk warnings where required."
)


class ContentAgent(BaseAgent):
    name = "content"
    description = "Financial marketing content — FAQs, teasers, pitch decks, compliant copy"

    def _get_default_prompt(self) -> str:
        return SYSTEM_PROMPT_BASE

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="copywriting",
                description="Generate marketing copy for any format",
                long_help="Generate marketing copy for headlines, landing pages, CTAs, and more. "
                          "Powered by XAI/Grok. Respects product context if set.",
                aliases=["copy"],
                examples=[
                    'content:copywriting topic:"Structured product benefits" format:bullet',
                    'content:copywriting topic:"Fund performance update" tone:professional',
                    'content:copywriting topic:"New bond offering" format:headline',
                ],
                required_integrations=["xai"],
                parameters={
                    "topic": {"description": "What to write about", "required": True},
                    "format": {"description": "Output format", "required": False, "default": "paragraph", "options": ["headline", "paragraph", "bullet", "cta"]},
                    "tone": {"description": "Writing tone", "required": False, "default": "professional", "options": ["professional", "casual", "urgent", "friendly"]},
                    "platform": {"description": "Target platform", "required": False, "default": "web", "options": ["web", "email", "social"]},
                },
                estimated_seconds=8,
            ),
            ToolDefinition(
                name="copy-editing",
                description="Review and improve existing copy",
                long_help="Analyze existing copy and provide improvements for clarity, persuasion, and conciseness.",
                aliases=["edit"],
                examples=[
                    'content:copy-editing input:"Our product helps businesses grow faster with AI."',
                    'content:edit input:"Sign up now for free" goal:persuasion',
                ],
                required_integrations=["xai"],
                parameters={
                    "input": {"description": "The copy to review and improve", "required": True},
                    "goal": {"description": "Editing focus", "required": False, "default": "all", "options": ["clarity", "persuasion", "conciseness", "all"]},
                },
                estimated_seconds=8,
            ),
            ToolDefinition(
                name="social-content",
                description="Platform-optimized social media posts",
                long_help="Generate social media posts optimized for specific platforms. "
                          "X posts are kept under 280 chars, LinkedIn posts are long-form professional.",
                aliases=["social"],
                examples=[
                    'content:social-content platform:linkedin topic:"Market outlook Q1"',
                    'content:social-content platform:x topic:"New fund launch"',
                ],
                required_integrations=["xai"],
                parameters={
                    "topic": {"description": "What to post about", "required": True},
                    "platform": {"description": "Target social platform", "required": False, "default": "x", "options": ["x", "linkedin", "both"]},
                    "tone": {"description": "Writing tone", "required": False, "default": "professional"},
                },
                estimated_seconds=10,
            ),
            ToolDefinition(
                name="email-sequence",
                description="Multi-step email drip sequences",
                long_help="Design multi-step email drip sequences with subject lines, body copy, and timing recommendations.",
                aliases=["email"],
                examples=[
                    "content:email-sequence type:nurture steps:5",
                    'content:email topic:"New structured product launch" type:onboarding steps:3',
                ],
                required_integrations=["xai"],
                parameters={
                    "type": {"description": "Sequence type", "required": False, "default": "onboarding", "options": ["onboarding", "nurture", "retention", "upsell", "reactivation"]},
                    "topic": {"description": "Email sequence topic/trigger", "required": False},
                    "steps": {"description": "Number of emails in sequence", "required": False, "default": "5"},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="faq",
                description="Generate FAQ document from product documentation",
                long_help="Generate a comprehensive FAQ based on compliance-approved product documents. "
                          "Answers are drawn from prospectus, term sheet, and T&Cs to ensure accuracy.",
                aliases=[],
                examples=[
                    'content:faq product:"Gold-Linked Autocallable Note"',
                    'content:faq source:term-sheet',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Product name", "required": False},
                    "source": {"description": "Primary source document", "required": False, "default": "all",
                               "options": ["all", "prospectus", "term-sheet", "terms-conditions", "priips"]},
                    "count": {"description": "Number of Q&A pairs", "required": False, "default": "15"},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="teaser",
                description="Create compliant product teaser",
                long_help="Generate a product teaser document suitable for initial distribution "
                          "to prospective investors. Includes key product features, indicative terms, "
                          "and required risk disclosures.",
                aliases=[],
                examples=[
                    'content:teaser product:"5Y Autocallable on FTSE 100" audience:"HNW retail"',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Product name/description", "required": True},
                    "audience": {"description": "Target investor audience", "required": False},
                    "format": {"description": "Teaser format", "required": False, "default": "one-pager",
                               "options": ["one-pager", "email", "social-snippet"]},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="pitch-deck",
                description="Generate pitch deck content for financial products",
                long_help="Create slide-by-slide content for a financial product pitch deck. "
                          "Includes product overview, market context, key terms, risk factors, "
                          "target market, and compliance disclosures.",
                aliases=["deck", "presentation"],
                examples=[
                    'content:pitch-deck product:"ESG Bond Fund" slides:10',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Product to pitch", "required": True},
                    "slides": {"description": "Number of slides", "required": False, "default": "10"},
                    "audience": {"description": "Presentation audience", "required": False, "default": "financial advisors"},
                },
                estimated_seconds=20,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured. Set XAI_API_KEY in .env")

        tool = self.resolve_tool(tool_name)
        # Check required params
        for pname, pinfo in (tool.parameters if tool else {}).items():
            if pinfo.get("required") and pname not in args:
                return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt=f"Missing required parameter: {pname}")

        prompt_base = self._get_system_prompt(context)
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        # RAG: retrieve relevant document sections; fall back to in-memory compliance docs
        rag = context.get_integration("rag")
        _DOC_TYPES = {
            "teaser":         ["product_description", "term_sheet", "teaser"],
            "faq":            ["faq", "term_sheet", "product_description"],
            "pitch-deck":     ["pitch_deck", "product_description", "term_sheet"],
            "email-sequence": ["product_description", "term_sheet"],
            "social-content": ["product_description", "teaser"],
            "copywriting":    ["product_description"],
        }
        if rag and tool_name in _DOC_TYPES:
            doc_context = rag.retrieve_as_prompt_block(
                query=tool_name, doc_types=_DOC_TYPES[tool_name], top_k=5
            )
        else:
            doc_context = context.compliance_docs.to_prompt_block()

        if tool_name == "copywriting":
            return await self._copywriting(args, xai, product_block, doc_context, prompt_base)
        elif tool_name == "copy-editing":
            return await self._copy_editing(args, xai, product_block, prompt_base)
        elif tool_name == "social-content":
            return await self._social_content(args, xai, product_block, doc_context, prompt_base)
        elif tool_name == "email-sequence":
            return await self._email_sequence(args, xai, product_block, doc_context, prompt_base)
        elif tool_name == "faq":
            return await self._faq(args, xai, product_block, doc_context, prompt_base)
        elif tool_name == "teaser":
            return await self._teaser(args, xai, product_block, doc_context, prompt_base)
        elif tool_name == "pitch-deck":
            return await self._pitch_deck(args, xai, product_block, doc_context, prompt_base)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _copywriting(self, args, xai, product_block, doc_context, prompt_base) -> ToolResult:
        topic = args["topic"]
        fmt = args.get("format", "paragraph")
        tone = args.get("tone", "professional")
        platform = args.get("platform", "web")

        system = f"""{prompt_base}
{product_block}
{doc_context}
Generate {fmt} format marketing copy. Tone: {tone}. Target platform: {platform}."""

        user_prompt = f"Write marketing copy about: {topic}"
        output = await xai.generate(system, user_prompt)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _copy_editing(self, args, xai, product_block, prompt_base) -> ToolResult:
        text = args.get("input", "")
        goal = args.get("goal", "all")

        system = f"""{prompt_base}
{product_block}
You are reviewing and improving existing copy. Focus: {goal}.
Provide the improved version followed by a brief explanation of changes."""

        output = await xai.generate(system, f"Improve this copy:\n\n{text}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _social_content(self, args, xai, product_block, doc_context, prompt_base) -> ToolResult:
        topic = args["topic"]
        platform = args.get("platform", "x")
        tone = args.get("tone", "professional")

        platforms = ["x", "linkedin"] if platform == "both" else [platform]
        outputs = []

        for p in platforms:
            if p == "x":
                constraint = "Maximum 280 characters. Punchy and engaging."
            else:
                constraint = "2-3 paragraphs. Professional LinkedIn style."

            system = f"""{prompt_base}
{product_block}
{doc_context}
Generate a {p.upper()} social media post. {constraint} Tone: {tone}.
Include relevant hashtags."""

            result = await xai.generate(system, f"Write a social post about: {topic}")
            outputs.append(f"--- {p.upper()} ---\n{result}")

        return ToolResult(status=ToolStatus.SUCCESS, output="\n\n".join(outputs))

    async def _email_sequence(self, args, xai, product_block, doc_context, prompt_base) -> ToolResult:
        seq_type = args.get("type", "onboarding")
        topic = args.get("topic", seq_type)
        steps = args.get("steps", "5")

        system = f"""{prompt_base}
{product_block}
{doc_context}
Design a {steps}-step {seq_type} email sequence.
For each email include: subject line, preview text, body copy, CTA, and recommended send timing."""

        output = await xai.generate(system, f"Create an email sequence for: {topic}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _faq(self, args, xai, product_block, doc_context, prompt_base) -> ToolResult:
        product = args.get("product", "the financial product")
        source = args.get("source", "all")
        count = args.get("count", "15")

        system = f"""{prompt_base}
{product_block}
{doc_context}
Generate {count} frequently asked questions and answers for: {product}
Source documents: {source}

Guidelines:
- Answers must be factually based on product documentation only
- Include questions about: product mechanics, risks, costs, target investors, redemption, taxation
- Never guarantee returns or performance
- Reference relevant sections of the prospectus/term sheet where appropriate
- Include a risk warning at the end"""

        output = await xai.generate(system, f"Generate FAQ for: {product}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _teaser(self, args, xai, product_block, doc_context, prompt_base) -> ToolResult:
        product = args["product"]
        audience = args.get("audience", "qualified investors")
        fmt = args.get("format", "one-pager")

        system = f"""{prompt_base}
{product_block}
{doc_context}
Create a {fmt} product teaser for: {product}
Target audience: {audience}

Include:
- Product headline and key selling points
- Indicative terms (coupon, maturity, underlying, barrier)
- Key dates (offer period, issue date, maturity)
- Risk factors summary
- Required regulatory disclosures
- Contact/next steps

This is a marketing document subject to financial promotions regulations.
It must be fair, clear, and not misleading."""

        output = await xai.generate(system, f"Create teaser for: {product}", max_tokens=2000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _pitch_deck(self, args, xai, product_block, doc_context, prompt_base) -> ToolResult:
        product = args["product"]
        slides = args.get("slides", "10")
        audience = args.get("audience", "financial advisors")

        system = f"""{prompt_base}
{product_block}
{doc_context}
Create content for a {slides}-slide pitch deck for: {product}
Target audience: {audience}

Suggested slide structure:
1. Title slide with product name and issuer
2. Market opportunity / macro context
3. Product overview and structure
4. Key terms and indicative pricing
5. Payoff scenarios (best/base/worst case)
6. Target market and suitability
7. Risk factors
8. Competitive positioning
9. Process and timeline
10. Disclaimers and regulatory disclosures

For each slide provide: title, key bullet points, and speaker notes.
All content must comply with financial promotion regulations."""

        output = await xai.generate(system, f"Pitch deck for: {product}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
