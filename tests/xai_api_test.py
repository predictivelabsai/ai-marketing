"""Test XAI API key from .env — verifies the key is set and working."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")


def test_xai_key():
    api_key = os.getenv("XAI_API_KEY")
    assert api_key, "XAI_API_KEY not found in .env"
    assert api_key.startswith("xai-"), f"Key should start with xai-, got: {api_key[:8]}..."

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    # List models to verify auth
    models = client.models.list()
    model_ids = [m.id for m in models.data]
    print(f"OK — {len(model_ids)} models available: {', '.join(model_ids[:5])}")
    assert len(model_ids) > 0, "No models returned"

    # Quick chat completion
    model = os.getenv("XAI_MODEL", "grok-3-fast")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say 'hello' in one word."}],
        max_tokens=10,
    )
    reply = resp.choices[0].message.content.strip()
    print(f"OK — {model} replied: {reply}")
    assert len(reply) > 0, "Empty response from model"


if __name__ == "__main__":
    test_xai_key()
    print("\nAll XAI API tests passed.")
