"""
POLLY Unified Channel API — standalone FastAPI server.

Run: python api/main.py
Port: 5056 (configurable via API_PORT env var)
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

import uvicorn
from api.routes import api

if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", 5056))
    print(f"\n  POLLY Channel API starting on port {port}")
    print(f"  Docs:   http://localhost:{port}/docs")
    print(f"  Health: http://localhost:{port}/health\n")
    uvicorn.run(
        "api.routes:api",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(ROOT / "api"), str(ROOT / "agents"), str(ROOT / "integrations")],
    )
