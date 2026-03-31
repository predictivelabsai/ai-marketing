"""Arcade.dev integration wrapper."""
import os
from typing import Any, Optional

from .base import IntegrationBackend


class ArcadeIntegration(IntegrationBackend):
    """Thin wrapper around arcadepy for social posting."""

    name = "arcade"

    def __init__(self, api_key: Optional[str] = None, user_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("ARCADE_API_KEY", "")
        self.user_id = user_id or os.getenv("ARCADE_USER_ID", "")
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.user_id)

    @property
    def client(self):
        if self._client is None:
            from arcadepy import Arcade
            self._client = Arcade(api_key=self.api_key)
        return self._client

    def execute_tool(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """Execute an Arcade tool and return a result dict."""
        try:
            response = self.client.tools.execute(
                tool_name=tool_name,
                input=inputs,
                user_id=self.user_id,
            )
            return {
                "success": response.success,
                "response": response.output.value if response.output else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
