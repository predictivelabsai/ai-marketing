#!/usr/bin/env python3
"""Main entry point for the POLLY Marketing CLI."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tui.app import PollyApp


async def main():
    """Main entry point."""
    app = PollyApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
