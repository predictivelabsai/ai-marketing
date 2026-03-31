"""
POLLY Test Suite — Comprehensive tests for the AI Marketing CLI.

Covers:
  1. Unit tests: agent registration, tool definitions, command parsing, session context
  2. Integration tests: XAI API connectivity and live agent execution
  3. Results are written to test-results/*.json
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Ensure project root is on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from agents.base import BaseAgent, ToolDefinition, ToolResult, ToolStatus
from agents.registry import AgentRegistry
from context.session import (
    ComplianceDocSet,
    ProductContext,
    SessionContext,
    UserPersona,
)
from tui.components.command_processor import BUILTINS, parse_command

# All agent classes
from agents.content import ContentAgent
from agents.strategy import StrategyAgent
from agents.social import SocialAgent
from agents.cro import CroAgent
from agents.seo import SeoAgent
from agents.ads import AdsAgent
from agents.compliance import ComplianceAgent
from agents.campaign import CampaignAgent
from agents.channels import ChannelsAgent

ALL_AGENT_CLASSES = [
    ContentAgent, StrategyAgent, SocialAgent, CroAgent, SeoAgent,
    AdsAgent, ComplianceAgent, CampaignAgent, ChannelsAgent,
]

RESULTS_DIR = ROOT / "test-results"
RESULTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_results(filename: str, results: dict):
    """Write test results to JSON file."""
    results["timestamp"] = datetime.now().isoformat() + "Z"
    path = RESULTS_DIR / filename
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results written to {path}")


def _fresh_registry() -> AgentRegistry:
    """Create a fresh registry with all agents registered."""
    AgentRegistry.reset()
    reg = AgentRegistry.get()
    for cls in ALL_AGENT_CLASSES:
        reg.register(cls())
    return reg


def _make_context() -> SessionContext:
    """Create a SessionContext with XAI configured if key is available."""
    ctx = SessionContext()
    api_key = os.getenv("XAI_API_KEY", "")
    if api_key:
        from integrations.xai_int import XaiIntegration
        xai = XaiIntegration(api_key=api_key, model=os.getenv("XAI_MODEL", "grok-3-fast"))
        if xai.is_configured():
            ctx.set_integration("xai", xai)
    return ctx


# ===========================================================================
# 1. UNIT TESTS — Agent Registration & Tool Definitions
# ===========================================================================

class TestAgentRegistration:
    """Verify all agents register correctly and expose valid tool definitions."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("unit_agent_registration.json", {
            "test_group": "agent_registration",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "tests": cls._results,
        })

    def setup_method(self):
        self.registry = _fresh_registry()

    def _record(self, name, status, detail=""):
        self.__class__._results.append({"name": name, "status": status, "detail": detail})

    def test_all_nine_agents_registered(self):
        agents = self.registry.all_agents()
        assert len(agents) == 9, f"Expected 9 agents, got {len(agents)}"
        self._record("all_nine_agents_registered", "passed", f"{len(agents)} agents")

    def test_agent_names(self):
        names = sorted(a.name for a in self.registry.all_agents())
        expected = sorted(["content", "strategy", "social", "cro", "seo", "ads",
                          "compliance", "campaign", "channels"])
        assert names == expected, f"Expected {expected}, got {names}"
        self._record("agent_names", "passed", str(names))

    def test_total_tool_count(self):
        total = sum(len(a.get_tools()) for a in self.registry.all_agents())
        assert total >= 50, f"Expected >=50 tools, got {total}"
        self._record("total_tool_count", "passed", f"{total} tools")

    def test_each_agent_has_tools(self):
        for agent in self.registry.all_agents():
            tools = agent.get_tools()
            assert len(tools) > 0, f"Agent '{agent.name}' has no tools"
            self._record(f"{agent.name}_has_tools", "passed", f"{len(tools)} tools")

    def test_tool_definitions_valid(self):
        for agent in self.registry.all_agents():
            for tool in agent.get_tools():
                assert tool.name, f"Tool in {agent.name} has empty name"
                assert tool.description, f"Tool {agent.name}:{tool.name} has empty description"
                assert isinstance(tool.parameters, dict), f"{agent.name}:{tool.name} params not dict"
                assert isinstance(tool.required_integrations, list), f"{agent.name}:{tool.name} integrations not list"
                self._record(f"{agent.name}:{tool.name}_valid", "passed")

    def test_no_duplicate_tool_names(self):
        for agent in self.registry.all_agents():
            names = [t.name for t in agent.get_tools()]
            assert len(names) == len(set(names)), f"Duplicate tool names in {agent.name}: {names}"
            self._record(f"{agent.name}_no_duplicate_tools", "passed")

    def test_resolve_agent_tool(self):
        test_cases = [
            ("content:copywriting", "content", "copywriting"),
            ("compliance:review", "compliance", "review"),
            ("campaign:warmup", "campaign", "warmup"),
            ("channels:report", "channels", "report"),
        ]
        for cmd, expected_agent, expected_tool in test_cases:
            agent, tool = self.registry.resolve(cmd)
            assert agent is not None, f"Agent not found for '{cmd}'"
            assert agent.name == expected_agent, f"Expected agent '{expected_agent}', got '{agent.name}'"
            assert tool == expected_tool, f"Expected tool '{expected_tool}', got '{tool}'"
            self._record(f"resolve_{cmd}", "passed")

    def test_resolve_aliases(self):
        agent, tool = self.registry.resolve("content:copy")
        assert agent is not None and tool == "copywriting", f"Alias 'copy' didn't resolve to 'copywriting'"
        self._record("resolve_alias_copy", "passed")

    def test_resolve_unknown_agent(self):
        agent, tool = self.registry.resolve("nonexistent:tool")
        assert agent is None, "Expected None for unknown agent"
        self._record("resolve_unknown_agent", "passed")

    def test_completions(self):
        completions = self.registry.all_completions()
        assert len(completions) > 50, f"Expected >50 completions, got {len(completions)}"
        assert "content" in completions
        assert "content:copywriting" in completions
        self._record("completions", "passed", f"{len(completions)} completions")


