import base64
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from backend.config.settings import get_settings
from backend.database.db import get_db
from backend.graph.workflow import build_graph
from backend.services.research_service import (
    delete_research_history,
    history_to_dict,
    list_research_history,
)
from backend.utils.logger import get_logger
from backend.utils.pdf_export import export_report_pdf

logger = get_logger(__name__)
router = APIRouter()


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    report_mode: Literal["short", "detailed"] = "detailed"
    export_pdf: bool = False


class UrlSummaryRequest(BaseModel):
    url: HttpUrl
    report_mode: Literal["short", "detailed"] = "short"
    export_pdf: bool = False


def _run_research(
    db: Session,
    query: str,
    report_mode: str,
    export_pdf: bool = False,
) -> dict:
    try:
        graph = build_graph()
        state = graph.invoke({"user_query": query, "report_mode": report_mode, "db": db})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Research workflow failed")
        raise HTTPException(status_code=500, detail=f"Research workflow failed: {exc}") from exc

    response = {
        "history_id": state.get("history_id"),
        "query": state["user_query"],
        "task_type": state["task_type"],
        "report_mode": state["report_mode"],
        "execution_plan": state["execution_plan"],
        "report": state["final_report"],
        "references": state.get("references", []),
        "sources": state.get("source_links", []),
    }

    if export_pdf:
        pdf_bytes = export_report_pdf(
            title=f"Research Report: {query}",
            report=state["final_report"],
            references=state.get("references", []),
        )
        response["pdf_base64"] = base64.b64encode(pdf_bytes).decode("ascii")

    return response


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "openrouter_configured": settings.has_openrouter_key,
        "tavily_configured": settings.has_tavily_key,
    }


@router.post("/research")
def research(payload: ResearchRequest, db: Session = Depends(get_db)) -> dict:
    return _run_research(db, payload.query.strip(), payload.report_mode, payload.export_pdf)


@router.post("/summarize-url")
def summarize_url(payload: UrlSummaryRequest, db: Session = Depends(get_db)) -> dict:
    return _run_research(db, str(payload.url), payload.report_mode, payload.export_pdf)


@router.get("/history")
def history(
    search: str | None = Query(default=None, max_length=200),
    db: Session = Depends(get_db),
) -> list[dict]:
    return [history_to_dict(item) for item in list_research_history(db, search)]


@router.delete("/history/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)) -> dict:
    deleted = delete_research_history(db, history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History item not found")
    return {"deleted": True, "id": history_id}
