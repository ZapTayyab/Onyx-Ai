"""Safe HTML rendering for Streamlit (avoids markdown code-block escaping)."""

from __future__ import annotations

import textwrap


def clean_html(html: str) -> str:
    """Remove Python indentation so markdown does not treat HTML as code."""
    return textwrap.dedent(html).strip()


def render_html(html: str) -> None:
    """Render HTML without markdown interpreting indented lines as code blocks."""
    import streamlit as st

    content = clean_html(html)
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)
