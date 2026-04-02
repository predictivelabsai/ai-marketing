"""Channel-agnostic message models for the unified API."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChannelSource(str, Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class ChannelMessage(BaseModel):
    """Inbound message -- every channel adapter converts its raw payload into this."""

    source: ChannelSource
    sender_id: str                          # user_id, phone number, telegram chat_id
    text: str
    product_id: Optional[int] = None
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChannelResponse(BaseModel):
    """Outbound response -- returned to the caller and routed to the right channel."""

    source: ChannelSource
    sender_id: str
    session_id: str
    agent: str = ""
    tool: str = ""
    text: str = ""
    status: str = "success"                 # success | error | needs_input
    data: dict[str, Any] = Field(default_factory=dict)
    elapsed_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    """Web UI chat request body."""

    message: str
    session_id: Optional[str] = None
    product_id: Optional[int] = None
