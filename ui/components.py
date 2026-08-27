"""Reusable UI building blocks for the enterprise interface."""

from config import get_config
from ui.brand import BRAND_NAME, BRAND_TAGLINE, BRAND_VERSION, render_logo
from ui.render import clean_html

_ICON_BEHAVIOR = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h10M4 17h7"/><path d="M18 15l2 2 4-4" transform="translate(-2 -2)"/></svg>'
_ICON_SECURITY = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3l7 4v5c0 5-3 7.5-7 9-4-1.5-7-4-7-9V7l7-4z"/><path d="M9.5 12.5l1.8 1.8 3.5-4"/></svg>'
_ICON_REPORT = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3h6l5 5v13H8z"/><path d="M14 3v5h5M10 13h6M10 17h6"/></svg>'


def render_hero_cinema(video_url: str = "") -> str:
    """Render a premium interactive hero panel."""
    return clean_html("""
    <section class="snt-hero" aria-label="SNT AI platform introduction">
      <div class="snt-hero-grid-overlay"></div>
      <div class="snt-hero-glow"></div>
      <div class="snt-hero-glow-2"></div>
      <div class="snt-hero-inner">
        <div class="snt-hero-grid">
          <div class="snt-hero-copy snt-fade-up">
            <div class="snt-hero-eyebrow">
              <span class="snt-hero-eyebrow-dot"></span>
              Enterprise AI assurance
            </div>
            <h1 class="snt-hero-title">
              <span class="snt-hero-title-gradient">Operational confidence</span><br>
              for <span class="snt-hero-accent-word">customer-facing</span> AI
            </h1>
            <p class="snt-hero-lead">
              Run structured stress tests, review evidence by scenario, and export
              audit-ready reports from a platform designed for risk, compliance, and QA teams.
            </p>
            <div class="snt-hero-actions">
              <a href="/Evaluation_Dashboard" class="snt-hero-btn snt-hero-btn-primary">
                Open evaluation workspace
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </a>
              <a href="#" class="snt-hero-btn snt-hero-btn-secondary">
                View documentation
              </a>
            </div>
          </div>
          <div class="snt-hero-panel snt-fade-up snt-delay-2">
            <div class="snt-hero-panel-head">
              <span>Deployment profile</span>
              <span class="snt-hero-panel-badge">v3.0</span>
            </div>
            <div class="snt-hero-metric-grid">
              <div class="snt-hero-metric">
                <p class="snt-hero-metric-value">5</p>
                <p class="snt-hero-metric-label">Active scenarios</p>
              </div>
              <div class="snt-hero-metric">
                <p class="snt-hero-metric-value">3</p>
                <p class="snt-hero-metric-label">Core controls</p>
              </div>
              <div class="snt-hero-metric">
                <p class="snt-hero-metric-value">100%</p>
                <p class="snt-hero-metric-label">Replayable runs</p>
              </div>
              <div class="snt-hero-metric">
                <p class="snt-hero-metric-value">TXT</p>
                <p class="snt-hero-metric-label">Audit export</p>
              </div>
            </div>
            <div class="snt-hero-note">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
              Built for internal validation, governance review, and release-readiness programs.
            </div>
          </div>
        </div>
      </div>
    </section>""")


def render_section_header(
    kicker: str,
    title: str,
    description: str = "",
) -> str:
    desc = f'<p class="snt-section-desc">{description}</p>' if description else ""
    return clean_html(f"""
    <div class="snt-section-head snt-fade-up">
      <p class="snt-section-kicker">{kicker}</p>
      <h2 class="snt-section-title">{title}</h2>
      {desc}
    </div>""")


def render_luxury_metrics(metrics: list[tuple[str, str]]) -> str:
    cells = "".join(
        f'<div class="snt-lux-metric"><p class="snt-lux-metric-val">{val}</p>'
        f'<p class="snt-lux-metric-lbl">{lbl}</p></div>'
        for val, lbl in metrics
    )
    return clean_html(f'<div class="snt-lux-metrics">{cells}</div>')


def render_pillar_card(number: str, icon: str, title: str, description: str) -> str:
    return clean_html(f"""
    <article class="snt-pillar">
      <div class="snt-pillar-icon">{icon}</div>
      <p class="snt-pillar-num">{number}</p>
      <h3 class="snt-pillar-title">{title}</h3>
      <p class="snt-pillar-desc">{description}</p>
    </article>""")


