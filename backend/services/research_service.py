import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import ResearchHistory


def save_research_history(
    db: Session,
    query: str,
    task_type: str,
    report_mode: str,
    report: str,
    references: list[dict],
) -> ResearchHistory:
    item = ResearchHistory(
        query=query,
        task_type=task_type,
        report_mode=report_mode,
        report=report,
        references=json.dumps(references),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_research_history(db: Session, search: str | None = None) -> list[ResearchHistory]:
    stmt = select(ResearchHistory).order_by(ResearchHistory.created_at.desc())
    if search:
        stmt = stmt.where(ResearchHistory.query.ilike(f"%{search}%"))
    return list(db.scalars(stmt).all())


def delete_research_history(db: Session, history_id: int) -> bool:
    item = db.get(ResearchHistory, history_id)
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True


def history_to_dict(item: ResearchHistory) -> dict[str, Any]:
    try:
        references = json.loads(item.references)
    except json.JSONDecodeError:
        references = []
    return {
        "id": item.id,
        "query": item.query,
        "task_type": item.task_type,
        "report_mode": item.report_mode,
        "report": item.report,
        "references": references,
        "created_at": item.created_at.isoformat(),
    }
