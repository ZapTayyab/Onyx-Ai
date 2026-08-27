"""Check logo HTML classes."""
import sys
sys.path.insert(0, ".")
from ui.brand import render_logo
import re
h = render_logo(40)
classes = set()
for m in re.findall(r'class="([^"]+)"', h):
    for c in m.split():
        classes.add(c)
print("Logo classes:", classes)
