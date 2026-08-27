"""SNT AI main application entry point."""
import streamlit as st

from config import get_config
from logging_config import configure_logging
from ui.theme import inject_global_styles
from ui.nav import render_top_nav
from ui.render import render_html
from ui.components import (
    render_hero_cinema,
    render_section_header,
    render_luxury_metrics,
    render_pillars,
    render_timeline,
    render_cta_lux,
    render_trust_seals,
    render_footer,
)

configure_logging()
config = get_config()

st.set_page_config(
    page_title=f"{config.app_name}",
    page_icon="\U0001f6e1\ufe0f",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_styles()
render_top_nav(over_hero=True)

render_html(render_hero_cinema())

render_html(
    render_section_header(
        "Platform capability",
        "Operational controls built into the product",
        "A practical assurance workflow with deterministic execution, structured evidence, and report export.",
    )
)
render_html(
    render_luxury_metrics([
        ("5", "Synthetic personas"),
        ("3", "Scored control areas"),
        ("50%", "Max failure injection"),
        ("100%", "Replayable with seed"),
    ])
)

render_html(
    render_section_header(
        "Audit domains",
        "Three assurance layers",
        "Focused evaluations that surface behavioral, escalation, and exploit weaknesses before release.",
    )
)
render_html(render_pillars())

render_html(
    render_section_header(
        "Methodology",
        "From scenario to evidence",
        "A straightforward evaluation flow for product, QA, risk, and governance teams.",
    )
)
render_html(render_timeline())

render_html(render_cta_lux())

render_html(render_trust_seals())
render_html(render_footer())
