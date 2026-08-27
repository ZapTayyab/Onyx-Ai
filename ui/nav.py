"""Shared top navigation for the application shell."""

from ui.brand import render_logo
from ui.render import render_html


def render_top_nav(over_hero: bool = False) -> None:
    """Render a simple product navigation with a theme toggle."""
    variant = "dark" if over_hero else "light"
    nav_class = "snt-nav snt-nav--hero" if over_hero else "snt-nav"

    render_html(f"""
    <div class="{nav_class}" role="navigation" aria-label="Main navigation">
      <div class="snt-nav-inner">
        <div class="snt-nav-brand">
          {render_logo(size=40, variant=variant)}
        </div>
        <div class="snt-nav-links" id="snt-nav-links">
          <a href="/" class="snt-nav-link">
            <span class="snt-nav-link-label">Overview</span>
          </a>
          <a href="/Evaluation_Dashboard" class="snt-nav-link">
            <span class="snt-nav-link-label">Evaluation</span>
          </a>
          <button class="snt-theme-toggle" id="snt-theme-toggle" aria-label="Toggle theme">
            <svg class="snt-theme-sun" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1" x2="12" y2="3"/>
              <line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1" y1="12" x2="3" y2="12"/>
              <line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <svg class="snt-theme-moon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
        </div>
        <button class="snt-nav-toggle" id="snt-nav-toggle" aria-label="Toggle menu" aria-expanded="false">
          <span class="snt-nav-toggle-bar"></span>
          <span class="snt-nav-toggle-bar"></span>
          <span class="snt-nav-toggle-bar"></span>
        </button>
      </div>
    </div>
    <div class="snt-nav-spacer" style="{"display:none" if over_hero else "display:block"}"></div>
    """)

    render_html("""
    <script>
    (function() {
      var t = document.getElementById('snt-nav-toggle');
      if (t) {
        t.addEventListener('click', function() {
          var e = t.getAttribute('aria-expanded') === 'true' ? 'false' : 'true';
          t.setAttribute('aria-expanded', e);
          document.getElementById('snt-nav-links').classList.toggle('snt-nav-links--open');
        });
      }
      var path = window.location.pathname.replace(new RegExp('/+$'), '') || '/';
      document.querySelectorAll('.snt-nav-link').forEach(function(a) {
        a.classList.remove('snt-nav-link--active');
        var href = a.getAttribute('href').replace(new RegExp('/+$'), '') || '/';
        if (path === href || (path !== '/' && href !== '/' && path.indexOf(href) !== -1)) {
          a.classList.add('snt-nav-link--active');
        }
      });
    })();
    </script>
    """)
