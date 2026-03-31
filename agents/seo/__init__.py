"""SEO agent — Audits, schema markup, competitor analysis."""
from datetime import date

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are an expert SEO specialist. "
    f"Today's date is {date.today()}. "
    "Provide specific, actionable recommendations with priority ratings and expected impact "
    "on search rankings. Reference current algorithm updates and recent best practices."
)


class SeoAgent(BaseAgent):
    name = "seo"
    description = "SEO audits, schema markup, competitor analysis"

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="audit",
                description="Technical SEO audit (meta, headings, schema, links)",
                long_help="Perform a technical SEO audit by crawling the page and analyzing "
                          "meta tags, heading structure, schema markup, internal/external links, and more.",
                aliases=["check"],
                examples=[
                    "seo:audit url:https://tendly.eu",
                    "seo:audit url:https://example.com/blog depth:shallow",
                ],
                required_integrations=["playwright"],
                parameters={
                    "url": {"description": "URL to audit", "required": True},
                    "depth": {"description": "Audit depth", "required": False, "default": "standard", "options": ["shallow", "standard", "deep"]},
                },
                estimated_seconds=25,
            ),
            ToolDefinition(
                name="programmatic",
                description="Generate SEO page templates at scale",
                long_help="Design programmatic SEO page templates that can be generated at scale. "
                          "Includes page structure, keyword patterns, and internal linking strategy.",
                aliases=["pSEO"],
                examples=[
                    'seo:programmatic template:"city landing pages" keyword-pattern:"{service} in {city}"',
                ],
                required_integrations=["xai"],
                parameters={
                    "template": {"description": "Type of page template", "required": True},
                    "keyword-pattern": {"description": "Keyword pattern with variables", "required": False},
                    "count": {"description": "Number of example pages to generate", "required": False, "default": "5"},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="ai-seo",
                description="Optimize for AI search engines (AEO/LLMO)",
                long_help="Optimize content for AI search engines and answer engines (Google AI Overview, "
                          "ChatGPT, Perplexity). Focus on Answer Engine Optimization (AEO) and LLM Optimization (LLMO).",
                aliases=["aeo", "llmo"],
                examples=[
                    'seo:ai-seo topic:"project management software" format:faq',
                    "seo:ai-seo url:https://example.com/features",
                ],
                required_integrations=["xai"],
                parameters={
                    "topic": {"description": "Topic to optimize for AI search", "required": False},
                    "url": {"description": "URL to analyze for AI search optimization", "required": False},
                    "format": {"description": "Content format", "required": False, "default": "recommendations", "options": ["recommendations", "faq", "structured"]},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="schema-markup",
                description="Generate or validate JSON-LD structured data",
                long_help="Generate JSON-LD structured data for a page or validate existing schema markup. "
                          "Supports Organization, Product, FAQ, Article, and other schema types.",
                aliases=["schema", "jsonld"],
                examples=[
                    "seo:schema-markup url:https://example.com action:validate",
                    'seo:schema-markup type:Product name:"Analytics Pro" action:generate',
                ],
                required_integrations=["playwright"],
                parameters={
                    "url": {"description": "URL to analyze for existing schema", "required": False},
                    "action": {"description": "Action to perform", "required": False, "default": "generate", "options": ["generate", "validate"]},
                    "type": {"description": "Schema type to generate", "required": False, "options": ["Organization", "Product", "FAQ", "Article", "SoftwareApplication", "WebSite"]},
                    "name": {"description": "Entity name for schema generation", "required": False},
                },
                estimated_seconds=20,
            ),
            ToolDefinition(
                name="competitor-alternatives",
                description="Build competitor comparison pages",
                long_help="Analyze competitor pages and generate 'alternatives to' or 'vs' comparison content "
                          "for SEO. Crawls competitor sites to understand their positioning.",
                aliases=["competitors", "vs"],
                examples=[
                    "seo:competitor-alternatives url:https://competitor.com",
                    'seo:competitors competitors:"Asana,Monday,ClickUp" product:"Our PM Tool"',
                ],
                required_integrations=["playwright", "xai"],
                parameters={
                    "url": {"description": "Competitor URL to analyze", "required": False},
                    "competitors": {"description": "Comma-separated competitor names", "required": False},
                    "product": {"description": "Your product name for comparison", "required": False},
                },
                estimated_seconds=25,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        if tool_name == "audit":
            return await self._audit(args, context, product_block)
        elif tool_name == "programmatic":
            return await self._programmatic(args, context, product_block)
        elif tool_name == "ai-seo":
            return await self._ai_seo(args, context, product_block)
        elif tool_name == "schema-markup":
            return await self._schema_markup(args, context, product_block)
        elif tool_name == "competitor-alternatives":
            return await self._competitor_alternatives(args, context, product_block)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _audit(self, args, context, product_block) -> ToolResult:
        url = args.get("url")
        if not url:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Which URL to audit?")

        playwright = context.get_integration("playwright")
        if not playwright:
            return ToolResult(status=ToolStatus.ERROR, error="Playwright not available. Install: pip install playwright && playwright install chromium")

        try:
            meta = await playwright.extract_meta(url)
        except Exception as e:
            return ToolResult(status=ToolStatus.ERROR, error=f"Failed to load page: {e}")

        depth = args.get("depth", "standard")
        xai = context.get_integration("xai")

        # Build audit report from extracted data
        lines = [f"SEO Audit: {url}", f"Title: {meta.get('title', 'N/A')}", ""]

        # Meta tags
        meta_tags = meta.get("meta", {})
        lines.append("META TAGS:")
        for key in ["description", "og:title", "og:description", "twitter:card", "robots"]:
            val = meta_tags.get(key, "[missing]")
            status = "[green]OK[/green]" if val != "[missing]" else "[red]MISSING[/red]"
            lines.append(f"  {key}: {val} {status}")

        # Headings
        headings = meta.get("headings", {})
        lines.append("\nHEADINGS:")
        for tag in ["h1", "h2", "h3"]:
            items = headings.get(tag, [])
            lines.append(f"  {tag}: {len(items)} found")
            for item in items[:5]:
                lines.append(f"    - {item}")

        # Schema/JSON-LD
        jsonld = meta.get("jsonld", [])
        lines.append(f"\nSTRUCTURED DATA: {len(jsonld)} JSON-LD blocks found")
        for block in jsonld[:3]:
            lines.append(f"  @type: {block.get('@type', 'unknown')}")

        report = "\n".join(lines)

        # If XAI available and not shallow, enhance with AI analysis
        if xai and depth != "shallow":
            system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Analyze the following SEO audit data and provide prioritized recommendations.
Structure: Critical Issues, Warnings, Opportunities, Quick Wins."""

            ai_analysis = await xai.generate(system, f"SEO audit data:\n{report}")
            report += f"\n\nAI ANALYSIS:\n{ai_analysis}"

        return ToolResult(status=ToolStatus.SUCCESS, output=report)

    async def _programmatic(self, args, context, product_block) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI not configured")

        template = args.get("template", "")
        if not template:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="What type of page template?")

        keyword_pattern = args.get("keyword-pattern", "")
        count = args.get("count", "5")

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Design a programmatic SEO page template.
Include: page structure (HTML outline), keyword mapping, meta tag templates, internal linking strategy.
Generate {count} example pages."""

        kw_note = f"Keyword pattern: {keyword_pattern}" if keyword_pattern else ""
        output = await xai.generate(system, f"Programmatic SEO template: {template}\n{kw_note}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _ai_seo(self, args, context, product_block) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI not configured")

        topic = args.get("topic", "")
        url = args.get("url", "")
        fmt = args.get("format", "recommendations")

        if not topic and not url:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Provide topic: or url: to optimize")

        page_content = ""
        if url:
            playwright = context.get_integration("playwright")
            if playwright:
                try:
                    snapshot = await playwright.get_page_snapshot(url)
                    page_content = f"\nPage title: {snapshot['title']}\nPage content excerpt: {snapshot['html'][:8000]}"
                except Exception:
                    page_content = f"\n(Could not fetch URL: {url})"

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Optimize for AI search engines (Google AI Overview, ChatGPT, Perplexity).
Focus on Answer Engine Optimization (AEO) and LLM Optimization (LLMO).
Output format: {fmt}."""

        prompt = f"Optimize for AI search: {topic or url}{page_content}"
        output = await xai.generate(system, prompt, max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _schema_markup(self, args, context, product_block) -> ToolResult:
        url = args.get("url", "")
        action = args.get("action", "generate")
        schema_type = args.get("type", "")
        name = args.get("name", "")

        if action == "validate" and url:
            playwright = context.get_integration("playwright")
            if not playwright:
                return ToolResult(status=ToolStatus.ERROR, error="Playwright not available for page analysis")

            try:
                meta = await playwright.extract_meta(url)
            except Exception as e:
                return ToolResult(status=ToolStatus.ERROR, error=f"Failed to load page: {e}")

            jsonld = meta.get("jsonld", [])
            if not jsonld:
                return ToolResult(status=ToolStatus.SUCCESS, output=f"No JSON-LD structured data found on {url}.\n\nRecommendation: Add schema markup to improve search appearance.")

            import json
            lines = [f"Found {len(jsonld)} JSON-LD block(s) on {url}:\n"]
            for i, block in enumerate(jsonld, 1):
                lines.append(f"Block {i} (@type: {block.get('@type', 'unknown')}):")
                lines.append(json.dumps(block, indent=2))
                lines.append("")

            xai = context.get_integration("xai")
            if xai:
                system = f"""{SYSTEM_PROMPT_BASE}
Validate the following JSON-LD structured data. Check for: completeness, correctness, recommended properties, Google rich result eligibility."""
                validation = await xai.generate(system, "\n".join(lines))
                lines.append(f"VALIDATION:\n{validation}")

            return ToolResult(status=ToolStatus.SUCCESS, output="\n".join(lines))

        # Generate mode
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI not configured for schema generation")

        if not schema_type:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Which schema type? (Organization, Product, FAQ, Article, SoftwareApplication, WebSite)")

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Generate valid JSON-LD structured data for schema.org type: {schema_type}.
Output only the JSON-LD script tag. Use realistic placeholder values."""

        name_note = f"Entity name: {name}" if name else ""
        output = await xai.generate(system, f"Generate {schema_type} JSON-LD schema markup. {name_note}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _competitor_alternatives(self, args, context, product_block) -> ToolResult:
        url = args.get("url", "")
        competitors = args.get("competitors", "")
        product = args.get("product", "")

        if not url and not competitors:
            return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt="Provide url: of a competitor or competitors: (comma-separated)")

        page_info = ""
        if url:
            playwright = context.get_integration("playwright")
            if playwright:
                try:
                    snapshot = await playwright.get_page_snapshot(url)
                    page_info = f"\nCompetitor page title: {snapshot['title']}\nCompetitor page excerpt: {snapshot['html'][:8000]}"
                except Exception:
                    page_info = f"\n(Could not fetch: {url})"

        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI not configured")

        product_name = product or (context.product.product if context.product.is_set() else "your product")
        comp_list = competitors or url

        system = f"""{SYSTEM_PROMPT_BASE}
{product_block}
Create competitor comparison / "alternatives to" SEO content.
Include: comparison table, key differentiators, SEO-optimized headings, target keywords.
Product: {product_name}."""

        output = await xai.generate(system, f"Competitor comparison for: {comp_list}{page_info}", max_tokens=3000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