# ===========================================================================
# 2. UNIT TESTS — Command Parser
# ===========================================================================

class TestCommandParser:
    """Verify the agent:tool command parser handles all syntax correctly."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("unit_command_parser.json", {
            "test_group": "command_parser",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "tests": cls._results,
        })

    def _record(self, name, status, detail=""):
        self.__class__._results.append({"name": name, "status": status, "detail": detail})

    def test_basic_command(self):
        cmd = parse_command("content:copywriting topic:test")
        assert cmd.is_valid
        assert cmd.agent == "content"
        assert cmd.tool == "copywriting"
        assert cmd.args == {"topic": "test"}
        self._record("basic_command", "passed")

    def test_quoted_values(self):
        cmd = parse_command('content:copywriting topic:"multi word topic" tone:casual')
        assert cmd.is_valid
        assert cmd.args["topic"] == "multi word topic"
        assert cmd.args["tone"] == "casual"
        self._record("quoted_values", "passed")

    def test_builtin_help(self):
        cmd = parse_command("help content")
        assert cmd.is_valid
        assert cmd.builtin == "help"
        assert cmd.builtin_arg == "content"
        self._record("builtin_help", "passed")

    def test_builtin_exit(self):
        cmd = parse_command("exit")
        assert cmd.is_valid
        assert cmd.builtin == "exit"
        self._record("builtin_exit", "passed")

    def test_quit_maps_to_exit(self):
        cmd = parse_command("quit")
        assert cmd.is_valid
        assert cmd.builtin == "exit"
        self._record("quit_maps_to_exit", "passed")

    def test_empty_input(self):
        cmd = parse_command("")
        assert not cmd.is_valid
        self._record("empty_input_invalid", "passed")

    def test_missing_tool(self):
        cmd = parse_command("content:")
        assert not cmd.is_valid
        self._record("missing_tool_invalid", "passed")

    def test_no_colon(self):
        cmd = parse_command("notacommand")
        assert not cmd.is_valid
        self._record("no_colon_invalid", "passed")

    def test_all_builtins(self):
        for b in BUILTINS:
            cmd = parse_command(b)
            assert cmd.is_valid, f"Builtin '{b}' should be valid"
            self._record(f"builtin_{b}", "passed")

    def test_multiple_args(self):
        cmd = parse_command('campaign:create product:"Gold Note" audience:"HNW" channels:email type:warmup')
        assert cmd.is_valid
        assert cmd.args["product"] == "Gold Note"
        assert cmd.args["audience"] == "HNW"
        assert cmd.args["channels"] == "email"
        assert cmd.args["type"] == "warmup"
        self._record("multiple_args", "passed")


# ===========================================================================
# 3. UNIT TESTS — Session Context
# ===========================================================================

class TestSessionContext:
    """Verify SessionContext, ProductContext, ComplianceDocSet, and UserPersona."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("unit_session_context.json", {
            "test_group": "session_context",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "tests": cls._results,
        })

    def _record(self, name, status, detail=""):
        self.__class__._results.append({"name": name, "status": status, "detail": detail})

    def test_product_context_defaults(self):
        ctx = ProductContext()
        assert not ctx.is_set()
        assert ctx.to_prompt_block() == ""
        self._record("product_context_defaults", "passed")

    def test_product_context_set_from_args(self):
        ctx = ProductContext()
        fields = ctx.set_from_args({
            "company": "ABC Capital",
            "product": "Gold-Linked Note",
            "product_type": "structured-product",
            "jurisdiction": "UK",
            "audience": "HNW investors",
        })
        assert ctx.is_set()
        assert ctx.company == "ABC Capital"
        assert ctx.product == "Gold-Linked Note"
        assert ctx.product_type == "structured-product"
        assert ctx.jurisdiction == "UK"
        assert len(fields) == 5
        self._record("product_context_set_from_args", "passed", str(fields))

    def test_product_context_prompt_block(self):
        ctx = ProductContext()
        ctx.set_from_args({"company": "TestCo", "product": "Bond Fund"})
        block = ctx.to_prompt_block()
        assert "TestCo" in block
        assert "Bond Fund" in block
        assert "Product Context:" in block
        self._record("product_context_prompt_block", "passed")

    def test_compliance_doc_set(self):
        docs = ComplianceDocSet()
        assert docs.to_prompt_block() == ""
        docs.product_description = "A 5-year autocallable note linked to FTSE 100"
        docs.faq = "Q: What is this product? A: ..."
        block = docs.to_prompt_block()
        assert "Product Description" in block
        assert "Faq" in block
        self._record("compliance_doc_set", "passed")

    def test_compliance_doc_set_truncation(self):
        docs = ComplianceDocSet()
        docs.prospectus = "x" * 1000
        block = docs.to_prompt_block()
        assert "..." in block  # Should truncate at 500 chars
        self._record("compliance_doc_set_truncation", "passed")

    def test_compliance_approved_docs(self):
        docs = ComplianceDocSet()
        docs.teaser = "Teaser content here"
        docs.approved_docs["teaser"] = "approved_teaser"
        block = docs.to_prompt_block()
        assert "Approved Documents" in block
        self._record("compliance_approved_docs", "passed")

    def test_user_persona_enum(self):
        assert UserPersona.MANAGEMENT.value == "management"
        assert UserPersona.SALES.value == "sales"
        assert UserPersona.CAMPAIGN.value == "campaign"
        self._record("user_persona_enum", "passed")

    def test_session_context_init(self):
        ctx = SessionContext()
        assert isinstance(ctx.product, ProductContext)
        assert isinstance(ctx.compliance_docs, ComplianceDocSet)
        assert ctx.persona == UserPersona.CAMPAIGN
        assert ctx.campaigns == {}
        self._record("session_context_init", "passed")

    def test_session_context_integrations(self):
        ctx = SessionContext()
        assert ctx.get_integration("xai") is None
        ctx.set_integration("xai", "mock_client")
        assert ctx.get_integration("xai") == "mock_client"
        self._record("session_context_integrations", "passed")


