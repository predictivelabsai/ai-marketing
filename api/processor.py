"""
POLLY Unified Processing Core -- single entry point for all channels.

Every channel (web, WhatsApp, Telegram) converts its payload into a
ChannelMessage, calls process(), and routes the ChannelResponse back.
"""
from __future__ import annotations

import logging
import time

from api.models import ChannelMessage, ChannelResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton runtime -- agents + integrations initialized once at startup
# ---------------------------------------------------------------------------

_runtime = None  # set after _Runtime class definition


class _Runtime:
    """Holds the shared AgentRegistry and SessionContext factory."""

    def __init__(self):
        from agents.registry import AgentRegistry
        from context.session import SessionContext

        self.registry = AgentRegistry.get()
        self._base_context = SessionContext()
        self._init_integrations()
        self._register_agents()
        logger.info(
            "Runtime ready: %d agents, %d tools",
            len(self.registry.all_agents()),
            sum(len(a.get_tools()) for a in self.registry.all_agents()),
        )

    def _init_integrations(self) -> None:
        from integrations.xai_int import XaiIntegration
        from integrations.arcade_int import ArcadeIntegration
        from integrations.playwright_int import PlaywrightIntegration
        from integrations.composio_int import ComposioIntegration
        from integrations.rag_int import RagIntegration

        for name, cls in [
            ("xai", XaiIntegration),
            ("arcade", ArcadeIntegration),
            ("playwright", PlaywrightIntegration),
            ("composio", ComposioIntegration),
            ("rag", RagIntegration),
        ]:
            backend = cls()
            if backend.is_configured():
                self._base_context.set_integration(name, backend)
                logger.info("Integration ready: %s", name)

    def _register_agents(self) -> None:
        from agents.content import ContentAgent
        from agents.strategy import StrategyAgent
        from agents.social import SocialAgent
        from agents.cro import CroAgent
        from agents.seo import SeoAgent
        from agents.ads import AdsAgent
        from agents.compliance import ComplianceAgent
        from agents.campaign import CampaignAgent
        from agents.channels import ChannelsAgent

        for AgentClass in [
            ContentAgent, StrategyAgent, SocialAgent, CroAgent,
            SeoAgent, AdsAgent, ComplianceAgent, CampaignAgent, ChannelsAgent,
        ]:
            self.registry.register(AgentClass())

    @property
    def context(self):
        """Return the shared context (integrations are reusable across requests)."""
        return self._base_context


def get_runtime() -> _Runtime:
    """Lazy-init singleton runtime."""
    global _runtime
    if _runtime is None:
        _runtime = _Runtime()
    return _runtime


# ---------------------------------------------------------------------------
# Message persistence
# ---------------------------------------------------------------------------

def _persist_message(msg: ChannelMessage, direction: str = "inbound",
                     response_text: str = "") -> None:
    """Store message in polly.messages (fire-and-forget, never blocks)."""
    try:
        from utils.db_pool import DatabasePool
        from sqlalchemy import text
        pool = DatabasePool.get()
        with pool.get_session() as s:
            s.execute(text("""
                INSERT INTO polly.messages
                    (source, sender_id, direction, content, product_id, session_id)
                VALUES
                    (:source, :sender_id, :direction, :content, :product_id, :session_id)
            """), {
                "source": msg.source.value,
                "sender_id": msg.sender_id,
                "direction": direction,
                "content": msg.text if direction == "inbound" else response_text,
                "product_id": msg.product_id,
                "session_id": msg.session_id,
            })
    except Exception as e:
        logger.warning("Failed to persist message: %s", e)


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

