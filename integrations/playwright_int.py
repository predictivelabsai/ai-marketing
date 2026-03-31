"""Playwright integration for page analysis."""
import os
from typing import Optional

from .base import IntegrationBackend


class PlaywrightIntegration(IntegrationBackend):
    """Shared browser manager for page analysis (CRO, SEO, Ads)."""

    name = "playwright"

    def __init__(self):
        self._browser = None
        self._playwright = None

    def is_configured(self) -> bool:
        # Playwright is available if the package is installed
        try:
            import playwright  # noqa: F401
            return True
        except ImportError:
            return False

    async def _ensure_browser(self):
        if self._browser is None:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)

    async def get_page_snapshot(self, url: str) -> dict[str, str]:
        """Navigate to URL and return page content + metadata."""
        await self._ensure_browser()
        page = await self._browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html = await page.content()
            title = await page.title()
            meta_desc = await page.evaluate(
                """() => {
                    const el = document.querySelector('meta[name="description"]');
                    return el ? el.content : '';
                }"""
            )
            return {"url": url, "title": title, "meta_description": meta_desc, "html": html}
        finally:
            await page.close()

    async def extract_meta(self, url: str) -> dict[str, str]:
        """Extract meta tags, headings, and structured data from a URL."""
        await self._ensure_browser()
        page = await self._browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            meta = await page.evaluate(
                """() => {
                    const result = {title: document.title, meta: {}, headings: {}, jsonld: []};
                    document.querySelectorAll('meta').forEach(m => {
                        const name = m.name || m.getAttribute('property') || '';
                        if (name) result.meta[name] = m.content || '';
                    });
                    ['h1','h2','h3'].forEach(tag => {
                        result.headings[tag] = [...document.querySelectorAll(tag)].map(e => e.textContent.trim());
                    });
                    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
                        try { result.jsonld.push(JSON.parse(s.textContent)); } catch {}
                    });
                    return result;
                }"""
            )
            return meta
        finally:
            await page.close()

    async def evaluate_page(self, url: str, js: str) -> str:
        """Run arbitrary JS on a page and return the result as string."""
        await self._ensure_browser()
        page = await self._browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            result = await page.evaluate(js)
            return str(result)
        finally:
            await page.close()

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
