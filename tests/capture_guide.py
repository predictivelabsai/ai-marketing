#!/usr/bin/env python3
"""
POLLY Guide Screenshot Capture

Launches a headless Playwright browser, logs in, navigates every page,
and captures screenshots to static/guide/ for the in-app user guide.

Usage:
    # App already running on port 5055
    python tests/capture_guide.py

    # Auto-start app (requires DB_URL in .env)
    python tests/capture_guide.py --start-app

    # Custom base URL
    python tests/capture_guide.py --base-url http://localhost:5055
"""
import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
GUIDE_DIR = ROOT / "static" / "guide"
RESULTS_FILE = ROOT / "test-results" / "guide_capture.json"


async def capture_all(base_url: str):
    from playwright.async_api import async_playwright

    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "test-results").mkdir(exist_ok=True)

    results = {"base_url": base_url, "screenshots": [], "errors": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        async def capture(name: str, description: str):
            path = GUIDE_DIR / f"{name}.png"
            await page.screenshot(path=str(path), full_page=False)
            size = path.stat().st_size
            results["screenshots"].append({
                "name": name, "file": f"{name}.png",
                "description": description, "size_bytes": size,
            })
            print(f"  [{len(results['screenshots']):02d}] {name}.png ({size // 1024}K) — {description}")

        async def capture_full(name: str, description: str):
            path = GUIDE_DIR / f"{name}.png"
            await page.screenshot(path=str(path), full_page=True)
            size = path.stat().st_size
            results["screenshots"].append({
                "name": name, "file": f"{name}.png",
                "description": description, "size_bytes": size,
            })
            print(f"  [{len(results['screenshots']):02d}] {name}.png ({size // 1024}K) — {description}")

        try:
            # ---- 1. Public pages ----
            print("\n=== Public Pages ===")

            await page.goto(f"{base_url}/")
            await page.wait_for_load_state("networkidle")
            await capture("01_home", "Home page — hero and feature cards")

            await page.goto(f"{base_url}/about")
            await page.wait_for_load_state("networkidle")
            await capture("02_about_top", "About page — hero and stats")

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(0.5)
            await capture("03_about_bottom", "About page — channels and CTA")

            await page.goto(f"{base_url}/demo")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            await capture("04_demo", "Interactive demo — device simulator")

            # ---- 2. Auth pages ----
            print("\n=== Auth Pages ===")

            await page.goto(f"{base_url}/register")
            await page.wait_for_load_state("networkidle")
            await capture("05_register", "Registration page")

            await page.goto(f"{base_url}/signin")
            await page.wait_for_load_state("networkidle")
            await capture("06_signin", "Login page")

            # ---- 3. Register test user and login ----
            print("\n=== Authenticated Pages ===")

            # Register a fresh guide-capture user
            test_email = "guide-capture@polly.test"
            test_pass = "guidecapture2026"
            await page.goto(f"{base_url}/register")
            await page.wait_for_load_state("networkidle")

            email_input = page.locator('input[name="email"]')
            pw_input = page.locator('input[name="password"]')
            name_input = page.locator('input[name="display_name"]')

            await email_input.fill(test_email)
            await pw_input.fill(test_pass)
            await name_input.fill("Guide User")
            await page.locator('button[type="submit"]').click()
            await page.wait_for_load_state("networkidle")

            # If user already exists, login instead
            if "/signin" in page.url or "/register" in page.url:
                await page.goto(f"{base_url}/signin")
                await page.wait_for_load_state("networkidle")
                await page.locator('input[name="email"]').fill(test_email)
                await page.locator('input[name="password"]').fill(test_pass)
                await page.locator('button[type="submit"]').click()
                await page.wait_for_load_state("networkidle")

            # ---- 4. Chat page ----
            print("\n=== Chat Page ===")

            await page.goto(f"{base_url}/chat")
            await page.wait_for_load_state("networkidle")
            await capture("07_chat_starter", "Chat page — 6 starter skill buttons")

            # Click a starter button to show chat
            await page.evaluate("quickChat('Create a campaign for my latest financial product')")
            await asyncio.sleep(2.5)
            await capture("08_chat_campaign", "Chat — campaign creation response")

            # Send another message
            await page.evaluate("quickChat('Show me campaign analytics for this week')")
            await asyncio.sleep(2.5)
            await capture("09_chat_analytics", "Chat — analytics response")

            # ---- 5. Profile page ----
            print("\n=== Profile Page ===")

            await page.goto(f"{base_url}/profile")
            await page.wait_for_load_state("networkidle")
            await capture("10_profile_top", "Profile — account and integrations")

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(0.5)
            await capture("11_profile_skills", "Profile — marketing skills grid")

            # ---- 6. Instructions Editor ----
            print("\n=== Instructions Editor ===")

            await page.goto(f"{base_url}/instructions")
            await page.wait_for_load_state("networkidle")
            await capture("12_instructions_top", "Instructions Editor — global and content agent")

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(0.5)
            await capture("13_instructions_bottom", "Instructions Editor — SEO and Ads agents")

            # ---- 7. Demo interactions ----
            print("\n=== Demo Interactions ===")

            await page.goto(f"{base_url}/demo")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)

            # Click a scenario
            scenario_card = page.locator('.scenario-card').first
            if await scenario_card.count() > 0:
                await scenario_card.click()
                await asyncio.sleep(4)
                await capture("14_demo_scenario", "Demo — campaign creation scenario")

            # Switch to Telegram
            tg_btn = page.locator('button:has-text("Telegram")')
            if await tg_btn.count() > 0:
                await tg_btn.click()
                await asyncio.sleep(1)
                await capture("15_demo_telegram", "Demo — Telegram device simulator")

            # Switch to analytics tab
            analytics_tab = page.locator('button:has-text("Live Analytics")')
            if await analytics_tab.count() > 0:
                await analytics_tab.click()
                await asyncio.sleep(0.5)
                await capture("16_demo_analytics", "Demo — live analytics dashboard")

            # Campaign preview tab
            campaign_tab = page.locator('button:has-text("Campaign Preview")')
            if await campaign_tab.count() > 0:
                await campaign_tab.click()
                await asyncio.sleep(0.5)
                await capture("17_demo_campaign_preview", "Demo — campaign A/B variant preview")

        except Exception as e:
            results["errors"].append(str(e))
            print(f"\n  ERROR: {e}")

        finally:
            await browser.close()

    # Write results
    results["total"] = len(results["screenshots"])
    results["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n=== Done: {results['total']} screenshots captured to {GUIDE_DIR} ===")
    print(f"Results: {RESULTS_FILE}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Capture POLLY guide screenshots")
    parser.add_argument("--base-url", default="http://localhost:5055",
                        help="Base URL of the running POLLY web app")
    parser.add_argument("--start-app", action="store_true",
                        help="Auto-start the web app before capturing")
    args = parser.parse_args()

    app_proc = None
    if args.start_app:
        print("Starting POLLY web app...")
        app_proc = subprocess.Popen(
            [sys.executable, str(ROOT / "web" / "app.py")],
            cwd=str(ROOT),
            env={**__import__("os").environ},
        )
        time.sleep(4)
        print(f"App started (PID {app_proc.pid})")

    try:
        asyncio.run(capture_all(args.base_url))
    finally:
        if app_proc:
            app_proc.terminate()
            app_proc.wait()
            print("App stopped")


if __name__ == "__main__":
    main()
