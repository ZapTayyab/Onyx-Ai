"""Quick check that component HTML classes exist in CSS selectors."""
import re
import sys
sys.path.insert(0, ".")

from ui.theme import GLOBAL_STYLES
from ui.components import render_footer, render_pillars, render_luxury_metrics, render_timeline, render_hero_cinema, render_cta_lux, render_trust_seals, render_empty_state, render_score_ring, render_session_card
from ui.nav import render_top_nav

css = GLOBAL_STYLES[GLOBAL_STYLES.index("<style>") + 7 : GLOBAL_STYLES.index("</style>")]
selectors = set(re.findall(r"\.([\w-]+)", css))

all_html = " ".join([
    render_footer(),
    render_pillars(),
    render_luxury_metrics([("5", "A"), ("4", "B"), ("3", "C"), ("2", "D")]),
    render_timeline(),
    render_hero_cinema(),
    render_cta_lux(),
    render_trust_seals(),
    render_empty_state(),
    render_score_ring(75),
])

all_classes = set()
for m in re.findall(r'class="([^"]+)"', all_html):
    for c in m.split():
        all_classes.add(c)

missing = all_classes - selectors
if missing:
    print("CLASSES IN HTML BUT NOT IN CSS:")
    for c in sorted(missing):
        print(f"  MISSING: .{c}")
else:
    print("All HTML classes have matching CSS selectors")

unused = selectors - all_classes
if unused:
    # Filter out obvious utility classes that don't appear in HTML
    util = {s for s in unused if s.startswith("snt-")}
    if util:
        print(f"\nCSS selectors not used in components ({len(util)}):")
        for c in sorted(util):
            print(f"  UNUSED: .{c}")

print(f"\nTotal CSS classes: {len(selectors)}, Used in HTML: {len(all_classes)}")
