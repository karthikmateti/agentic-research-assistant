from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.db import Base
from backend.services.research_service import (
    delete_research_history,
    list_research_history,
    save_research_history,
)


def test_database_create_read_delete() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    item = save_research_history(
        session,
        "query",
        "topic_research",
        "short",
        "report",
        [{"url": "https://example.com"}],
    )

    assert item.id is not None
    assert len(list_research_history(session)) == 1
    assert delete_research_history(session, item.id) is True
    assert list_research_history(session) == []
