import httpx
from bs4 import BeautifulSoup

async def scrape_competitor_site(url: str) -> str:
    """
    Scrapes a competitor's website and returns the visible text or HTML.
    For this portfolio project, we use httpx and BeautifulSoup.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # We use a User-Agent to avoid basic blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles to clean up the text for the LLM
            for script in soup(["script", "style"]):
                script.extract()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Limit the text length to avoid token limits for LLM
            return text[:4000]
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
