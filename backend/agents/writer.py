from langchain_openai import ChatOpenAI

from backend.config.settings import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class WriterAgent:
    def __init__(self) -> None:
        self.settings = get_settings()

    def write(
        self,
        query: str,
        task_type: str,
        report_mode: str,
        execution_plan: list[str],
        findings: list[str],
        references: list[dict],
    ) -> str:
        logger.info("Writer started report_mode=%s task_type=%s", report_mode, task_type)
        if self.settings.has_openrouter_key:
            try:
                return self._write_with_llm(
                    query, task_type, report_mode, execution_plan, findings, references
                )
            except Exception as exc:
                logger.exception("OpenRouter generation failed; using local writer: %s", exc)

        return self._write_locally(query, task_type, report_mode, execution_plan, findings, references)

    def _write_with_llm(
        self,
        query: str,
        task_type: str,
        report_mode: str,
        execution_plan: list[str],
        findings: list[str],
        references: list[dict],
    ) -> str:
        llm = ChatOpenAI(
            model=self.settings.openrouter_model,
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.openrouter_base_url,
            temperature=0.2,
        )
        sections = self._section_names(report_mode)
        prompt = f"""
You are the Writer Agent for an Agentic AI Research Assistant.
Create a {report_mode} structured research report.

Query: {query}
Task type: {task_type}
Execution plan: {execution_plan}
Required sections: {sections}
Findings:
{chr(10).join(f'- {finding}' for finding in findings)}

References:
{chr(10).join(f'- {ref.get("citation", ref.get("url", ""))}' for ref in references)}

Use clear academic language. Include concise citations inline where useful.
"""
        response = llm.invoke(prompt)
        return str(response.content)

    def _write_locally(
        self,
        query: str,
        task_type: str,
        report_mode: str,
        execution_plan: list[str],
        findings: list[str],
        references: list[dict],
    ) -> str:
        if report_mode == "short":
            return self._short_report(query, task_type, findings, references)
        return self._detailed_report(query, task_type, execution_plan, findings, references)

    def _short_report(
        self, query: str, task_type: str, findings: list[str], references: list[dict]
    ) -> str:
        key_findings = "\n".join(f"- {finding}" for finding in findings[:5])
        refs = "\n".join(f"- {ref.get('citation', ref.get('url', ''))}" for ref in references)
        return f"""# Overview
This {task_type.replace("_", " ")} report addresses: {query}.

# Key Findings
{key_findings}

# Summary
The collected evidence indicates that the topic should be evaluated through both practical applications and source-backed constraints. The references below provide the basis for deeper review.

# References
{refs if refs else "- No references available."}
"""

    def _detailed_report(
        self,
        query: str,
        task_type: str,
        execution_plan: list[str],
        findings: list[str],
        references: list[dict],
    ) -> str:
        findings_text = "\n".join(f"- {finding}" for finding in findings[:8])
        plan_text = "\n".join(f"- {step}" for step in execution_plan)
        refs = "\n".join(f"- {ref.get('citation', ref.get('url', ''))}" for ref in references)
        return f"""# Executive Summary
This report investigates {query} using an automated multi-agent workflow. The system classified the task as {task_type.replace("_", " ")} and synthesized evidence from available web, academic, or URL-based sources.

# Introduction
The goal is to produce a structured, citation-aware research document that helps readers quickly understand the topic and decide where to investigate further.

# Background
The Planner Agent created this execution plan:
{plan_text}

# Key Findings
{findings_text}

# Analysis
The evidence suggests that {query} should be assessed across source reliability, practical relevance, and research maturity. Findings are strongest when multiple independent sources converge and weakest when live search access is unavailable.

# Challenges
- External search quality depends on API credentials, rate limits, and network availability.
- Article pages can block scraping or omit readable paragraph content.
- Automated summaries should be reviewed before being used in formal academic work.

# Future Scope
- Add a Reviewer Agent for critique and gap detection.
- Add a Verifier Agent for source triangulation.
- Add PDF paper upload and long-document extraction.

# Conclusion
The assistant produced a structured report with traceable references. The result is suitable as a starting point for research, briefing, or literature exploration.

# References
{refs if refs else "- No references available."}
"""

    def _section_names(self, report_mode: str) -> list[str]:
        if report_mode == "short":
            return ["Overview", "Key Findings", "Summary"]
        return [
            "Executive Summary",
            "Introduction",
            "Background",
            "Key Findings",
            "Analysis",
            "Challenges",
            "Future Scope",
            "Conclusion",
            "References",
        ]