def render_pillars() -> str:
    return clean_html(
        '<div class="snt-pillars snt-fade-up">'
        + render_pillar_card(
            "01",
            _ICON_BEHAVIOR,
            "Scenario simulation",
            "Model difficult customers, vulnerable users, and adversarial actors in a controlled evaluation loop.",
        )
        + render_pillar_card(
            "02",
            _ICON_SECURITY,
            "Security resilience",
            "Test prompt-injection resistance, leakage boundaries, and unsafe output behavior with explicit scoring rules.",
        )
        + render_pillar_card(
            "03",
            _ICON_REPORT,
            "Audit reporting",
            "Generate plain-language summaries, failure matrices, and executive-ready evidence packages for review.",
        )
        + "</div>"
    )


def render_timeline() -> str:
    return clean_html("""
    <div class="snt-timeline snt-fade-up">
      <div class="snt-timeline-step">
        <div class="snt-timeline-dot">01</div>
        <p class="snt-timeline-title">Prepare scope</p>
        <p class="snt-timeline-desc">
          Select deterministic inputs, seed values, and failure conditions for the evaluation batch.
        </p>
      </div>
      <div class="snt-timeline-step">
        <div class="snt-timeline-dot">02</div>
        <p class="snt-timeline-title">Run evidence capture</p>
        <p class="snt-timeline-desc">
          Execute session-by-session tests and score every turn against behavioral and security controls.
        </p>
      </div>
      <div class="snt-timeline-step">
        <div class="snt-timeline-dot">03</div>
        <p class="snt-timeline-title">Review and report</p>
        <p class="snt-timeline-desc">
          Review flagged sessions, share report artifacts, and use findings to guide remediation.
        </p>
      </div>
    </div>""")


def render_cta_lux() -> str:
    return clean_html("""
    <div class="snt-cta-lux snt-fade-up">
      <h3>Start a structured evaluation</h3>
      <p>
        Use the dashboard to run repeatable audits and review operational evidence in one place.
      </p>
      <a href="/Evaluation_Dashboard" class="snt-hero-btn snt-hero-btn-primary" style="display: inline-flex;">
        Run an audit now
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
    </div>""")


def render_trust_seals() -> str:
    return clean_html("""
    <div class="snt-seals snt-fade-up">
      <div class="snt-seal">
        <div class="snt-seal-ring">OPS</div>
        <p class="snt-seal-label">Deterministic runs</p>
        <p class="snt-seal-sub">Operational repeatability</p>
      </div>
      <div class="snt-seal">
        <div class="snt-seal-ring">RISK</div>
        <p class="snt-seal-label">Scenario coverage</p>
        <p class="snt-seal-sub">Behavioral and exploit checks</p>
      </div>
      <div class="snt-seal">
        <div class="snt-seal-ring">TXT</div>
        <p class="snt-seal-label">Audit export</p>
        <p class="snt-seal-sub">Portable evidence artifact</p>
      </div>
      <div class="snt-seal">
        <div class="snt-seal-ring">UI</div>
        <p class="snt-seal-label">Accessible interface</p>
        <p class="snt-seal-sub">Clear hierarchy and legibility</p>
      </div>
    </div>""")


def render_footer() -> str:
    config = get_config()
    return clean_html(f"""
    <footer class="snt-footer">
      <div class="snt-footer-inner">
        <div class="snt-footer-col">
          <div class="snt-footer-brand">
            {render_logo(size=38)}
          </div>
          <p class="snt-footer-desc">
            {BRAND_NAME} provides a structured operating model for testing customer-facing AI systems before release.
          </p>
          <div class="snt-footer-social">
            <a href="mailto:{config.support_email}" class="snt-footer-social-link" aria-label="Email support">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </a>
          </div>
        </div>
        <div class="snt-footer-col">
          <p class="snt-footer-heading">Platform</p>
          <ul class="snt-footer-list">
            <li><a href="/" class="snt-footer-link">Overview</a></li>
            <li><a href="/Evaluation_Dashboard" class="snt-footer-link">Evaluation</a></li>
            <li><a href="{config.docs_url}" class="snt-footer-link">Documentation</a></li>
            <li><a href="mailto:{config.support_email}" class="snt-footer-link">Support</a></li>
          </ul>
        </div>
        <div class="snt-footer-col">
          <p class="snt-footer-heading">Assurance</p>
          <ul class="snt-footer-list">
            <li><a href="{config.docs_url}" class="snt-footer-link">Control model</a></li>
            <li><a href="{config.docs_url}" class="snt-footer-link">Evaluation method</a></li>
            <li><a href="{config.docs_url}" class="snt-footer-link">Reporting format</a></li>
            <li><a href="{config.docs_url}" class="snt-footer-link">Deployment guide</a></li>
          </ul>
        </div>
        <div class="snt-footer-col">
          <p class="snt-footer-heading">Company</p>
          <ul class="snt-footer-list">
            <li><a href="mailto:{config.support_email}" class="snt-footer-link">Contact</a></li>
            <li><a href="{config.privacy_url}" class="snt-footer-link">Privacy</a></li>
            <li><a href="{config.terms_url}" class="snt-footer-link">Terms</a></li>
            <li><a href="{config.docs_url}" class="snt-footer-link">Operations</a></li>
          </ul>
        </div>
      </div>
      <div class="snt-footer-bottom">
        <span>&copy; 2026 {BRAND_NAME}. All rights reserved.</span>
        <span>
          <a href="{config.privacy_url}">Privacy Policy</a> &middot;
          <a href="{config.terms_url}">Terms of Service</a> &middot;
          <span class="snt-footer-badge">
            <span class="snt-footer-badge-dot"></span>
            v{BRAND_VERSION}
          </span>
        </span>
      </div>
    </footer>""")


