from typing import Literal, TypedDict

from backend.utils.logger import get_logger

logger = get_logger(__name__)

TaskType = Literal["topic_research", "url_summarization", "paper_summarization"]
ReportMode = Literal["short", "detailed"]


class Plan(TypedDict):
    task_type: TaskType
    report_mode: ReportMode
    execution_plan: list[str]


class PlannerAgent:
    def plan(self, user_query: str, report_mode: str = "detailed") -> Plan:
        query = user_query.strip()
        if not query:
            raise ValueError("Research query cannot be empty")

        normalized_mode: ReportMode = "short" if report_mode.lower() == "short" else "detailed"
        lowered = query.lower()

        if lowered.startswith(("http://", "https://")):
            task_type: TaskType = "url_summarization"
            steps = [
                "Validate and fetch the URL content",
                "Extract the article title, main text, and metadata",
                "Summarize the source with citations",
            ]
        elif any(token in lowered for token in ["paper", "arxiv", "doi", "journal", "study"]):
            task_type = "paper_summarization"
            steps = [
                "Search academic sources for relevant papers",
                "Extract abstracts, authors, and publication metadata",
                "Synthesize findings into a research-oriented report",
            ]
        else:
            task_type = "topic_research"
            steps = [
                "Search reliable web sources",
                "Search academic sources for supporting evidence",
                "Combine evidence into a structured report",
            ]

        logger.info("Planner selected task_type=%s report_mode=%s", task_type, normalized_mode)
        return {
            "task_type": task_type,
            "report_mode": normalized_mode,
            "execution_plan": steps,
        }
