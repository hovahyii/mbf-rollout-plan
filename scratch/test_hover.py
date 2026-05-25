import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Listen for console events
        page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        # Load the local index.html
        file_url = f"file:///{os.path.abspath('index.html').replace(chr(92), '/')}"
        print(f"Loading {file_url}")
        await page.goto(file_url, wait_until="networkidle")
        
        # Wait for the map to load and markers to be created
        await page.wait_for_timeout(2000)
        
        # Simulate hovering over a marker
        # We can just evaluate some JS in the page to trigger a hover on the first marker,
        # or we can click it. Let's just find the first leaflet-interactive element and hover.
        elements = await page.query_selector_all(".leaflet-interactive")
        print(f"Found {len(elements)} interactive elements (markers/paths).")
        
        if elements:
            try:
                # Hover and click the first marker to trigger events
                await elements[0].hover()
                await page.wait_for_timeout(500)
                await elements[0].click()
                await page.wait_for_timeout(500)
            except Exception as e:
                print(f"Error hovering/clicking: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
