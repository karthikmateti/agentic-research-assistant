from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from backend.agents.planner import PlannerAgent
from backend.agents.searcher import SearcherAgent
from backend.agents.writer import WriterAgent
from backend.services.research_service import save_research_history
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ResearchState(TypedDict, total=False):
    user_query: str
    task_type: str
    report_mode: str
    execution_plan: list[str]
    search_results: list[str]
    references: list[dict]
    source_links: list[str]
    final_report: str
    history_id: int
    db: Session


def planner_node(state: ResearchState) -> ResearchState:
    plan = PlannerAgent().plan(state["user_query"], state.get("report_mode", "detailed"))
    return {**state, **plan}


def search_node(state: ResearchState) -> ResearchState:
    results = SearcherAgent().search(state["user_query"], state["task_type"])
    return {
        **state,
        "search_results": results["findings"],
        "references": results["references"],
        "source_links": results["source_links"],
    }


def writer_node(state: ResearchState) -> ResearchState:
    report = WriterAgent().write(
        query=state["user_query"],
        task_type=state["task_type"],
        report_mode=state["report_mode"],
        execution_plan=state["execution_plan"],
        findings=state.get("search_results", []),
        references=state.get("references", []),
    )
    return {**state, "final_report": report}


def save_history_node(state: ResearchState) -> ResearchState:
    db = state.get("db")
    if db is None:
        logger.warning("No database session in graph state; skipping history save")
        return state
    history = save_research_history(
        db=db,
        query=state["user_query"],
        task_type=state["task_type"],
        report_mode=state["report_mode"],
        report=state["final_report"],
        references=state.get("references", []),
    )
    return {**state, "history_id": history.id}


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("planner_node", planner_node)
    graph.add_node("search_node", search_node)
    graph.add_node("writer_node", writer_node)
    graph.add_node("save_history_node", save_history_node)
    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "search_node")
    graph.add_edge("search_node", "writer_node")
    graph.add_edge("writer_node", "save_history_node")
    graph.add_edge("save_history_node", END)
    return graph.compile()
