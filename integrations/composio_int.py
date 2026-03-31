"""Composio integration wrapper (stub — activate when API key available)."""
import os
from typing import Any, Optional

from .base import IntegrationBackend


class ComposioIntegration(IntegrationBackend):
    """Wrapper for Composio SDK (GA4, Mailchimp, Semrush, etc.)."""

    name = "composio"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY", "")
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def execute_action(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a Composio action. Returns result dict."""
        if not self.is_configured():
            return {"success": False, "error": "Composio API key not configured. Set COMPOSIO_API_KEY in .env"}
        # TODO: Wire up composio SDK when key is available
        return {"success": False, "error": f"Composio action '{action}' not yet implemented"}
