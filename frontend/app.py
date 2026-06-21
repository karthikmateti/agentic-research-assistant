import importlib.util
from pathlib import Path

import streamlit as st

PAGES = {
    "Research": "home.py",
    "History": "history.py",
    "Settings": "settings.py",
}


def load_page(filename: str):
    page_path = Path(__file__).parent / "pages" / filename
    spec = importlib.util.spec_from_file_location(filename.replace(".py", ""), page_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


st.set_page_config(
    page_title="Agentic Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.sidebar.title("Agentic Research Assistant")
selected = st.sidebar.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
st.sidebar.caption("Multi-agent research automation")

page = load_page(PAGES[selected])
page.render()
