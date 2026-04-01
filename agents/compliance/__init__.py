"""Compliance agent — Document approval workflows and regulatory checks for financial products."""
from datetime import date
from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus


SYSTEM_PROMPT_BASE = (
    "You are POLLY Compliance, an AI compliance assistant for financial product marketing. "
    f"Today's date is {date.today()}. You ensure all marketing content complies with MiFID II, "
    "PRIIPs regulations, FCA guidelines, and relevant financial marketing regulations. "
    "You NEVER provide investment advice. You focus on regulatory compliance of marketing materials."
)


class ComplianceAgent(BaseAgent):
    name = "compliance"
    description = "Document approval, regulatory review, MiFID/PRIIPs compliance"

    def _get_default_prompt(self) -> str:
        return SYSTEM_PROMPT_BASE

    def get_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="review",
                description="Review marketing content for regulatory compliance",
                long_help="Review marketing content against MiFID II, PRIIPs, and FCA regulations. "
                          "Checks for required disclosures, risk warnings, fair/balanced presentation, "
                          "and compliance with target market requirements.",
                aliases=["check"],
                examples=[
                    'compliance:review content:"Guaranteed 10% returns on our structured product"',
                    'compliance:review content:"Capital at risk. Past performance..." type:teaser',
                ],
                required_integrations=["xai"],
                parameters={
                    "content": {"description": "Marketing content to review", "required": True},
                    "type": {"description": "Document type being reviewed", "required": False, "default": "general",
                             "options": ["teaser", "faq", "pitch-deck", "email", "social", "ad", "general"]},
                    "jurisdiction": {"description": "Regulatory jurisdiction", "required": False, "default": "UK",
                                    "options": ["UK", "EU", "US", "APAC"]},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="submit",
                description="Submit a document for compliance approval",
                long_help="Submit a marketing document to the compliance approval queue. "
                          "Documents must be reviewed and approved before use in campaigns.",
                aliases=["send"],
                examples=[
                    'compliance:submit doc-type:teaser content:"Our new structured product..." name:"Q1 Teaser"',
                ],
                required_integrations=[],
                parameters={
                    "doc-type": {"description": "Type of document", "required": True,
                                 "options": ["product-description", "prospectus", "term-sheet", "terms-conditions",
                                            "priips", "mifid-disclosures", "faq", "teaser", "pitch-deck", "market-research"]},
                    "content": {"description": "Document content", "required": True},
                    "name": {"description": "Document name/identifier", "required": False},
                },
                estimated_seconds=2,
            ),
            ToolDefinition(
                name="approve",
                description="Approve a submitted document (management only)",
                long_help="Approve a document in the compliance queue. Requires management persona. "
                          "Once approved, the document becomes part of the compliance-approved set "
                          "that content generation draws from.",
                aliases=[],
                examples=[
                    'compliance:approve doc-type:teaser',
                ],
                required_integrations=[],
                parameters={
                    "doc-type": {"description": "Document type to approve", "required": True,
                                 "options": ["product-description", "prospectus", "term-sheet", "terms-conditions",
                                            "priips", "mifid-disclosures", "faq", "teaser", "pitch-deck", "market-research"]},
                },
                estimated_seconds=1,
            ),
            ToolDefinition(
                name="document-set",
                description="View the current compliance-approved document set",
                long_help="Display all compliance-approved documents and their status. "
                          "These form the foundation from which marketing campaigns can be created.",
                aliases=["docs", "docset"],
                examples=[
                    "compliance:document-set",
                    "compliance:docs",
                ],
                required_integrations=[],
                parameters={},
                estimated_seconds=1,
            ),
            ToolDefinition(
                name="target-market",
                description="Define or review target market assessment",
                long_help="Help define the MiFID II target market and negative target market for a product. "
                          "Covers investor type, knowledge/experience, financial situation, risk tolerance, "
                          "and investment objectives per manufacturer obligations.",
                aliases=["tma"],
                examples=[
                    'compliance:target-market product:"Autocallable on FTSE 100"',
                    'compliance:target-market action:review',
                ],
                required_integrations=["xai"],
                parameters={
                    "product": {"description": "Product to assess", "required": False},
                    "action": {"description": "Define or review", "required": False, "default": "define",
                              "options": ["define", "review"]},
                },
                estimated_seconds=15,
            ),
            ToolDefinition(
                name="risk-warnings",
                description="Generate compliant risk warnings and disclosures",
                long_help="Generate appropriate risk warnings and regulatory disclosures "
                          "based on the product type, jurisdiction, and target market.",
                aliases=["disclaimers"],
                examples=[
                    'compliance:risk-warnings product-type:structured-product jurisdiction:UK',
                    'compliance:risk-warnings product-type:fund',
                ],
                required_integrations=["xai"],
                parameters={
                    "product-type": {"description": "Type of financial product", "required": True,
                                     "options": ["structured-product", "fund", "bond", "etf", "derivative", "general"]},
                    "jurisdiction": {"description": "Regulatory jurisdiction", "required": False, "default": "UK",
                                    "options": ["UK", "EU", "US", "APAC"]},
                    "channel": {"description": "Distribution channel (affects disclosure format)", "required": False,
                               "options": ["email", "social", "web", "print", "whatsapp"]},
                },
                estimated_seconds=10,
            ),
        ]

    async def execute(self, tool_name: str, args: dict[str, str], context) -> ToolResult:
        tool = self.resolve_tool(tool_name)
        for pname, pinfo in (tool.parameters if tool else {}).items():
            if pinfo.get("required") and pname not in args:
                return ToolResult(status=ToolStatus.NEEDS_INPUT, follow_up_prompt=f"Missing required parameter: {pname}")

        prompt_base = self._get_system_prompt(context)

        if tool_name == "review":
            return await self._review(args, context, prompt_base)
        elif tool_name == "submit":
            return self._submit(args, context)
        elif tool_name == "approve":
            return self._approve(args, context)
        elif tool_name == "document-set":
            return self._document_set(context)
        elif tool_name == "target-market":
            return await self._target_market(args, context, prompt_base)
        elif tool_name == "risk-warnings":
            return await self._risk_warnings(args, context, prompt_base)

        return ToolResult(status=ToolStatus.ERROR, error=f"Unknown tool: {tool_name}")

    async def _review(self, args, context, prompt_base) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured. Set XAI_API_KEY in .env")

        content = args["content"]
        doc_type = args.get("type", "general")
        jurisdiction = args.get("jurisdiction", "UK")
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        system = f"""{prompt_base}
{product_block}
Review the following {doc_type} marketing content for compliance with {jurisdiction} financial regulations.

Check for:
1. Misleading claims or guarantees of returns
2. Missing risk warnings or disclosures
3. Fair and balanced presentation of risks vs benefits
4. Compliance with target market restrictions
5. MiFID II / PRIIPs / FCA requirements for {doc_type} materials
6. Appropriate use of past performance disclaimers
7. Clear, fair, and not misleading language

Provide a compliance assessment with:
- PASS / FAIL / NEEDS REVISION verdict
- Specific issues found (with line references)
- Required changes for compliance
- Suggested compliant alternatives"""

        output = await xai.generate(system, f"Review this content:\n\n{content}")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    def _submit(self, args, context) -> ToolResult:
        doc_type = args["doc-type"].replace("-", "_")
        content = args["content"]
        name = args.get("name", doc_type)

        # Store in compliance docs pending area
        if hasattr(context, 'compliance_docs'):
            setattr(context.compliance_docs, doc_type, content)
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Document '{name}' ({doc_type}) submitted for compliance review.\n"
                       f"Content length: {len(content)} characters.\n"
                       f"Status: PENDING APPROVAL\n\n"
                       f"A management user must run 'compliance:approve doc-type:{args['doc-type']}' to approve."
            )
        return ToolResult(status=ToolStatus.ERROR, error="Compliance document set not initialized in session context.")

    def _approve(self, args, context) -> ToolResult:
        from context.session import UserPersona
        if hasattr(context, 'persona') and context.persona != UserPersona.MANAGEMENT:
            return ToolResult(
                status=ToolStatus.ERROR,
                error="Only management persona can approve documents. Current persona: " + context.persona.value
            )

        doc_type = args["doc-type"].replace("-", "_")
        if hasattr(context, 'compliance_docs'):
            content = getattr(context.compliance_docs, doc_type, "")
            if not content:
                return ToolResult(status=ToolStatus.ERROR, error=f"No document of type '{doc_type}' found in submission queue.")
            context.compliance_docs.approved_docs[doc_type] = f"approved_{doc_type}"
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Document '{doc_type}' APPROVED.\n"
                       f"It is now part of the compliance-approved document set.\n"
                       f"Content can be generated based on this approved document."
            )
        return ToolResult(status=ToolStatus.ERROR, error="Compliance document set not initialized.")

    def _document_set(self, context) -> ToolResult:
        if not hasattr(context, 'compliance_docs'):
            return ToolResult(status=ToolStatus.SUCCESS, output="No compliance document set initialized.")

        docs = context.compliance_docs
        lines = ["Compliance-Approved Document Set:", ""]
        doc_fields = [
            ("product_description", "Product Description"),
            ("prospectus", "Prospectus / Offering Document"),
            ("term_sheet", "Term Sheet / Final Terms"),
            ("terms_conditions", "Terms & Conditions"),
            ("priips", "PRIIPs Document"),
            ("mifid_disclosures", "MiFID Disclosures"),
            ("faq", "FAQ"),
            ("teaser", "Teaser"),
            ("pitch_deck", "Pitch Deck"),
            ("market_research", "Market Research"),
        ]

        for field_name, label in doc_fields:
            content = getattr(docs, field_name, "")
            approved = field_name in docs.approved_docs
            if content:
                status = "[green]APPROVED[/green]" if approved else "[yellow]PENDING[/yellow]"
                lines.append(f"  {label:<35} {status}  ({len(content)} chars)")
            else:
                lines.append(f"  {label:<35} [dim]NOT LOADED[/dim]")

        lines.append("")
        if docs.approved_docs:
            lines.append(f"  Total approved: {len(docs.approved_docs)}")
        else:
            lines.append("  No documents approved yet.")
        return ToolResult(status=ToolStatus.SUCCESS, output="\n".join(lines))

    async def _target_market(self, args, context, prompt_base) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        product = args.get("product", "")
        action = args.get("action", "define")
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        if action == "review" and hasattr(context, 'compliance_docs'):
            existing = f"Current target market: {context.product.target_market}" if context.product.target_market else ""
            existing += f"\nNegative target: {context.product.negative_target}" if context.product.negative_target else ""
        else:
            existing = ""

        system = f"""{prompt_base}
{product_block}
{existing}
{'Review the existing' if action == 'review' else 'Define a'} MiFID II target market assessment.

Cover:
1. Target Market (positive):
   - Type of client (retail, professional, eligible counterparty)
   - Knowledge and experience requirements
   - Financial situation (ability to bear losses)
   - Risk tolerance and compatibility
   - Investment objectives and needs
2. Negative Target Market:
   - Client types for whom the product is NOT suitable
   - Specific exclusion criteria
3. Distribution Strategy:
   - Appropriate distribution channels
   - Information provision requirements"""

        prompt = f"Target market assessment for: {product}" if product else "Review current target market assessment"
        output = await xai.generate(system, prompt, max_tokens=2000)
        return ToolResult(status=ToolStatus.SUCCESS, output=output)

    async def _risk_warnings(self, args, context, prompt_base) -> ToolResult:
        xai = context.get_integration("xai")
        if not xai:
            return ToolResult(status=ToolStatus.ERROR, error="XAI integration not configured.")

        product_type = args["product-type"]
        jurisdiction = args.get("jurisdiction", "UK")
        channel = args.get("channel", "")
        product_block = context.product.to_prompt_block() if context.product.is_set() else ""

        channel_note = f"Format for {channel} channel." if channel else ""
        system = f"""{prompt_base}
{product_block}
Generate required risk warnings and regulatory disclosures for a {product_type} in {jurisdiction}.
{channel_note}

Include:
1. Capital at risk warning
2. Past performance disclaimer
3. Product-specific risk factors
4. Regulatory status disclosure
5. Target market suitability notice
6. Any jurisdiction-specific required statements
7. Complaint handling / ombudsman reference if applicable

Format appropriately for the distribution channel."""

        output = await xai.generate(system, f"Risk warnings for {product_type} ({jurisdiction})")
        return ToolResult(status=ToolStatus.SUCCESS, output=output)