def render_status_badge(status: str) -> str:
    mapping = {
        "pass": ("snt-badge-pass", "Pass"),
        "review": ("snt-badge-warn", "Review Required"),
        "fail": ("snt-badge-fail", "Action Required"),
        "ok": ("snt-badge-ok", "Passed"),
        "flagged": ("snt-badge-fail", "Flagged"),
        "idle": ("snt-badge-neutral", "Not Run"),
    }
    css, label = mapping.get(status, ("snt-badge-neutral", status))
    return f'<span class="snt-badge {css}">{label}</span>'


def render_score_ring(score: float, size: int = 140) -> str:
    pct = max(0.0, min(100.0, score))
    radius = 58
    circumference = 2 * 3.14159 * radius
    offset = circumference - (pct / 100) * circumference
    if pct >= 80:
        stroke = "#34D399"
    elif pct >= 50:
        stroke = "#FBBF24"
    else:
        stroke = "#F87171"

    return clean_html(f"""
    <div class="snt-score-ring-wrap">
      <svg width="{size}" height="{size}" viewBox="0 0 140 140" aria-hidden="true">
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="6"/>
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="{stroke}" stroke-width="6"
                stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"
                stroke-linecap="round"/>
      </svg>
      <div class="snt-score-ring-val">
        <span class="snt-score-num">{score:.0f}</span>
        <span class="snt-score-unit">Safety score</span>
      </div>
    </div>""")


def render_session_card(session: dict) -> str:
    name = session["customer_name"]
    emo = session["emotional_state"]
    tier = session["account_tier"]
    literacy = session["digital_literacy"]
    failed = session["session_failed"]
    badge = render_status_badge("flagged" if failed else "ok")

    turns = session.get("turn_results", [])
    passed = sum(1 for t in turns if t["passed"])
    total = len(turns)
    rate = (passed / total * 100) if total else 0

    if failed:
        reasons = session.get("failure_reasons", [])
        detail = f'<p class="snt-session-reasons">{"; ".join(reasons)}</p>'
    else:
        detail = '<p class="snt-session-ok">All conversational turns passed evaluation.</p>'

    table = ""
    failed_turns = [t for t in turns if not t["passed"]]
    if failed_turns:
        rows = ""
        for t in failed_turns:
            text = t["user_text"][:80] + ("\u2026" if len(t["user_text"]) > 80 else "")
            rows += f"""
            <tr>
              <td>Turn {t['turn_id']}</td>
              <td class="fail">{t['reason']}</td>
              <td>{text}</td>
            </tr>"""
        table = f"""
        <div class="snt-table-wrap">
          <table class="snt-table">
            <thead><tr><th>Turn</th><th>Issue</th><th>User input</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    return clean_html(f"""
    <article class="snt-session">
      <div class="snt-session-head">
        <div>
          <p class="snt-session-name">{name}</p>
          <p class="snt-session-meta">
            {emo} &middot; {tier} &middot; Literacy {literacy}/10 &middot; {rate:.0f}% pass rate
          </p>
        </div>
        {badge}
      </div>
      {detail}
      {table}
    </article>""")


def render_empty_state() -> str:
    return clean_html("""
    <div class="snt-empty">
      <div class="snt-empty-icon">\u2022</div>
      <p class="snt-empty-title">Ready to evaluate</p>
      <p class="snt-empty-desc">
        Choose a seed and failure rate, then run the audit to generate evidence and report output.
      </p>
    </div>""")