# ===========================================================================
# 4. UNIT TESTS — Compliance Agent Logic (no LLM)
# ===========================================================================

class TestComplianceAgentUnit:
    """Test compliance agent document workflow without LLM calls."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("unit_compliance_workflow.json", {
            "test_group": "compliance_workflow",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "tests": cls._results,
        })

    def _record(self, name, status, detail=""):
        self.__class__._results.append({"name": name, "status": status, "detail": detail})

    def test_submit_document(self):
        agent = ComplianceAgent()
        ctx = SessionContext()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("submit", {
                "doc-type": "teaser",
                "content": "Our new structured product offers...",
                "name": "Q1 Teaser",
            }, ctx)
        )
        assert result.status == ToolStatus.SUCCESS
        assert "PENDING APPROVAL" in result.output
        assert ctx.compliance_docs.teaser == "Our new structured product offers..."
        self._record("submit_document", "passed")

    def test_approve_requires_management(self):
        agent = ComplianceAgent()
        ctx = SessionContext()
        ctx.compliance_docs.teaser = "Content here"
        # Default persona is CAMPAIGN, not MANAGEMENT
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("approve", {"doc-type": "teaser"}, ctx)
        )
        assert result.status == ToolStatus.ERROR
        assert "management" in result.error.lower() or "Only management" in result.error
        self._record("approve_requires_management", "passed")

    def test_approve_with_management_persona(self):
        agent = ComplianceAgent()
        ctx = SessionContext()
        ctx.persona = UserPersona.MANAGEMENT
        ctx.compliance_docs.teaser = "Approved teaser content"
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("approve", {"doc-type": "teaser"}, ctx)
        )
        assert result.status == ToolStatus.SUCCESS
        assert "APPROVED" in result.output
        assert "teaser" in ctx.compliance_docs.approved_docs
        self._record("approve_with_management", "passed")

    def test_approve_empty_doc_fails(self):
        agent = ComplianceAgent()
        ctx = SessionContext()
        ctx.persona = UserPersona.MANAGEMENT
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("approve", {"doc-type": "prospectus"}, ctx)
        )
        assert result.status == ToolStatus.ERROR
        self._record("approve_empty_doc_fails", "passed")

    def test_document_set_view(self):
        agent = ComplianceAgent()
        ctx = SessionContext()
        ctx.compliance_docs.faq = "Some FAQ content"
        ctx.compliance_docs.approved_docs["faq"] = "approved_faq"
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("document-set", {}, ctx)
        )
        assert result.status == ToolStatus.SUCCESS
        assert "FAQ" in result.output
        assert "APPROVED" in result.output
        assert "NOT LOADED" in result.output  # Other docs not loaded
        self._record("document_set_view", "passed")

    def test_missing_required_param(self):
        agent = ComplianceAgent()
        ctx = SessionContext()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("review", {}, ctx)  # Missing 'content'
        )
        assert result.status == ToolStatus.NEEDS_INPUT
        assert "content" in result.follow_up_prompt.lower()
        self._record("missing_required_param", "passed")


# ===========================================================================
# 5. INTEGRATION TESTS — XAI API Connectivity
# ===========================================================================

@pytest.mark.integration
class TestXaiConnectivity:
    """Test XAI/Grok API connectivity and basic generation."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("integration_xai_connectivity.json", {
            "test_group": "xai_connectivity",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "skipped": sum(1 for t in cls._results if t["status"] == "skipped"),
            "tests": cls._results,
        })

    def setup_method(self):
        self.api_key = os.getenv("XAI_API_KEY", "")

    def _record(self, name, status, detail=""):
        self.__class__._results.append({"name": name, "status": status, "detail": detail})

    def test_api_key_present(self):
        assert self.api_key, "XAI_API_KEY not set in .env"
        assert self.api_key.startswith("xai-"), f"Key should start with xai-"
        self._record("api_key_present", "passed")

    def test_xai_integration_configured(self):
        from integrations.xai_int import XaiIntegration
        xai = XaiIntegration()
        assert xai.is_configured(), "XaiIntegration not configured"
        self._record("xai_integration_configured", "passed")

    def test_model_list(self):
        if not self.api_key:
            self._record("model_list", "skipped", "No API key")
            pytest.skip("No XAI_API_KEY")
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        assert len(model_ids) > 0
        self._record("model_list", "passed", f"{len(model_ids)} models: {', '.join(model_ids[:5])}")

    def test_basic_generation(self):
        if not self.api_key:
            self._record("basic_generation", "skipped", "No API key")
            pytest.skip("No XAI_API_KEY")

        from integrations.xai_int import XaiIntegration
        xai = XaiIntegration(model="grok-3-fast")
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            xai.generate(
                system="You are a test assistant. Reply in exactly one short sentence.",
                user="Say hello.",
                max_tokens=50,
            )
        )
        elapsed = time.monotonic() - t0
        assert len(result) > 0, "Empty response"
        self._record("basic_generation", "passed", f"{elapsed:.1f}s — '{result[:80]}'")

    def test_streaming_generation(self):
        if not self.api_key:
            self._record("streaming_generation", "skipped", "No API key")
            pytest.skip("No XAI_API_KEY")

        from integrations.xai_int import XaiIntegration
        xai = XaiIntegration(model="grok-3-fast")

        async def _stream():
            chunks = []
            async for chunk in xai.generate_stream(
                system="You are a test assistant.",
                user="Count from 1 to 5.",
                max_tokens=50,
            ):
                chunks.append(chunk)
            return "".join(chunks)

        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(_stream())
        elapsed = time.monotonic() - t0
        assert len(result) > 0, "Empty stream"
        self._record("streaming_generation", "passed", f"{elapsed:.1f}s — '{result[:80]}'")


