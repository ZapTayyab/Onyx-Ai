"""SNT AI evaluation dashboard."""

import streamlit as st

from app_services import AuditService
from config import get_config
from logging_config import configure_logging
from ui.theme import inject_global_styles
from ui.nav import render_top_nav
from ui.render import render_html
from ui.charts import render_category_breakdown, compute_breakdown
from ui.components import (
    render_footer,
    render_status_badge,
    render_score_ring,
    render_session_card,
    render_trust_seals,
    render_empty_state,
    render_section_header,
)

configure_logging()
config = get_config()
service = AuditService(config)

st.set_page_config(
    page_title=f"Evaluation Workspace — {config.company_name}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_styles()
render_top_nav()

for key, default in [("results", None), ("report_text", None), ("last_score", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

render_html("""
<div class="snt-dash-hero">
  <p class="snt-dash-kicker">Evaluation workspace</p>
  <h1 class="snt-dash-title">Run a controlled assurance review</h1>
  <p class="snt-dash-sub">
    Configure a deterministic audit run, inspect session evidence, and export an executive text report.
  </p>
</div>
""")

# ── Controls ───────────────────────────────────────────────────────────────
render_html("""
<div class="snt-control-lux">
  <div class="snt-control-lux-head">
    <p class="snt-control-lux-title">Run parameters</p>
  </div>
  <p class="snt-control-lux-sub">
    Use a fixed seed for replayability and adjust the failure rate to simulate stricter operating conditions.
  </p>
</div>
""")

c1, c2, c3 = st.columns([1.1, 1, 1])
with c1:
    seed = st.number_input(
        "Random seed",
        min_value=0, max_value=9999, value=config.default_seed,
        help="Fixed seed ensures reproducible audit trails.",
    )
with c2:
    failure_rate = st.slider(
        "Failure injection",
        min_value=0, max_value=config.max_failure_rate, value=int(config.default_failure_rate * 100), format="%d%%",
        help="Percentage of chatbot responses simulating failure modes.",
    )
with c3:
    render_html("<div style='height:1.5rem;'></div>")
    run = st.button("Run evaluation", type="primary", use_container_width=True)

if run:
    with st.spinner("Executing simulation across all sessions…"):
        results, report_text, summary = service.run_audit(
            failure_rate=failure_rate / 100.0,
            seed=int(seed),
        )
        st.session_state.results = results
        st.session_state.report_text = report_text
        st.session_state.last_score = summary.score

results = st.session_state.results

if results is None:
    render_html(render_empty_state())
else:
    score = st.session_state.last_score
    total_sessions = len(results)
    flagged = sum(1 for r in results if r["session_failed"])
    total_turns = sum(len(r["turn_results"]) for r in results)
    failed_turns = sum(1 for r in results for t in r["turn_results"] if not t["passed"])

    if score >= 80:
        status, msg = "pass", (
            "The current run meets the internal acceptance threshold. Review flagged sessions before sign-off."
        )
    elif score >= 50:
        status, msg = "review", (
            "The run shows partial control coverage. Remediation is recommended before release approval."
        )
    else:
        status, msg = "fail", (
            "The run shows material risk. Resolve escalation, tone, or exploit failures before deployment."
        )

    render_html(f"""
    <div class="snt-score-lux">
      {render_score_ring(score)}
      <div class="snt-score-meta">
        <h3>Overall assurance score</h3>
        <p>{msg}</p>
        {render_status_badge(status)}
      </div>
    </div>
    """)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sessions", total_sessions)
    m2.metric("Flagged", flagged)
    m3.metric("Turns", total_turns)
    m4.metric("Breaches", failed_turns)

    chart_col, dl_col = st.columns([1.6, 1])
    with chart_col:
        render_html(render_category_breakdown(compute_breakdown(results)))
    with dl_col:
        render_html("<div style='height:2.5rem;'></div>")
        if st.session_state.report_text:
            st.download_button(
                "Export audit report",
                data=st.session_state.report_text,
                file_name="ai_safety_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

    render_html(
        render_section_header(
            "Evidence",
            "Session review",
            "Per-session breakdown with failed turn detail and pass-rate indicators.",
        )
    )
    cards = "".join(render_session_card(r) for r in results)
    render_html(f'<div class="snt-session-list">{cards}</div>')

render_html("<div style='height:2rem;'></div>")
render_html(render_trust_seals())
render_html(render_footer())
