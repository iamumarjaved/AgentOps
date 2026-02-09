from langchain_core.tools import tool


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for information. Returns article summaries."""
    try:
        import wikipedia

        results = wikipedia.search(query, results=3)
        if not results:
            return f"No Wikipedia articles found for: {query}"

        summaries = []
        for title in results[:2]:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                summaries.append(f"## {page.title}\n{page.summary[:1000]}")
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue

        return "\n\n".join(summaries) if summaries else f"No content found for: {query}"
    except Exception as e:
        return f"Wikipedia error: {str(e)}"
