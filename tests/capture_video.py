#!/usr/bin/env python3
"""
Capture POLLY Product Demo Video

Playwright script that walks through key functionality,
capturing frames for an animated GIF and MP4 video (~40-60s).

Usage:
    python web/app.py &
    python tests/capture_video.py

    # Or auto-start:
    python tests/capture_video.py --start-app

Output:
    docs/demo_video.mp4
    docs/demo_video.gif
    docs/frames/*.png
"""
import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
FRAMES_DIR = ROOT / "docs" / "frames"
BASE_URL = "http://localhost:5055"
EMAIL = "testadmin@polly.ai"
PASSWORD = "pollytest2026"

frame_num = 0


async def capture(page, label, pause=1.0):
    global frame_num
    await asyncio.sleep(pause)
    path = FRAMES_DIR / f"{frame_num:03d}_{label}.png"
    await page.screenshot(path=str(path), type="png")
    print(f"  [{frame_num:03d}] {label}")
    frame_num += 1


async def run():
    from playwright.async_api import async_playwright

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # ===== 1. HOME PAGE =====
        await page.goto(f"{BASE_URL}/")
        await asyncio.sleep(1.5)
        await capture(page, "home_hero", 1.0)

        # Scroll to features
        await page.evaluate("window.scrollTo(0, 500)")
        await capture(page, "home_features", 1.0)

        # ===== 2. ABOUT PAGE =====
        await page.goto(f"{BASE_URL}/about")
        await asyncio.sleep(1)
        await capture(page, "about_top", 1.0)

        await page.evaluate("window.scrollTo(0, 800)")
        await capture(page, "about_personas", 0.8)

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await capture(page, "about_channels", 0.8)

        # ===== 3. LOGIN =====
        await page.goto(f"{BASE_URL}/signin")
        await asyncio.sleep(1)
        await capture(page, "login_page", 0.5)

        await page.fill('input[name="email"]', EMAIL)
        await page.fill('input[name="password"]', PASSWORD)
        await capture(page, "login_filled", 0.8)

        await page.click('button[type="submit"]')
        await asyncio.sleep(2)

        # ===== 4. CHAT — STARTER BUTTONS =====
        await page.goto(f"{BASE_URL}/chat")
        await asyncio.sleep(1.5)
        await capture(page, "chat_starters", 1.5)
        await capture(page, "chat_starters_hold", 0.5)  # extra frame for pacing

        # ===== 5. CHAT — CAMPAIGN CREATION =====
        await page.evaluate("quickChat('Create a campaign for my latest financial product')")
        await asyncio.sleep(3)
        await capture(page, "chat_campaign", 1.0)

        # ===== 6. CHAT — COMPLIANCE REVIEW =====
        await page.evaluate("quickChat('Review my marketing content for compliance')")
        await asyncio.sleep(3)
        await capture(page, "chat_compliance", 1.0)

        # ===== 7. CHAT — ANALYTICS =====
        await page.evaluate("quickChat('Show me campaign analytics for this week')")
        await asyncio.sleep(3)
        await capture(page, "chat_analytics", 1.0)

        # ===== 8. PROFILE PAGE =====
        await page.goto(f"{BASE_URL}/profile")
        await asyncio.sleep(1)
        await capture(page, "profile_integrations", 1.0)

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await capture(page, "profile_skills", 0.8)

        # ===== 9. INSTRUCTIONS EDITOR =====
        await page.goto(f"{BASE_URL}/instructions")
        await asyncio.sleep(1.5)
        await capture(page, "instructions_top", 1.0)

        await page.evaluate("window.scrollTo(0, 600)")
        await capture(page, "instructions_agents", 0.8)

        # ===== 10. DEMO — WHATSAPP =====
        await page.goto(f"{BASE_URL}/demo")
        await asyncio.sleep(1.5)
        await capture(page, "demo_whatsapp", 1.0)

        # Click first scenario
        first_card = page.locator('.scenario-card').first
        if await first_card.count() > 0:
            await first_card.click()
            await asyncio.sleep(4)
            await capture(page, "demo_scenario", 1.0)

        # ===== 11. DEMO — TELEGRAM =====
        tg_btn = page.locator('button:has-text("Telegram")')
        if await tg_btn.count() > 0:
            await tg_btn.click()
            await asyncio.sleep(1)
            await capture(page, "demo_telegram", 0.8)

        # ===== 12. DEMO — ANALYTICS TAB =====
        analytics_tab = page.locator('button:has-text("Live Analytics")')
        if await analytics_tab.count() > 0:
            await analytics_tab.click()
            await asyncio.sleep(0.5)
            await capture(page, "demo_analytics_tab", 1.0)

        # ===== 13. DEMO — CAMPAIGN PREVIEW =====
        campaign_tab = page.locator('button:has-text("Campaign Preview")')
        if await campaign_tab.count() > 0:
            await campaign_tab.click()
            await asyncio.sleep(0.5)
            await capture(page, "demo_campaign_preview", 1.0)

        # ===== 14. BACK TO HOME (CLOSING SHOT) =====
        await page.goto(f"{BASE_URL}/")
        await asyncio.sleep(1.5)
        await capture(page, "final_home", 1.5)

        await browser.close()

    print(f"\n  Captured {frame_num} frames to {FRAMES_DIR}")


