import base64

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


def _post(path: str, payload: dict) -> dict:
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def render() -> None:
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
                        result = _post(
                            "/research",
                            {"query": topic.strip(), "report_mode": mode, "export_pdf": export_pdf},
                        )
                        _render_result(result)
                    except requests.RequestException as exc:
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
                        result = _post(
                            "/summarize-url",
                            {"url": url.strip(), "report_mode": mode, "export_pdf": export_url_pdf},
                        )
                        _render_result(result)
                    except requests.RequestException as exc:
                        st.error(f"URL summarization failed: {exc}")


def _render_result(result: dict) -> None:
    st.subheader("Report")
    st.markdown(result["report"])

    st.subheader("References")
    for ref in result.get("references", []):
        st.write(ref.get("citation") or ref.get("url"))

    st.subheader("Sources")
    for source in result.get("sources", []):
        st.write(source)

    if result.get("pdf_base64"):
        pdf_bytes = base64.b64decode(result["pdf_base64"])
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="research_report.pdf",
            mime="application/pdf",
        )
