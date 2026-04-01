"""Prompt management service — resolve, cache, and persist agent system prompts."""
import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

# Hardcoded defaults (with {{today}} template var instead of f-string date).
# These match the SYSTEM_PROMPT_BASE in each agent file and serve as fallback
# when the DB is unavailable (TUI mode, tests, first run before seeding).
_DEFAULTS: dict[str, str] = {
    "content": (
        "You are POLLY Content, an AI content specialist for financial product marketing. "
        "Today's date is {{today}}. You create compliant marketing content for financial "
        "advisors and product distributors. All content must be fair, clear, and not misleading "
        "per FCA/MiFID II guidelines. Never make guarantees about returns or performance. "
        "Always include appropriate risk warnings where required."
    ),
    "strategy": (
        "You are POLLY Strategy, an AI strategist for financial product distribution and marketing. "
        "Today's date is {{today}}. You help financial advisors and product manufacturers plan "
        "go-to-market strategies, distribution approaches, and marketing campaigns for financial products. "
        "All strategies must consider MiFID II product governance, target market requirements, "
        "and financial promotion regulations."
    ),
    "compliance": (
        "You are POLLY Compliance, an AI compliance assistant for financial product marketing. "
        "Today's date is {{today}}. You ensure all marketing content complies with MiFID II, "
        "PRIIPs regulations, FCA guidelines, and relevant financial marketing regulations. "
        "You NEVER provide investment advice. You focus on regulatory compliance of marketing materials."
    ),
    "campaign": (
        "You are POLLY Campaign Manager, an AI campaign management assistant for financial product marketing. "
        "Today's date is {{today}}. You help plan, execute, and monitor marketing campaigns "
        "for financial products while ensuring compliance with financial marketing regulations."
    ),
    "channels": (
        "You are POLLY Channel Analyst, an AI assistant that monitors and analyzes marketing performance "
        "across multiple communication channels for financial product campaigns. Today's date is {{today}}. "
        "You consolidate data from email, WhatsApp, Telegram, social media, and CRM systems."
    ),
    "cro": (
        "You are an expert conversion rate optimization (CRO) specialist. "
        "Today's date is {{today}}. "
        "Analyze the provided page data and give specific, actionable recommendations "
        "with priority ratings (high/medium/low) and expected impact. "
        "Reference current best practices and recent industry benchmarks."
    ),
    "seo": (
        "You are an expert SEO specialist. "
        "Today's date is {{today}}. "
        "Provide specific, actionable recommendations with priority ratings and expected impact "
        "on search rankings. Reference current algorithm updates and recent best practices."
    ),
    "ads": (
        "You are an expert paid advertising and growth marketing specialist. "
        "Today's date is {{today}}. "
        "Provide data-driven, actionable recommendations using current platform features and recent benchmarks."
    ),
}

AGENT_NAMES = list(_DEFAULTS.keys())


