from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from playwright_stealth import stealth_async

async def scrape_site(url: str) -> str:
    """
    Scrapes a website using Playwright with stealth settings to bypass simple bot protection.
    Returns the visible text of the page.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await stealth_async(page)
            
            # Navigate to the URL
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait a brief moment for dynamic content to render
            await page.wait_for_timeout(2000)
            
            html_content = await page.content()
            await browser.close()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove scripts, styles, and empty elements
            for script in soup(["script", "style", "nav", "footer", "noscript"]):
                script.extract()
            
            # Extract text and clean it
            text = soup.get_text(separator='\n', strip=True)
            
            # Limit the text length to avoid token limits for LLM
            return text[:6000]
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
