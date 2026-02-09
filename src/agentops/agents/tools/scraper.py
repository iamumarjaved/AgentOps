import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool


@tool
async def scrape_url(url: str) -> str:
    """Scrape content from a web URL. Returns the main text content."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            response = await client.get(
                url, headers={"User-Agent": "AgentOps Research Bot/1.0"}
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Truncate to avoid token limits
            return text[:3000] if len(text) > 3000 else text
        except Exception as e:
            return f"Scraping error for {url}: {str(e)}"