async def process(msg: ChannelMessage) -> ChannelResponse:
    """
    Process any inbound message -- the single entry point for all channels.

    1. Parse the text as an agent:tool command
    2. Resolve agent + tool via registry
    3. Execute the agent
    4. Return a ChannelResponse
    """
    rt = get_runtime()
    t0 = time.monotonic()

    # Persist inbound
    _persist_message(msg, direction="inbound")

    # Parse command
    from tui.components.command_processor import parse_command
    parsed = parse_command(msg.text)

    if not parsed.is_valid:
        # Not a structured command -- treat as free-text chat
        return await _handle_freetext(msg, rt, t0)

    if parsed.builtin:
        return _handle_builtin(msg, parsed, rt, t0)

    # Resolve agent:tool
    agent, tool_name = rt.registry.resolve(f"{parsed.agent}:{parsed.tool}")
    if not agent:
        return ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id, status="error",
            text=f"Unknown agent: '{parsed.agent}'. Type 'help' to see available agents.",
            elapsed_seconds=time.monotonic() - t0,
        )
    if not tool_name:
        return ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id, status="error",
            text=f"Unknown tool: '{parsed.agent}:{parsed.tool}'. Type 'help {parsed.agent}' to see tools.",
            elapsed_seconds=time.monotonic() - t0,
        )

    # Execute
    try:
        result = await agent.execute(tool_name, parsed.args, rt.context)
        elapsed = time.monotonic() - t0

        # Attach RAG source documents if available
        response_data = result.data or {}
        rag = rt.context.get_integration("rag")
        if rag and parsed.agent in ("content", "compliance"):
            try:
                sources = rag.retrieve(
                    query=msg.text,
                    product_id=msg.product_id,
                    top_k=4,
                )
                response_data["sources"] = sources
            except Exception:
                pass

        resp = ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id,
            agent=parsed.agent, tool=tool_name,
            text=result.output or result.error or "",
            status=result.status.value,
            data=response_data,
            elapsed_seconds=round(elapsed, 2),
        )

        # Persist outbound
        _persist_message(msg, direction="outbound", response_text=resp.text)
        return resp

    except Exception as e:
        logger.exception("Agent execution failed: %s:%s", parsed.agent, tool_name)
        return ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id,
            agent=parsed.agent, tool=tool_name,
            status="error",
            text=f"Error executing {parsed.agent}:{tool_name}: {str(e)[:200]}",
            elapsed_seconds=round(time.monotonic() - t0, 2),
        )


async def _handle_freetext(msg: ChannelMessage, rt: _Runtime,
                           t0: float) -> ChannelResponse:
    """
    Handle free-text messages that aren't agent:tool commands.

    Uses RAG to retrieve relevant documents, queries DB for product info,
    and answers any natural language question with full context.
    """
    xai = rt.context.get_integration("xai")
    if not xai:
        return ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id, status="error",
            text="XAI integration not configured. Use agent:tool commands instead.",
            elapsed_seconds=round(time.monotonic() - t0, 2),
        )

    # 1. RAG retrieval -- pull relevant document sections
    rag = rt.context.get_integration("rag")
    doc_context = ""
    sources = []
    if rag:
        try:
            sources = rag.retrieve(query=msg.text, top_k=6)
            if sources:
                doc_sections = []
                for s in sources[:6]:
                    doc_sections.append(
                        f"[{s.get('filename', '?')} | {s.get('section_name', '')}]\n"
                        f"{s.get('content', '')[:600]}"
                    )
                doc_context = (
                    "\n\n--- RETRIEVED DOCUMENTS ---\n"
                    + "\n\n".join(doc_sections)
                    + "\n--- END DOCUMENTS ---\n"
                )
        except Exception:
            pass

    # 2. DB context -- product and document counts
    db_context = ""
    try:
        from utils.db_pool import DatabasePool
        from sqlalchemy import text
        pool = DatabasePool.get()
        with pool.get_session() as s:
            products = s.execute(text(
                "SELECT id, name, product_type, jurisdiction, status "
                "FROM polly.products ORDER BY id"
            )).fetchall()
            doc_count = s.execute(text(
                "SELECT COUNT(*) FROM polly_rag_hierarchical.documents"
            )).scalar()
            approved_count = s.execute(text(
                "SELECT COUNT(*) FROM polly_rag_hierarchical.documents WHERE approved = true"
            )).scalar()

            if products:
                prod_lines = [f"  - {r[1]} (id={r[0]}, type={r[2]}, jurisdiction={r[3]}, status={r[4]})"
                              for r in products]
                db_context = (
                    f"\n\nProducts in database ({len(products)}):\n"
                    + "\n".join(prod_lines)
                    + f"\n\nDocuments: {doc_count} total, {approved_count} approved"
                )
    except Exception:
        pass

    # 3. Build agent list for context
    agents_info = []
    for a in rt.registry.all_agents():
        tools = ", ".join(t.name for t in a.get_tools())
        agents_info.append(f"- {a.name}: {a.description} (tools: {tools})")
    agents_block = "\n".join(agents_info)

    system = (
        "You are POLLY, an AI marketing assistant for financial advisors. "
        "You help create compliant marketing content for structured financial products.\n\n"
        "You have access to product documents via RAG and a database of products.\n"
        "Answer the user's question using the retrieved documents and database info below.\n"
        "If the question is about creating content, generating materials, or running a tool, "
        "answer directly AND suggest the exact agent:tool command they can use.\n"
        "Be specific, use facts from the documents, and be concise.\n\n"
        f"Available agents and tools:\n{agents_block}\n"
        f"{db_context}\n"
        f"{doc_context}\n"
    )

    try:
        response_text = await xai.generate(
            system=system, user=msg.text, max_tokens=2000
        )
        elapsed = time.monotonic() - t0

        response_data = {}
        if sources:
            response_data["sources"] = sources

        resp = ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id,
            text=response_text, status="success",
            data=response_data,
            elapsed_seconds=round(elapsed, 2),
        )
        _persist_message(msg, direction="outbound", response_text=resp.text)
        return resp
    except Exception as e:
        return ChannelResponse(
            source=msg.source, sender_id=msg.sender_id,
            session_id=msg.session_id, status="error",
            text=f"Error: {str(e)[:200]}",
            elapsed_seconds=round(time.monotonic() - t0, 2),
        )


