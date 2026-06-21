import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


def render() -> None:
    st.title("Settings")
    st.caption("Configuration and API status")

    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        response.raise_for_status()
        health = response.json()
    except requests.RequestException as exc:
        st.error(f"Backend unavailable: {exc}")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Backend", health["status"])
    col2.metric("OpenRouter", "Configured" if health["openrouter_configured"] else "Fallback")
    col3.metric("Tavily", "Configured" if health["tavily_configured"] else "Fallback")

    st.write("Environment variables")
    st.code("OPENROUTER_API_KEY\nTAVILY_API_KEY\nOPENROUTER_MODEL\nDATABASE_URL", language="text")
