from backend.agents.planner import PlannerAgent


def test_planner_detects_url() -> None:
    plan = PlannerAgent().plan("https://example.com/article", "short")
    assert plan["task_type"] == "url_summarization"
    assert plan["report_mode"] == "short"
    assert plan["execution_plan"]


def test_planner_detects_paper() -> None:
    plan = PlannerAgent().plan("summarize this arxiv paper about transformers")
    assert plan["task_type"] == "paper_summarization"
