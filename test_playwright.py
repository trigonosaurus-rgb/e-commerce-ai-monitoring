import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    print('launching')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-http2"])
        print('context')
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        print('stealth')
        try:
            await Stealth().apply_stealth_async(page)
        except Exception as e:
            print("Stealth error:", e)
        print('navigating to galaxus')
        try:
            await page.goto("https://www.galaxus.de/", wait_until="commit", timeout=30000)
            await page.wait_for_timeout(2000)
            html = await page.content()
            print("success! HTML length:", len(html))
        except Exception as e:
            print("nav error:", e)
        await browser.close()
        print('done')

asyncio.run(main())
