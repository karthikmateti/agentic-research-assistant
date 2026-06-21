import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


def render() -> None:
    st.title("History")
    query = st.text_input("Search Reports", placeholder="Filter by query")

    try:
        response = requests.get(f"{API_URL}/history", params={"search": query or None}, timeout=30)
        response.raise_for_status()
        items = response.json()
    except requests.RequestException as exc:
        st.error(f"Unable to load history: {exc}")
        return

    if not items:
        st.info("No saved reports yet.")
        return

    for item in items:
        with st.expander(f"{item['query']} · {item['created_at']}"):
            cols = st.columns([2, 1, 1])
            cols[0].write(f"Task: {item['task_type']}")
            cols[1].write(f"Mode: {item['report_mode']}")
            if cols[2].button("Delete Report", key=f"delete_{item['id']}"):
                try:
                    delete_response = requests.delete(f"{API_URL}/history/{item['id']}", timeout=30)
                    delete_response.raise_for_status()
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Delete failed: {exc}")
            st.markdown(item["report"])
            st.write("References")
            for ref in item.get("references", []):
                st.write(ref.get("citation") or ref.get("url"))
