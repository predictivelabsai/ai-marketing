"""
POLLY API Routes -- FastAPI endpoints for the unified channel backend.

Run standalone: python api/main.py (port 5056)
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.models import ChannelMessage, ChannelResponse, ChannelSource, ChatRequest
from api.processor import process

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

api = FastAPI(
    title="POLLY Channel API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Web chat endpoint
# ---------------------------------------------------------------------------

@api.post("/chat", response_model=ChannelResponse)
async def chat(req: ChatRequest, user_id: str = "web-anonymous"):
    """Process a web chat message through the unified pipeline."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    msg = ChannelMessage(
        source=ChannelSource.WEB,
        sender_id=user_id,
        text=req.message.strip(),
        product_id=req.product_id,
        session_id=req.session_id or "",
    )
    return await process(msg)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@api.get("/health")
async def health():
    from api.processor import get_runtime
    rt = get_runtime()
    agents = rt.registry.all_agents()
    return {
        "status": "ok",
        "agents": len(agents),
        "tools": sum(len(a.get_tools()) for a in agents),
        "integrations": list(rt.context._integrations.keys()),
    }


# ---------------------------------------------------------------------------
# Agent discovery
# ---------------------------------------------------------------------------

@api.get("/agents")
async def list_agents():
    """List all available agents and their tools."""
    from api.processor import get_runtime
    rt = get_runtime()
    result = []
    for a in rt.registry.all_agents():
        tools = []
        for t in a.get_tools():
            tools.append({
                "name": t.name,
                "description": t.description,
                "aliases": t.aliases,
                "parameters": t.parameters,
                "examples": t.examples,
            })
        result.append({
            "name": a.name,
            "description": a.description,
            "tools": tools,
        })
    return {"agents": result}


# ---------------------------------------------------------------------------
# Telegram webhook
# ---------------------------------------------------------------------------

@api.post("/webhook/telegram")
async def telegram_incoming(payload: dict):
    """Receive Telegram messages via Bot API webhook."""
    from api.channels.telegram import parse_update, send_message, is_configured

    if not is_configured():
        logger.warning("Telegram webhook hit but TELEGRAM_BOT_TOKEN not set")
        return {"status": "not_configured"}

    parsed = parse_update(payload)
    if not parsed:
        return {"status": "ignored"}

    logger.info("Telegram message from %s: %s", parsed["username"], parsed["text"][:50])

    msg = ChannelMessage(
        source=ChannelSource.TELEGRAM,
        sender_id=parsed["chat_id"],
        text=parsed["text"],
    )

    response = await process(msg)
    await send_message(parsed["chat_id"], response.text)
    return {"status": "ok"}


@api.post("/webhook/telegram/setup")
async def telegram_setup_webhook():
    """Set the Telegram webhook URL. Call once after deployment."""
    import os
    from api.channels.telegram import set_webhook, is_configured

    if not is_configured():
        raise HTTPException(status_code=400, detail="TELEGRAM_BOT_TOKEN not set")

    base_url = os.getenv("API_BASE_URL", "")
    if not base_url:
        raise HTTPException(status_code=400,
                            detail="Set API_BASE_URL env var (e.g. https://api.polly.predictivelabs.ai)")

    webhook_url = f"{base_url.rstrip('/')}/webhook/telegram"
    result = await set_webhook(webhook_url)
    return {"webhook_url": webhook_url, "telegram_response": result}


@api.get("/webhook/telegram/status")
async def telegram_status():
    """Check Telegram bot info and webhook status."""
    from api.channels.telegram import get_me, is_configured

    if not is_configured():
        return {"configured": False}

    try:
        info = await get_me()
        return {"configured": True, "bot": info.get("result", {})}
    except Exception as e:
        return {"configured": True, "error": str(e)}


# ---------------------------------------------------------------------------
# WhatsApp webhook (placeholder -- activated when Meta key is configured)
# ---------------------------------------------------------------------------

@api.get("/webhook/whatsapp")
async def whatsapp_verify(hub_mode: str = "", hub_verify_token: str = "",
                          hub_challenge: str = ""):
    """Meta webhook verification (GET request during setup)."""
    import os
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return int(hub_challenge) if hub_challenge.isdigit() else hub_challenge
    raise HTTPException(status_code=403, detail="Verification failed")


@api.post("/webhook/whatsapp")
async def whatsapp_incoming(payload: dict):
    """Receive WhatsApp messages via Meta Cloud API webhook."""
    # TODO: parse Meta webhook payload into ChannelMessage
    # TODO: call process() and route response back via Meta API
    logger.info("WhatsApp webhook received: %s", payload)
    return {"status": "received"}
