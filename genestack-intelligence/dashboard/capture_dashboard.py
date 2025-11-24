#!/usr/bin/env python3
"""
Capture a screenshot of the running Streamlit dashboard using Playwright.

Usage:
    python capture_dashboard.py --url http://localhost:8600 --output /path/to/img.png
"""

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Playwright is required. Install with `pip install playwright && playwright install chromium`."
    ) from exc


async def grab_screenshot(
    url: str,
    output: Path,
    wait_time: float,
    scroll_text: str | None = None,
    full_page: bool = False,
) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(wait_time * 1000)
        # Wait for core dashboard sections to render so we capture beyond the header
        key_sections = [
            "Top 10 Active Branches",
            "Top 10 Modified Files per Branch",
            "AI Analysis",
        ]
        for text in key_sections:
            try:
                await page.wait_for_selector(f"text={text}", timeout=10000)
            except Exception:
                continue
        # Streamlit wraps content in a scrollable block container, so expand it
        # before taking the screenshot to avoid clipping the lower sections.
        await page.add_style_tag(
            content="""
            section.main, [data-testid="block-container"] {
                height: auto !important;
                min-height: 0 !important;
                overflow: visible !important;
            }
            """
        )
        # Scroll once through the main container to trigger lazy loading.
        await page.evaluate(
            """
            const container = document.querySelector('[data-testid="block-container"]');
            if (container) {
                container.scrollTo(0, container.scrollHeight);
            } else {
                window.scrollTo(0, document.body.scrollHeight);
            }
            """
        )
        await page.wait_for_timeout(500)
        if scroll_text:
            try:
                target = await page.wait_for_selector(f"text={scroll_text}", timeout=10000)
                await target.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
            except Exception:
                pass
        output.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(output), full_page=full_page)
        await browser.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Capture Streamlit dashboard screenshot.")
    parser.add_argument("--url", required=True, help="Dashboard URL to capture")
    parser.add_argument("--output", required=True, help="Path to write PNG screenshot")
    parser.add_argument("--wait", type=float, default=5.0, help="Seconds to wait after load before capture")
    parser.add_argument(
        "--scroll-text",
        help="Scroll to the first element containing this text before capturing the screenshot.",
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="Capture the entire document height instead of just the viewport.",
    )
    args = parser.parse_args(argv)

    asyncio.run(
        grab_screenshot(
            args.url,
            Path(args.output),
            args.wait,
            scroll_text=args.scroll_text,
            full_page=args.full_page,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
