"""
Telegram Bot adapter for POLLY.

Receives messages via webhook, processes through unified pipeline,
sends response back via Telegram Bot API.

Setup:
  1. Create bot via @BotFather on Telegram -> get _get_token()
  2. Set env vars: TELEGRAM__get_token()
  3. Set webhook: POST https://api.telegram.org/bot<TOKEN>/setWebhook
     Body: {"url": "https://your-domain.com/webhook/telegram"}
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

def _get_token() -> str:
    return os.getenv("TELEGRAM__get_token()", "").strip()


def _get_api_url() -> str:
    return f"https://api.telegram.org/bot{_get_token()}"


def is_configured() -> bool:
    return bool(_get_token())


def parse_update(payload: dict) -> dict | None:
    """
    Parse a Telegram Update object into {chat_id, text, first_name}.
    Returns None if the update doesn't contain a text message.
    """
    message = payload.get("message") or payload.get("edited_message")
    if not message:
        return None

    text = message.get("text")
    if not text:
        return None

    chat = message.get("chat", {})
    user = message.get("from", {})

    return {
        "chat_id": str(chat.get("id", "")),
        "text": text,
        "first_name": user.get("first_name", ""),
        "username": user.get("username", ""),
        "message_id": message.get("message_id"),
    }


async def send_message(chat_id: str, text: str) -> bool:
    """Send a text message back to a Telegram chat."""
    token = _get_token()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set, cannot send message")
        return False
    logger.info("Sending to chat_id=%s, token=%s..., url=%s",
                chat_id, token[:10], _get_api_url()[:50])

    # Telegram max message length is 4096 chars
    chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]

    async with httpx.AsyncClient(timeout=30) as client:
        for chunk in chunks:
            resp = await client.post(
                f"{_get_api_url()}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "Markdown",
                },
            )
            if resp.status_code != 200:
                logger.error("Telegram sendMessage failed: %s %s",
                             resp.status_code, resp.text)
                return False
    return True


async def set_webhook(webhook_url: str) -> dict:
    """Set the Telegram webhook URL. Call once during deployment."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{_get_api_url()}/setWebhook",
            json={"url": webhook_url},
        )
        return resp.json()


async def get_me() -> dict:
    """Get bot info (verify token works)."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{_get_api_url()}/getMe")
        return resp.json()