# ===========================================================================
# 6. INTEGRATION TESTS — Live Agent Execution
# ===========================================================================

@pytest.mark.integration
class TestAgentExecution:
    """Test actual agent tool execution with live XAI calls."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("integration_agent_execution.json", {
            "test_group": "agent_execution",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "skipped": sum(1 for t in cls._results if t["status"] == "skipped"),
            "tests": cls._results,
        })

    def setup_method(self):
        self.ctx = _make_context()
        self.ctx.product.set_from_args({
            "company": "POLLY Test Corp",
            "product": "5Y Autocallable on FTSE 100",
            "product_type": "structured-product",
            "jurisdiction": "UK",
            "audience": "HNW retail investors",
        })
        self.has_xai = self.ctx.get_integration("xai") is not None

    def _record(self, name, status, detail="", elapsed=0):
        self.__class__._results.append({
            "name": name, "status": status, "detail": detail,
            "elapsed_seconds": round(elapsed, 2),
        })

    def _skip_if_no_xai(self, test_name):
        if not self.has_xai:
            self._record(test_name, "skipped", "No XAI integration")
            pytest.skip("No XAI_API_KEY")

    def test_content_copywriting(self):
        self._skip_if_no_xai("content_copywriting")
        agent = ContentAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("copywriting", {
                "topic": "Structured product capital protection benefits",
                "format": "bullet",
                "tone": "professional",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        assert len(result.output) > 50, "Output too short"
        self._record("content_copywriting", "passed", f"{len(result.output)} chars", elapsed)

    def test_content_teaser(self):
        self._skip_if_no_xai("content_teaser")
        agent = ContentAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("teaser", {
                "product": "5Y Autocallable on FTSE 100",
                "audience": "HNW retail investors",
                "format": "one-pager",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        assert len(result.output) > 100
        self._record("content_teaser", "passed", f"{len(result.output)} chars", elapsed)

    def test_content_faq(self):
        self._skip_if_no_xai("content_faq")
        agent = ContentAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("faq", {
                "product": "5Y Autocallable on FTSE 100",
                "count": "5",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        assert len(result.output) > 100
        self._record("content_faq", "passed", f"{len(result.output)} chars", elapsed)

    def test_compliance_review(self):
        self._skip_if_no_xai("compliance_review")
        agent = ComplianceAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("review", {
                "content": "Invest in our FTSE Autocallable — guaranteed 8% annual returns with zero risk to your capital!",
                "type": "teaser",
                "jurisdiction": "UK",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        # Should flag the misleading "guaranteed" and "zero risk" claims
        output_lower = result.output.lower()
        assert any(w in output_lower for w in ["fail", "misleading", "guaranteed", "issue", "concern", "non-compliant", "revision"]), \
            "Compliance review should flag misleading claims"
        self._record("compliance_review", "passed", f"{len(result.output)} chars — flagged issues", elapsed)

    def test_compliance_risk_warnings(self):
        self._skip_if_no_xai("compliance_risk_warnings")
        agent = ComplianceAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("risk-warnings", {
                "product-type": "structured-product",
                "jurisdiction": "UK",
                "channel": "email",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        output_lower = result.output.lower()
        assert any(w in output_lower for w in ["capital", "risk", "past performance"]), \
            "Risk warnings should mention capital risk"
        self._record("compliance_risk_warnings", "passed", f"{len(result.output)} chars", elapsed)

    def test_strategy_market_research(self):
        self._skip_if_no_xai("strategy_market_research")
        agent = StrategyAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("market-research", {
                "sector": "structured products",
                "region": "UK",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        assert len(result.output) > 100
        self._record("strategy_market_research", "passed", f"{len(result.output)} chars", elapsed)

    def test_campaign_warmup(self):
        self._skip_if_no_xai("campaign_warmup")
        agent = CampaignAgent()
        t0 = time.monotonic()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("warmup", {
                "question": "Do you think gold or equities will outperform in the next six months?",
                "channels": "email,whatsapp",
            }, self.ctx)
        )
        elapsed = time.monotonic() - t0
        assert result.status == ToolStatus.SUCCESS, f"Error: {result.error}"
        assert len(result.output) > 100
        self._record("campaign_warmup", "passed", f"{len(result.output)} chars", elapsed)

    def test_strategy_product_context(self):
        """Test the product-context tool (no LLM needed)."""
        agent = StrategyAgent()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("product-context", {}, self.ctx)
        )
        assert result.status == ToolStatus.SUCCESS
        assert "POLLY Test Corp" in result.output
        self._record("strategy_product_context", "passed")

    def test_channels_whatsapp_status(self):
        """Test WhatsApp channel status (no LLM needed)."""
        agent = ChannelsAgent()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("whatsapp", {"action": "status"}, self.ctx)
        )
        assert result.status == ToolStatus.SUCCESS
        assert "whatsapp" in result.output.lower()
        self._record("channels_whatsapp_status", "passed")

    def test_channels_telegram_authorize(self):
        """Test Telegram authorization info (no LLM needed)."""
        agent = ChannelsAgent()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute("telegram", {"action": "authorize"}, self.ctx)
        )
        assert result.status == ToolStatus.SUCCESS
        assert "Telegram" in result.output
        assert "authorize" in result.output.lower() or "Authorization" in result.output
        self._record("channels_telegram_authorize", "passed")


# ===========================================================================
# 7. INTEGRATION TESTS — End-to-End Workflow
# ===========================================================================

@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test a complete compliance → campaign workflow."""
    _results = []

    @classmethod
    def setup_class(cls):
        cls._results = []

    @classmethod
    def teardown_class(cls):
        _write_results("integration_e2e_workflow.json", {
            "test_group": "e2e_workflow",
            "total_tests": len(cls._results),
            "passed": sum(1 for t in cls._results if t["status"] == "passed"),
            "failed": sum(1 for t in cls._results if t["status"] == "failed"),
            "tests": cls._results,
        })

    def _record(self, name, status, detail=""):
        self.__class__._results.append({"name": name, "status": status, "detail": detail})

    def test_full_document_workflow(self):
        """Submit → reject (wrong persona) → approve (management) → view docs."""
        ctx = SessionContext()
        compliance = ComplianceAgent()
        loop = asyncio.get_event_loop()

        # Step 1: Submit a teaser
        r = loop.run_until_complete(compliance.execute("submit", {
            "doc-type": "teaser",
            "content": "Invest in our new FTSE-linked autocallable note...",
            "name": "Q1 Teaser",
        }, ctx))
        assert r.status == ToolStatus.SUCCESS
        self._record("e2e_step1_submit", "passed")

        # Step 2: Try approve as CAMPAIGN persona — should fail
        r = loop.run_until_complete(compliance.execute("approve", {
            "doc-type": "teaser",
        }, ctx))
        assert r.status == ToolStatus.ERROR
        self._record("e2e_step2_reject_wrong_persona", "passed")

        # Step 3: Switch to management and approve
        ctx.persona = UserPersona.MANAGEMENT
        r = loop.run_until_complete(compliance.execute("approve", {
            "doc-type": "teaser",
        }, ctx))
        assert r.status == ToolStatus.SUCCESS
        assert "teaser" in ctx.compliance_docs.approved_docs
        self._record("e2e_step3_approve_management", "passed")

        # Step 4: View document set
        r = loop.run_until_complete(compliance.execute("document-set", {}, ctx))
        assert r.status == ToolStatus.SUCCESS
        assert "APPROVED" in r.output
        self._record("e2e_step4_view_docset", "passed")

    def test_product_context_workflow(self):
        """Set product context → verify it's accessible across agents."""
        ctx = SessionContext()
        strategy = StrategyAgent()
        loop = asyncio.get_event_loop()

        # Set context
        r = loop.run_until_complete(strategy.execute("product-context", {
            "set": "true",
            "company": "Alpha Securities",
            "product": "ESG Bond Fund",
            "industry": "asset management",
            "audience": "institutional investors",
        }, ctx))
        assert r.status == ToolStatus.SUCCESS
        assert ctx.product.company == "Alpha Securities"
        self._record("e2e_product_context_set", "passed")

        # Verify context is visible
        r = loop.run_until_complete(strategy.execute("product-context", {}, ctx))
        assert "Alpha Securities" in r.output
        assert "ESG Bond Fund" in r.output
        self._record("e2e_product_context_view", "passed")

        # Verify prompt block works
        block = ctx.product.to_prompt_block()
        assert "Alpha Securities" in block
        assert "ESG Bond Fund" in block
        self._record("e2e_product_context_prompt_block", "passed")


# ===========================================================================
# Summary report generation
# ===========================================================================

def pytest_sessionfinish(session, exitstatus):
    """Generate a summary report after all tests complete."""
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "exit_status": exitstatus,
        "total_collected": session.testscollected,
        "results_dir": str(RESULTS_DIR),
        "result_files": sorted(str(f.name) for f in RESULTS_DIR.glob("*.json") if f.name != "summary.json"),
    }
    with open(RESULTS_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
