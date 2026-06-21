from backend.agents.searcher import SearcherAgent


def test_searcher_returns_fallback_when_no_sources(monkeypatch) -> None:
    searcher = SearcherAgent()
    monkeypatch.setattr(searcher, "_search_tavily", lambda query: [])
    monkeypatch.setattr(searcher, "_search_arxiv", lambda query: [])

    result = searcher.search("test topic", "topic_research")

    assert result["findings"]
    assert result["references"]
    assert result["source_links"] == ["local:fallback"]
