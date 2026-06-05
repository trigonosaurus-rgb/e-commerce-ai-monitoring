import httpx
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from playwright_stealth import Stealth

async def scrape_site(url: str) -> str:
    """
    Scrapes a website using Playwright with stealth settings to bypass simple bot protection.
    If Playwright fails (e.g. strict anti-headless like Datadome), fallbacks to simple HTTP request.
    Returns the visible text of the page.
    """
    browser = None
    html_content = ""
    try:
        print(f"Scraper: starting playwright for {url}")
        async with async_playwright() as p:
            print("Scraper: launching chromium")
            browser = await p.chromium.launch(headless=True, args=["--disable-http2"])
            print("Scraper: new context")
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            # Navigate to the URL
            print("Scraper: navigating")
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Wait a brief moment for dynamic content to render
            await page.wait_for_timeout(2000)
            
            html_content = await page.content()
    except Exception as e:
        print(f"Playwright error for {url}: {e}")
    finally:
        if browser:
            await browser.close()

    # Fallback to httpx if Playwright failed to get content
    if not html_content:
        print(f"Scraper: Falling back to HTTPX for {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        try:
            async with httpx.AsyncClient(http2=False, verify=False) as client:
                res = await client.get(url, headers=headers, timeout=20.0)
                html_content = res.text
        except Exception as e:
            print(f"HTTPX error for {url}: {e}")
            return ""

    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts, styles, and empty elements
        for script in soup(["script", "style", "nav", "footer", "noscript"]):
            script.extract()
        
        # Extract text and clean it
        text = soup.get_text(separator='\n', strip=True)
        
        # Limit the text length to avoid token limits for LLM
        return text[:6000]
        
    return ""
