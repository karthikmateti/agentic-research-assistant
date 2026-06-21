from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from backend.config.settings import get_settings
from backend.utils.citation import generate_citation
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SearchResult(TypedDict):
    findings: list[str]
    references: list[dict]
    source_links: list[str]


@dataclass
class Source:
    title: str
    url: str
    content: str
    author: str | None = None
    published: str | None = None


class SearcherAgent:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: str, task_type: str) -> SearchResult:
        logger.info("Searcher started task_type=%s query=%s", task_type, query[:120])
        sources: list[Source] = []

        if task_type == "url_summarization":
            sources.extend(self._scrape_url(query))
        else:
            sources.extend(self._search_tavily(query))
            sources.extend(self._search_arxiv(query))

        if not sources:
            sources.append(
                Source(
                    title=f"Research brief for {query}",
                    url="local:fallback",
                    content=(
                        f"No live external sources were available for '{query}'. "
                        "This fallback finding summarizes the topic from the query context "
                        "and should be replaced by live search results when API keys and "
                        "network access are configured."
                    ),
                    author="Agentic Research Assistant",
                    published=None,
                )
            )

        references = [
            {
                "title": source.title,
                "url": source.url,
                "author": source.author,
                "published": source.published,
                "citation": generate_citation(
                    source.title, source.url, source.author, source.published, "APA"
                ),
            }
            for source in sources
        ]
        findings = [self._compact_finding(source) for source in sources]
        source_links = [source.url for source in sources]
        logger.info("Searcher collected %s sources", len(sources))
        return {"findings": findings, "references": references, "source_links": source_links}

    def _search_tavily(self, query: str) -> list[Source]:
        if not self.settings.has_tavily_key:
            logger.warning("Tavily API key missing; skipping Tavily search")
            return []

        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.settings.tavily_api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": 5,
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            sources = []
            if payload.get("answer"):
                sources.append(
                    Source(
                        title=f"Tavily answer: {query}",
                        url="https://tavily.com",
                        content=payload["answer"],
                        author="Tavily",
                    )
                )
            for item in payload.get("results", []):
                sources.append(
                    Source(
                        title=item.get("title") or "Untitled Tavily result",
                        url=item.get("url") or "",
                        content=item.get("content") or "",
                    )
                )
            return sources
        except requests.RequestException as exc:
            logger.exception("Tavily search failed: %s", exc)
            return []

    def _search_arxiv(self, query: str) -> list[Source]:
        try:
            response = requests.get(
                "https://export.arxiv.org/api/query",
                params={"search_query": f"all:{query}", "start": 0, "max_results": 3},
                timeout=20,
            )
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            sources = []
            for entry in feed.entries:
                authors = ", ".join(author.name for author in entry.get("authors", []))
                sources.append(
                    Source(
                        title=entry.get("title", "Untitled arXiv paper").replace("\n", " "),
                        url=entry.get("link", ""),
                        content=entry.get("summary", "").replace("\n", " "),
                        author=authors or "Unknown authors",
                        published=entry.get("published", "")[:10],
                    )
                )
            return sources
        except requests.RequestException as exc:
            logger.exception("arXiv search failed: %s", exc)
            return []

    def _scrape_url(self, url: str) -> list[Source]:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Invalid URL. Provide a valid http or https URL.")

        try:
            response = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "AgenticResearchAssistant/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("URL scraping failed: %s", exc)
            raise ValueError(f"Unable to fetch URL: {exc}") from exc

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        content = " ".join(paragraphs)[:7000] or soup.get_text(" ", strip=True)[:7000]
        if not content:
            raise ValueError("No readable article content found at URL.")
        return [Source(title=title, url=url, content=content)]

    def _compact_finding(self, source: Source) -> str:
        text = " ".join(source.content.split())
        if len(text) > 900:
            text = text[:897].rsplit(" ", 1)[0] + "..."
        return f"{source.title}: {text}"
