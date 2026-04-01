"""POLLY session context holding shared state across agents."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


@dataclass
class ProductContext:
    """Shared product context that all agents can read for LLM prompt injection."""
    company: str = ""
    product: str = ""
    audience: str = ""
    tone: str = "professional"
    industry: str = ""
    website: str = ""
    competitors: list[str] = field(default_factory=list)
    value_proposition: str = ""
    extra: dict[str, str] = field(default_factory=dict)
    # Financial-product-specific fields
    product_type: str = ""          # e.g. "structured-product", "fund", "bond", "etf"
    jurisdiction: str = ""          # regulatory jurisdiction
    target_market: str = ""         # MiFID target market definition
    negative_target: str = ""       # negative target market
    distribution_strategy: str = "" # how the product is distributed
    risk_level: str = ""            # product risk level

    def is_set(self) -> bool:
        return bool(self.company or self.product)

    def to_prompt_block(self) -> str:
        """Render as a block suitable for injecting into LLM system prompts."""
        if not self.is_set():
            return ""
        lines = ["Product Context:"]
        if self.company:
            lines.append(f"  Company: {self.company}")
        if self.product:
            lines.append(f"  Product: {self.product}")
        if self.audience:
            lines.append(f"  Target Audience: {self.audience}")
        if self.tone:
            lines.append(f"  Tone: {self.tone}")
        if self.industry:
            lines.append(f"  Industry: {self.industry}")
        if self.website:
            lines.append(f"  Website: {self.website}")
        if self.competitors:
            lines.append(f"  Competitors: {', '.join(self.competitors)}")
        if self.value_proposition:
            lines.append(f"  Value Proposition: {self.value_proposition}")
        if self.product_type:
            lines.append(f"  Product Type: {self.product_type}")
        if self.jurisdiction:
            lines.append(f"  Jurisdiction: {self.jurisdiction}")
        if self.target_market:
            lines.append(f"  Target Market: {self.target_market}")
        if self.negative_target:
            lines.append(f"  Negative Target Market: {self.negative_target}")
        if self.distribution_strategy:
            lines.append(f"  Distribution Strategy: {self.distribution_strategy}")
        if self.risk_level:
            lines.append(f"  Risk Level: {self.risk_level}")
        for k, v in self.extra.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    def set_from_args(self, args: dict[str, str]) -> list[str]:
        """Set fields from key:value args. Returns list of fields that were set."""
        set_fields = []
        known = {
            "company", "product", "audience", "tone", "industry",
            "website", "value_proposition", "value-proposition",
            "product_type", "product-type",
            "jurisdiction",
            "target_market", "target-market",
            "negative_target", "negative-target",
            "distribution_strategy", "distribution-strategy",
            "risk_level", "risk-level",
        }
        for key, value in args.items():
            normalized = key.replace("-", "_")
            if normalized == "competitors":
                self.competitors = [c.strip() for c in value.split(",")]
                set_fields.append("competitors")
            elif normalized in known:
                setattr(self, normalized, value)
                set_fields.append(normalized)
            else:
                self.extra[key] = value
                set_fields.append(key)
        return set_fields


@dataclass
class ComplianceDocSet:
    """Tracks compliance-approved documents for a product."""
    product_description: str = ""       # (4) Product Description
    prospectus: str = ""               # (5) Prospectus / Offering Document
    term_sheet: str = ""               # (6) Term Sheet / Final Terms
    terms_conditions: str = ""         # (7) Terms and Conditions
    priips: str = ""                   # PRIIPs Document
    mifid_disclosures: str = ""        # MiFID disclosures
    faq: str = ""                      # (1) FAQ
    teaser: str = ""                   # (2) Teaser
    pitch_deck: str = ""              # (3) Pitch Deck
    market_research: str = ""          # (8) Market research
    approved_docs: dict[str, str] = field(default_factory=dict)  # doc_name -> approved_version_path

    def to_prompt_block(self) -> str:
        """Render loaded docs as context block for LLM prompts."""
        lines = ["Compliance Document Set:"]
        for field_name in ["product_description", "prospectus", "term_sheet", "terms_conditions",
                          "priips", "mifid_disclosures", "faq", "teaser", "pitch_deck", "market_research"]:
            val = getattr(self, field_name)
            if val:
                label = field_name.replace("_", " ").title()
                # Truncate for prompt injection (first 500 chars)
                snippet = val[:500] + "..." if len(val) > 500 else val
                lines.append(f"  {label}: {snippet}")
        if self.approved_docs:
            lines.append(f"  Approved Documents: {', '.join(self.approved_docs.keys())}")
        return "\n".join(lines) if len(lines) > 1 else ""


class UserPersona(Enum):
    MANAGEMENT = "management"
    SALES = "sales"
    CAMPAIGN = "campaign"


class SessionContext:
    """Holds integration clients and shared state for a POLLY session."""

    def __init__(self):
        self.product = ProductContext()
        self.compliance_docs = ComplianceDocSet()
        self.persona: UserPersona = UserPersona.CAMPAIGN
        self.user_id: Optional[int] = None
        self.campaigns: dict[str, Any] = {}
        self.scratch: dict[str, Any] = {}
        self._integrations: dict[str, Any] = {}

    def get_integration(self, name: str) -> Optional[Any]:
        return self._integrations.get(name)

    def set_integration(self, name: str, client: Any) -> None:
        self._integrations[name] = client

    @property
    def xai(self) -> Optional[Any]:
        return self._integrations.get("xai")

    @property
    def arcade(self) -> Optional[Any]:
        return self._integrations.get("arcade")

    @property
    def playwright(self) -> Optional[Any]:
        return self._integrations.get("playwright")

    @property
    def composio(self) -> Optional[Any]:
        return self._integrations.get("composio")
