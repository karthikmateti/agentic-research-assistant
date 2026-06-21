from backend.agents.writer import WriterAgent


def test_writer_short_report_contains_sections() -> None:
    report = WriterAgent().write(
        query="AI research assistants",
        task_type="topic_research",
        report_mode="short",
        execution_plan=["Search sources"],
        findings=["Source: useful finding"],
        references=[{"citation": "Example citation"}],
    )
    assert "# Overview" in report
    assert "# Key Findings" in report
    assert "Example citation" in report
