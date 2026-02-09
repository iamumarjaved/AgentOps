from langchain_core.tools import tool


@tool
def arxiv_search(query: str) -> str:
    """Search arXiv for academic papers on a topic. Returns paper titles and summaries."""
    try:
        import arxiv

        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
        results = list(client.results(search))

        if not results:
            return f"No arXiv papers found for: {query}"

        papers = []
        for paper in results:
            papers.append(
                f"## {paper.title}\n"
                f"Authors: {', '.join(a.name for a in paper.authors[:3])}\n"
                f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
                f"Summary: {paper.summary[:500]}"
            )

        return "\n\n".join(papers)
    except Exception as e:
        return f"arXiv error: {str(e)}"
