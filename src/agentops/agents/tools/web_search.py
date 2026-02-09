import httpx
from langchain_core.tools import tool


@tool
async def web_search(query: str) -> str:
    """Search the web for information about a topic. Returns relevant search results."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            response.raise_for_status()
            data = response.json()

            results = []
            if data.get("Abstract"):
                results.append(f"Summary: {data['Abstract']}")
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(topic["Text"])

            return "\n\n".join(results) if results else f"No results found for: {query}"
        except Exception as e:
            return f"Search error: {str(e)}"