def _handle_builtin(msg: ChannelMessage, parsed, rt: _Runtime,
                    t0: float) -> ChannelResponse:
    """Handle builtin commands (help, agents, etc.)."""
    if parsed.builtin == "agents":
        lines = []
        for a in rt.registry.all_agents():
            tools = ", ".join(t.name for t in a.get_tools())
            lines.append(f"**{a.name}** -- {a.description}\n  Tools: {tools}")
        text = "\n\n".join(lines)

    elif parsed.builtin == "help":
        if parsed.builtin_arg:
            # Help for specific agent or agent:tool
            agent, tool_name = rt.registry.resolve(parsed.builtin_arg)
            if agent and tool_name:
                td = agent.resolve_tool(tool_name)
                text = (
                    f"**{agent.name}:{td.name}**\n"
                    f"{td.description}\n"
                    f"{td.long_help or ''}\n\n"
                    f"Parameters: {', '.join(f'{k} ({v.get('description','')})' for k,v in td.parameters.items())}\n"
                    f"Examples: {', '.join(td.examples) if td.examples else 'none'}"
                )
            elif agent:
                tools = "\n".join(
                    f"  - **{t.name}**: {t.description}"
                    for t in agent.get_tools()
                )
                text = f"**{agent.name}** -- {agent.description}\n\nTools:\n{tools}"
            else:
                text = f"Unknown: '{parsed.builtin_arg}'. Type 'agents' to see all."
        else:
            text = (
                "**POLLY Commands:**\n"
                "- `agent:tool key:value` -- run a marketing tool\n"
                "- `agents` -- list all agents and tools\n"
                "- `help agent` -- help for an agent\n"
                "- `help agent:tool` -- help for a specific tool\n\n"
                "Or just type a question and POLLY will help."
            )
    else:
        text = f"Command '{parsed.builtin}' is not available in chat."

    return ChannelResponse(
        source=msg.source, sender_id=msg.sender_id,
        session_id=msg.session_id, text=text, status="success",
        elapsed_seconds=round(time.monotonic() - t0, 2),
    )
