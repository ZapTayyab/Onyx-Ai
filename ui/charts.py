"""Dashboard visualization helpers."""

from ui.render import clean_html


def render_category_breakdown(categories: list[tuple[str, float, int, int]]) -> str:
    """Horizontal bar chart for control categories."""
    rows = ""
    for label, pct, passed, total in categories:
        width = max(4, min(100, pct))
        rows += f"""
        <div class="snt-chart-row">
          <div class="snt-chart-meta">
            <span class="snt-chart-label">{label}</span>
            <span class="snt-chart-val">{passed}/{total} · {pct:.0f}%</span>
          </div>
          <div class="snt-chart-track">
            <div class="snt-chart-fill" style="width:{width}%;"></div>
          </div>
        </div>"""

    return clean_html(f"""
    <div class="snt-chart-panel">
      <p class="snt-chart-title">Control coverage</p>
      <div class="snt-chart-rows">{rows}</div>
    </div>""")


def render_session_sparkline(pass_rates: list[float]) -> str:
    """Mini sparkline for session pass rates."""
    if not pass_rates:
        return ""
    w, h = 120, 36
    step = w / max(len(pass_rates) - 1, 1)
    points = " ".join(
        f"{i * step:.1f},{h - (r / 100) * (h - 6) - 3:.1f}"
        for i, r in enumerate(pass_rates)
    )
    return clean_html(f"""
    <svg class="snt-sparkline" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">
      <polyline points="{points}" fill="none" stroke="#6B5FFF" stroke-width="1.5"
                stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""")


def compute_breakdown(results: list[dict]) -> list[tuple[str, float, int, int]]:
    """Derive category stats from audit results."""
    total_turns = sum(len(r["turn_results"]) for r in results)
    if total_turns == 0:
        return []

    def count_fail(keyword: str) -> int:
        return sum(
            1 for r in results for t in r["turn_results"]
            if keyword in t["reason"].lower()
        )

    cats = [
        ("Politeness and tone", "politeness"),
        ("Escalation protocol", "escalat"),
        ("Loop prevention", "loop"),
        ("Exploit resistance", "verif"),
    ]
    out = []
    for label, kw in cats:
        fails = count_fail(kw)
        passed = total_turns - fails
        pct = (passed / total_turns) * 100
        out.append((label, pct, passed, total_turns))
    return out
