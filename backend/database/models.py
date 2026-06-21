from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.db import Base


class ResearchHistory(Base):
    __tablename__ = "research_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    report_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    report: Mapped[str] = mapped_column(Text, nullable=False)
    references: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