def build_video():
    """Assemble frames into MP4 and GIF."""
    from PIL import Image
    import av
    import numpy as np

    frames = sorted(FRAMES_DIR.glob("*.png"))
    if not frames:
        print("  No frames found!")
        return

    images = [np.array(Image.open(f)) for f in frames]
    print(f"  Building video from {len(images)} frames...")

    # --- MP4 ---
    mp4_path = ROOT / "docs" / "demo_video.mp4"
    fps = 2
    hold_frames = 3  # each screenshot held for 1.5 seconds

    container = av.open(str(mp4_path), mode="w")
    h, w = images[0].shape[:2]
    w_enc = w if w % 2 == 0 else w - 1
    h_enc = h if h % 2 == 0 else h - 1
    stream = container.add_stream("libx264", rate=fps)
    stream.width = w_enc
    stream.height = h_enc
    stream.pix_fmt = "yuv420p"

    for img in images:
        img_cropped = img[:h_enc, :w_enc, :3]
        frame = av.VideoFrame.from_ndarray(img_cropped, format="rgb24")
        for _ in range(hold_frames):
            for packet in stream.encode(frame):
                container.mux(packet)

    for packet in stream.encode():
        container.mux(packet)
    container.close()
    total_secs = len(images) * hold_frames / fps
    size_mb = mp4_path.stat().st_size / (1024 * 1024)
    print(f"  MP4: {mp4_path} ({total_secs:.0f}s, {size_mb:.1f}MB)")

    # --- GIF (half-size for smaller file) ---
    gif_path = ROOT / "docs" / "demo_video.gif"
    pil_frames = []
    for img in images:
        pil_img = Image.fromarray(img[:, :, :3])
        pil_img = pil_img.resize((w // 2, h // 2), Image.LANCZOS)
        pil_frames.append(pil_img)

    pil_frames[0].save(
        str(gif_path), save_all=True, append_images=pil_frames[1:],
        duration=1500, loop=0, optimize=True,
    )
    size_mb = gif_path.stat().st_size / (1024 * 1024)
    print(f"  GIF: {gif_path} ({size_mb:.1f}MB)")


def main():
    parser = argparse.ArgumentParser(description="Capture POLLY demo video")
    parser.add_argument("--start-app", action="store_true", help="Auto-start the web app")
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  POLLY Product Demo — Video Capture")
    print(f"{'='*60}\n")

    app_proc = None
    if args.start_app:
        print("  Starting POLLY web app...")
        app_proc = subprocess.Popen(
            [sys.executable, str(ROOT / "web" / "app.py")],
            cwd=str(ROOT),
            env={**__import__("os").environ},
        )
        time.sleep(4)
        print(f"  App started (PID {app_proc.pid})\n")

    try:
        asyncio.run(run())
        print(f"\n{'='*60}")
        print(f"  Building video and GIF...")
        print(f"{'='*60}\n")
        build_video()
    finally:
        if app_proc:
            app_proc.terminate()
            app_proc.wait()
            print("  App stopped")

    print(f"\n  Done!")
    print(f"  MP4: docs/demo_video.mp4")
    print(f"  GIF: docs/demo_video.gif")
    print(f"  Frames: docs/frames/\n")


if __name__ == "__main__":
    main()
