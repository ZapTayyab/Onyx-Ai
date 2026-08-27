"""Brand constants and enterprise-safe logo rendering."""

from ui.render import clean_html

BRAND_NAME = "SNT AI"
BRAND_TAGLINE = "AI Assurance Platform"
BRAND_VERSION = "3.0"


def render_logo(size: int = 40, show_wordmark: bool = True, variant: str = "light") -> str:
    """Return an inline SVG logo with optional wordmark."""
    text_class = "snt-wordmark-name" if variant == "light" else "snt-wordmark-name snt-wordmark-dark"
    tag_class = "snt-wordmark-tag" if variant == "light" else "snt-wordmark-tag snt-wordmark-tag-dark"

    wordmark = ""
    if show_wordmark:
        wordmark = f"""
        <div class="snt-wordmark">
          <span class="{text_class}">{BRAND_NAME}</span>
          <span class="{tag_class}">{BRAND_TAGLINE}</span>
        </div>"""

    return clean_html(f"""
    <div class="snt-logo-wrap">
      <svg class="snt-logo-mark" width="{size}" height="{size}" viewBox="0 0 44 44"
           fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect width="44" height="44" rx="12" fill="#0F172A"/>
        <rect x="0.75" y="0.75" width="42.5" height="42.5" rx="11.25" stroke="#CBD5E1" stroke-opacity="0.28"/>
        <path d="M22 9.5L31 14.4V22.7C31 29 26.9 33.2 22 35.3C17.1 33.2 13 29 13 22.7V14.4L22 9.5Z"
              stroke="#E2E8F0" stroke-width="1.5" fill="none"/>
        <path d="M17 22.2L20.1 25.3L27.2 18.2" stroke="#3B82F6" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {wordmark}
    </div>""")
