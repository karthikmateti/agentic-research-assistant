import base64
import os

import streamlit as st


def load_streamlit_secrets() -> None:
    for key in [
        "OPENROUTER_API_KEY",
        "TAVILY_API_KEY",
        "OPENROUTER_MODEL",
        "DATABASE_URL",
        "APP_ENV",
        "LOG_LEVEL",
    ]:
        value = st.secrets.get(key)
        if value and not os.environ.get(key):
            os.environ[key] = str(value)


load_streamlit_secrets()

from backend.config.settings import get_settings  # noqa: E402
from backend.database.db import SessionLocal, init_db  # noqa: E402
from backend.graph.workflow import build_graph  # noqa: E402
from backend.services.research_service import (  # noqa: E402
    delete_research_history,
    history_to_dict,
    list_research_history,
)
from backend.utils.pdf_export import export_report_pdf  # noqa: E402


st.set_page_config(
    page_title="Agentic Research Assistant",
    page_icon="🔎",
    layout="wide",
)

init_db()


def run_research(query: str, report_mode: str) -> dict:
    graph = build_graph()
    with SessionLocal() as db:
        state = graph.invoke({"user_query": query, "report_mode": report_mode, "db": db})
    return {
        "history_id": state.get("history_id"),
        "query": state["user_query"],
        "task_type": state["task_type"],
        "report_mode": state["report_mode"],
        "execution_plan": state["execution_plan"],
        "report": state["final_report"],
        "references": state.get("references", []),
        "sources": state.get("source_links", []),
    }


def render_result(result: dict, export_pdf: bool) -> None:
    st.subheader("Report")
    st.markdown(result["report"])

    st.subheader("References")
    for ref in result.get("references", []):
        st.write(ref.get("citation") or ref.get("url"))

    st.subheader("Sources")
    for source in result.get("sources", []):
        st.write(source)

    if export_pdf:
        pdf_bytes = export_report_pdf(
            title=f"Research Report: {result['query']}",
            report=result["report"],
            references=result.get("references", []),
        )
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="research_report.pdf",
            mime="application/pdf",
        )


def research_page() -> None:
    st.title("Research")
    st.caption("Generate source-aware reports from topics or URLs.")

    mode = st.segmented_control("Report mode", ["short", "detailed"], default="detailed")
    tab_topic, tab_url = st.tabs(["Topic", "URL"])

    with tab_topic:
        topic = st.text_input("Topic Input", placeholder="Example: agentic AI in education")
        export_pdf = st.checkbox("Export PDF", key="topic_pdf")
        if st.button("Generate Report", key="topic_generate", type="primary"):
            if not topic.strip():
                st.error("Enter a topic to research.")
            else:
                with st.spinner("Agents are researching..."):
                    try:
                        render_result(run_research(topic.strip(), mode), export_pdf)
                    except Exception as exc:
                        st.error(f"Research failed: {exc}")

    with tab_url:
        url = st.text_input("URL Input", placeholder="https://example.com/article")
        export_url_pdf = st.checkbox("Export PDF", key="url_pdf")
        if st.button("Generate Report", key="url_generate", type="primary"):
            if not url.strip():
                st.error("Enter a URL to summarize.")
            else:
                with st.spinner("Agents are reading the URL..."):
                    try:
                        render_result(run_research(url.strip(), mode), export_url_pdf)
                    except Exception as exc:
                        st.error(f"URL summarization failed: {exc}")


def history_page() -> None:
    st.title("History")
    query = st.text_input("Search Reports", placeholder="Filter by query")

    with SessionLocal() as db:
        items = [history_to_dict(item) for item in list_research_history(db, query or None)]

    if not items:
        st.info("No saved reports yet.")
        return

    for item in items:
        with st.expander(f"{item['query']} · {item['created_at']}"):
            cols = st.columns([2, 1, 1])
            cols[0].write(f"Task: {item['task_type']}")
            cols[1].write(f"Mode: {item['report_mode']}")
            if cols[2].button("Delete Report", key=f"delete_{item['id']}"):
                with SessionLocal() as db:
                    delete_research_history(db, item["id"])
                st.rerun()
            st.markdown(item["report"])
            st.write("References")
            for ref in item.get("references", []):
                st.write(ref.get("citation") or ref.get("url"))


def settings_page() -> None:
    settings = get_settings()
    st.title("Settings")
    st.caption("Configuration and API status")

    col1, col2, col3 = st.columns(3)
    col1.metric("Runtime", "Streamlit Cloud Ready")
    col2.metric("OpenRouter", "Configured" if settings.has_openrouter_key else "Fallback")
    col3.metric("Tavily", "Configured" if settings.has_tavily_key else "Fallback")

    st.write("Required secrets")
    st.code("OPENROUTER_API_KEY\nTAVILY_API_KEY\nOPENROUTER_MODEL", language="text")


st.sidebar.title("Agentic Research Assistant")
page = st.sidebar.radio("Navigation", ["Research", "History", "Settings"], label_visibility="collapsed")
st.sidebar.caption("Multi-agent research automation")

if page == "Research":
    research_page()
elif page == "History":
    history_page()
else:
    settings_page()
