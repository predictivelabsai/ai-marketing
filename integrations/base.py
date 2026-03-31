"""Base integration backend abstraction."""
from abc import ABC, abstractmethod


class IntegrationBackend(ABC):
    """Abstract base for all integration wrappers."""

    name: str = ""

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if this integration has the necessary credentials/config."""
        ...

    def status_label(self) -> str:
        return "ready" if self.is_configured() else "not configured"