class PromptService:
    """Singleton service for resolving, caching, and persisting agent prompts."""

    _instance: Optional["PromptService"] = None

    def __init__(self):
        # Cache: (user_id_or_None, agent_name) → prompt_text
        self._cache: dict[tuple[Optional[int], str], str] = {}

    @classmethod
    def get(cls) -> "PromptService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self, agent_name: str, user_id: Optional[int] = None) -> str:
        """
        Resolve the effective system prompt for an agent.

        Order: user override → global DB → hardcoded default.
        Prepends global instructions (_global) if they exist.
        Replaces {{today}} with current date.
        """
        # Resolve agent-specific prompt
        base = self._resolve_base(agent_name, user_id)

        # Resolve global instructions (prepend)
        global_instr = ""
        if user_id:
            global_instr = self._lookup(user_id, "_global") or ""
        if not global_instr:
            global_instr = self._lookup(None, "_global") or ""

        parts = [p for p in [global_instr, base] if p]
        final = "\n\n".join(parts)
        return final.replace("{{today}}", str(date.today()))

    def _resolve_base(self, agent_name: str, user_id: Optional[int]) -> str:
        """Resolve the base prompt without global instructions."""
        # 1. User override
        if user_id:
            user_prompt = self._lookup(user_id, agent_name)
            if user_prompt:
                return user_prompt

        # 2. Global DB default
        global_prompt = self._lookup(None, agent_name)
        if global_prompt:
            return global_prompt

        # 3. Hardcoded fallback
        return _DEFAULTS.get(agent_name, "")

    def _lookup(self, user_id: Optional[int], agent_name: str) -> Optional[str]:
        """Look up a prompt, checking cache first, then DB."""
        key = (user_id, agent_name)
        if key in self._cache:
            return self._cache[key]

        # Try DB
        try:
            text_val = self._db_get(user_id, agent_name)
            if text_val is not None:
                self._cache[key] = text_val
            return text_val
        except Exception as e:
            logger.debug(f"DB lookup failed for {key}: {e}")
            return None

    def _db_get(self, user_id: Optional[int], agent_name: str) -> Optional[str]:
        from sqlalchemy import text
        from utils.db_pool import DatabasePool
        pool = DatabasePool.get()
        with pool.get_session() as session:
            if user_id is None:
                result = session.execute(
                    text("SELECT prompt_text FROM polly.prompts WHERE user_id IS NULL AND agent_name = :a AND is_active = TRUE"),
                    {"a": agent_name},
                )
            else:
                result = session.execute(
                    text("SELECT prompt_text FROM polly.prompts WHERE user_id = :u AND agent_name = :a AND is_active = TRUE"),
                    {"u": user_id, "a": agent_name},
                )
            row = result.fetchone()
            return row[0] if row else None

    # ------------------------------------------------------------------
    # Get all prompts for a user (for the editor UI)
    # ------------------------------------------------------------------

    def get_all_for_user(self, user_id: int) -> dict[str, tuple[str, str]]:
        """
        Return {agent_name: (prompt_text, source)} for all agents.
        source is 'user', 'global', or 'default'.
        Also includes '_global' if it exists.
        """
        result = {}
        for agent_name in AGENT_NAMES + ["_global"]:
            # Check user override
            user_prompt = self._lookup(user_id, agent_name)
            if user_prompt:
                result[agent_name] = (user_prompt, "user")
                continue

            # Check global DB
            global_prompt = self._lookup(None, agent_name)
            if global_prompt:
                result[agent_name] = (global_prompt, "global")
                continue

            # Hardcoded default
            default = _DEFAULTS.get(agent_name, "")
            if default:
                result[agent_name] = (default, "default")

        return result

    def get_global_prompts(self) -> dict[str, str]:
        """Return all global prompts from DB (for admin view)."""
        result = {}
        for agent_name in AGENT_NAMES + ["_global"]:
            prompt = self._lookup(None, agent_name)
            if prompt:
                result[agent_name] = prompt
        return result

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def save_prompt(self, agent_name: str, prompt_text: str, user_id: Optional[int] = None) -> None:
        """Upsert a prompt. user_id=None means global default."""
        from sqlalchemy import text
        from utils.db_pool import DatabasePool
        pool = DatabasePool.get()
        with pool.get_session() as session:
            if user_id is None:
                session.execute(
                    text("""
                        INSERT INTO polly.prompts (user_id, agent_name, prompt_text)
                        VALUES (NULL, :a, :t)
                        ON CONFLICT (agent_name) WHERE user_id IS NULL
                        DO UPDATE SET prompt_text = EXCLUDED.prompt_text, updated_at = NOW()
                    """),
                    {"a": agent_name, "t": prompt_text},
                )
            else:
                session.execute(
                    text("""
                        INSERT INTO polly.prompts (user_id, agent_name, prompt_text)
                        VALUES (:u, :a, :t)
                        ON CONFLICT (user_id, agent_name) WHERE user_id IS NOT NULL
                        DO UPDATE SET prompt_text = EXCLUDED.prompt_text, updated_at = NOW()
                    """),
                    {"u": user_id, "a": agent_name, "t": prompt_text},
                )
        # Update cache
        self._cache[(user_id, agent_name)] = prompt_text

    def delete_user_prompt(self, agent_name: str, user_id: int) -> None:
        """Delete a user override, reverting to global default."""
        from sqlalchemy import text
        from utils.db_pool import DatabasePool
        pool = DatabasePool.get()
        with pool.get_session() as session:
            session.execute(
                text("DELETE FROM polly.prompts WHERE user_id = :u AND agent_name = :a"),
                {"u": user_id, "a": agent_name},
            )
        self._cache.pop((user_id, agent_name), None)

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def reload(self, user_id: Optional[int] = None) -> None:
        """Clear cache. If user_id given, only clear that user's entries."""
        if user_id is not None:
            keys_to_remove = [k for k in self._cache if k[0] == user_id]
            for k in keys_to_remove:
                del self._cache[k]
        else:
            self._cache.clear()

    # ------------------------------------------------------------------
    # Seeding
    # ------------------------------------------------------------------

    def seed_defaults(self) -> int:
        """
        Insert global defaults from hardcoded constants if not already present.
        Returns the number of prompts inserted.
        """
        from sqlalchemy import text
        from utils.db_pool import DatabasePool
        pool = DatabasePool.get()
        count = 0
        with pool.get_session() as session:
            for agent_name, prompt_text in _DEFAULTS.items():
                result = session.execute(
                    text("""
                        INSERT INTO polly.prompts (user_id, agent_name, prompt_text)
                        VALUES (NULL, :a, :t)
                        ON CONFLICT (agent_name) WHERE user_id IS NULL DO NOTHING
                    """),
                    {"a": agent_name, "t": prompt_text},
                )
                if result.rowcount > 0:
                    count += 1
        self._cache.clear()
        return count
