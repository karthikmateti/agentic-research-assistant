from datetime import datetime
from typing import Literal


def _clean(value: str | None, fallback: str) -> str:
    value = (value or "").strip()
    return value if value else fallback


def generate_citation(
    title: str,
    url: str,
    author: str | None = None,
    published: str | None = None,
    style: Literal["APA", "MLA"] = "APA",
) -> str:
    author_text = _clean(author, "Unknown author")
    title_text = _clean(title, "Untitled source")
    url_text = _clean(url, "No URL")
    year = _clean(published, str(datetime.utcnow().year))[:4]

    if style.upper() == "MLA":
        return f'{author_text}. "{title_text}." {url_text}. Accessed {datetime.utcnow().date()}.'

    return f"{author_text}. ({year}). {title_text}. Retrieved from {url_text}"


def generate_citations(references: list[dict], style: Literal["APA", "MLA"] = "APA") -> list[str]:
    return [
        generate_citation(
            title=ref.get("title", ""),
            url=ref.get("url", ""),
            author=ref.get("author"),
            published=ref.get("published"),
            style=style,
        )
        for ref in references
    ]
