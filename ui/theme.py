"""Global CSS for the premium enterprise UI shell."""

from ui.render import clean_html, render_html

GLOBAL_STYLES = clean_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --snt-bg: #0A0D1A;
  --snt-surface: #11152B;
  --snt-surface-muted: rgba(255,255,255,0.03);
  --snt-surface-elevated: #1A1F3A;
  --snt-border: rgba(255,255,255,0.06);
  --snt-border-strong: rgba(255,255,255,0.12);
  --snt-ink: #FFFFFF;
  --snt-ink-secondary: #ADB5CC;
  --snt-ink-muted: #737A9A;
  --snt-ink-faint: #4A5280;
  --snt-accent: #4F7CFF;
  --snt-accent-deep: #3A5FE0;
  --snt-accent-glow: #6B8FFF;
  --snt-accent-mist: rgba(79,124,255,0.10);
  --snt-gold: #F0B429;
  --snt-green: #34D399;
  --snt-green-deep: #10B981;
  --snt-success: #34D399;
  --snt-success-bg: rgba(52,211,153,0.10);
  --snt-warning: #FBBF24;
  --snt-warning-bg: rgba(251,191,36,0.10);
  --snt-danger: #F87171;
  --snt-danger-bg: rgba(248,113,113,0.10);
  --snt-glass-bg: rgba(17,21,43,0.65);
  --snt-glass-border: rgba(255,255,255,0.08);
  --snt-glass-shadow: 0 8px 32px rgba(0,0,0,0.4);
  --snt-shadow-xs: 0 2px 8px rgba(0,0,0,0.2);
  --snt-shadow-sm: 0 8px 24px rgba(0,0,0,0.3);
  --snt-shadow-md: 0 16px 48px rgba(0,0,0,0.4);
  --snt-shadow-glow: 0 0 20px rgba(79,124,255,0.15);
  --snt-radius-sm: 8px;
  --snt-radius-md: 12px;
  --snt-radius-lg: 16px;
  --snt-radius-xl: 24px;
  --snt-radius-2xl: 32px;
  --snt-font-display: 'Google Sans Text', Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --snt-font-body: 'Google Sans Text', Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --snt-font-mono: 'JetBrains Mono', 'SF Mono', ui-monospace, monospace;
  --snt-max-width: 1200px;
  --snt-grid: 1.2rem;
}

html.snt-light {
  --snt-bg: #F4F6FA;
  --snt-surface: #FFFFFF;
  --snt-surface-muted: #F1F3F8;
  --snt-surface-elevated: #FFFFFF;
  --snt-border: #E2E6EE;
  --snt-border-strong: #CBD0DC;
  --snt-ink: #0A0D1A;
  --snt-ink-secondary: #4A5070;
  --snt-ink-muted: #737A9A;
  --snt-ink-faint: #ADB5CC;
  --snt-accent: #4F7CFF;
  --snt-accent-deep: #3A5FE0;
  --snt-accent-glow: #6B8FFF;
  --snt-accent-mist: rgba(79,124,255,0.08);
  --snt-glass-bg: rgba(255,255,255,0.7);
  --snt-glass-border: rgba(0,0,0,0.06);
  --snt-glass-shadow: 0 8px 32px rgba(0,0,0,0.06);
  --snt-shadow-xs: 0 2px 8px rgba(0,0,0,0.04);
  --snt-shadow-sm: 0 8px 24px rgba(0,0,0,0.05);
  --snt-shadow-md: 0 16px 48px rgba(0,0,0,0.08);
  --snt-shadow-glow: 0 0 20px rgba(79,124,255,0.12);
  --snt-success-bg: #ECFDF5;
  --snt-warning-bg: #FFF7ED;
  --snt-danger-bg: #FEF2F2;
}

*, *::before, *::after { box-sizing: border-box; }

body, html, [class*="css"], .stApp {
  background: var(--snt-bg) !important;
  color: var(--snt-ink-secondary);
  font-family: var(--snt-font-body);
  font-size: 15px;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0 !important; }
.stDeployButton { display: none; }
.block-container { max-width: var(--snt-max-width) !important; padding: 0 2rem 5rem !important; }

h1, h2, h3, h4 {
  color: var(--snt-ink) !important;
  font-family: var(--snt-font-display);
  font-weight: 600;
  letter-spacing: -0.02em;
}

a { color: var(--snt-accent); text-decoration: none; transition: color 0.2s; }
a:hover { color: var(--snt-accent-glow); }

.stButton > button, .stDownloadButton > button {
  min-height: 48px;
  border-radius: 12px !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  border: 1px solid var(--snt-border-strong) !important;
  box-shadow: none !important;
  transition: all 0.25s ease !important;
  letter-spacing: 0.01em;
}
.stButton > button {
  background: var(--snt-accent) !important;
  color: #FFFFFF !important;
  border-color: var(--snt-accent) !important;
}
.stButton > button:hover {
  background: var(--snt-accent-glow) !important;
  border-color: var(--snt-accent-glow) !important;
  transform: translateY(-1px);
  box-shadow: var(--snt-shadow-glow) !important;
}
.stDownloadButton > button {
  background: var(--snt-surface) !important;
  color: var(--snt-accent) !important;
}
.stDownloadButton > button:hover {
  background: var(--snt-accent-mist) !important;
  transform: translateY(-1px);
}

[data-testid="stMetric"] {
  background: var(--snt-surface) !important;
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-md);
  padding: 1rem 1.25rem;
  box-shadow: var(--snt-shadow-xs);
}
[data-testid="stMetricLabel"] {
  color: var(--snt-ink-muted) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
  color: var(--snt-ink) !important;
  font-family: var(--snt-font-mono) !important;
}

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--snt-border-strong); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--snt-ink-muted); }

/* ── Navigation ─────────────────────────────────────────────────────────── */
.snt-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(10,13,26,0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--snt-border);
  transition: background 0.3s;
}
html.snt-light .snt-nav {
  background: rgba(244,246,250,0.85);
}
.snt-nav-inner {
  max-width: var(--snt-max-width);
  margin: 0 auto;
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.snt-nav-brand { display: flex; align-items: center; }
.snt-nav-links { display: flex; align-items: center; gap: 0.25rem; }
.snt-nav-link {
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--snt-ink-muted);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}
.snt-nav-link:hover { color: var(--snt-ink); background: var(--snt-accent-mist); }
.snt-nav-link--active { color: var(--snt-ink); background: var(--snt-accent-mist); }
.snt-nav-link-label { position: relative; }
.snt-nav-link--active .snt-nav-link-label::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--snt-accent);
  border-radius: 999px;
}
.snt-nav-toggle { display: none; }
.snt-nav-spacer { height: 0; }

.snt-theme-toggle {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--snt-border);
  border-radius: 999px;
  background: var(--snt-surface);
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 0.5rem;
}
.snt-theme-toggle:hover { border-color: var(--snt-ink-muted); background: var(--snt-surface-elevated); }
.snt-theme-toggle svg { width: 16px; height: 16px; stroke: var(--snt-ink); fill: none; stroke-width: 1.8; }
.snt-theme-toggle .snt-theme-sun { display: none; }
.snt-theme-toggle .snt-theme-moon { display: block; }
html.snt-light .snt-theme-toggle .snt-theme-sun { display: block; }
html.snt-light .snt-theme-toggle .snt-theme-moon { display: none; }

/* ── Animations ─────────────────────────────────────────────────────────── */
@keyframes sntFadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes sntFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes sntGradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes sntFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes sntGridPulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}
@keyframes sntCountUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes sntGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(79,124,255,0.15); }
  50% { box-shadow: 0 0 40px rgba(79,124,255,0.3); }
}
@keyframes sntShimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.snt-fade-up { animation: sntFadeUp 0.7s ease forwards; }
.snt-fade-in { animation: sntFadeIn 0.7s ease forwards; }
.snt-delay-1 { animation-delay: 0.1s; }
.snt-delay-2 { animation-delay: 0.2s; }
.snt-delay-3 { animation-delay: 0.3s; }
.snt-delay-4 { animation-delay: 0.4s; }
.snt-delay-5 { animation-delay: 0.5s; }

/* ── Hero Section ───────────────────────────────────────────────────────── */
.snt-hero {
  position: relative;
  min-height: 85vh;
  display: flex;
  align-items: center;
  padding: 6rem 0 3rem;
  margin: 0 -2rem;
  overflow: hidden;
}
.snt-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0A0D1A 0%, #1A1040 40%, #0F1630 70%, #0A0D1A 100%);
  background-size: 200% 200%;
  animation: sntGradientShift 15s ease infinite;
  z-index: 0;
}
html.snt-light .snt-hero::before {
  background: linear-gradient(135deg, #F4F6FA 0%, #E8ECF8 40%, #F0F2FA 70%, #F4F6FA 100%);
}
.snt-hero-grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(79,124,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(79,124,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: sntGridPulse 8s ease infinite;
  z-index: 1;
}
.snt-hero-glow {
  position: absolute;
  top: -20%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(79,124,255,0.12) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
}
.snt-hero-glow-2 {
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(240,180,41,0.06) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
}
.snt-hero-inner {
  position: relative;
  z-index: 2;
  max-width: var(--snt-max-width);
  margin: 0 auto;
  padding: 0 2rem;
  width: 100%;
}
.snt-hero-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 3rem;
  align-items: center;
}
.snt-hero-copy { padding: 0; }
.snt-hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem;
  background: var(--snt-accent-mist);
  border: 1px solid rgba(79,124,255,0.15);
  border-radius: 999px;
  color: var(--snt-accent-glow);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}
.snt-hero-eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--snt-accent-glow);
  animation: sntGlow 2s ease infinite;
}
.snt-hero-title {
  font-size: clamp(2.4rem, 5vw, 4rem);
  line-height: 1.08;
  margin: 0 0 1.25rem;
  letter-spacing: -0.03em;
  font-weight: 700;
  color: var(--snt-ink) !important;
}
.snt-hero-title-gradient {
  background: linear-gradient(135deg, #FFFFFF 0%, #ADB5CC 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
html.snt-light .snt-hero-title-gradient {
  background: linear-gradient(135deg, #0A0D1A 0%, #4A5070 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.snt-hero-accent-word {
  background: linear-gradient(135deg, var(--snt-accent), var(--snt-accent-glow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.snt-hero-lead {
  font-size: 1.05rem;
  line-height: 1.65;
  color: var(--snt-ink-muted);
  max-width: 520px;
  margin: 0 0 2rem;
}
.snt-hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.snt-hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.25s ease;
  cursor: pointer;
  border: none;
  font-family: inherit;
  letter-spacing: 0.01em;
}
.snt-hero-btn-primary {
  background: linear-gradient(135deg, var(--snt-accent), var(--snt-accent-glow));
  color: #FFFFFF;
  box-shadow: 0 4px 15px rgba(79,124,255,0.3);
}
.snt-hero-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(79,124,255,0.4);
  color: #FFFFFF;
}
.snt-hero-btn-secondary {
  background: var(--snt-glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--snt-border-strong);
  color: var(--snt-ink-secondary);
}
.snt-hero-btn-secondary:hover {
  background: var(--snt-surface-elevated);
  border-color: var(--snt-ink-muted);
  transform: translateY(-2px);
  color: var(--snt-ink);
}

/* Hero Panel (glass metrics) */
.snt-hero-panel {
  background: var(--snt-glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--snt-glass-border);
  border-radius: var(--snt-radius-2xl);
  padding: 1.75rem;
  box-shadow: var(--snt-glass-shadow);
}
.snt-hero-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--snt-border);
  color: var(--snt-ink-secondary);
  font-size: 0.82rem;
  font-weight: 500;
}
.snt-hero-panel-badge {
  padding: 0.2rem 0.6rem;
  background: var(--snt-accent-mist);
  border: 1px solid rgba(79,124,255,0.15);
  border-radius: 999px;
  color: var(--snt-accent-glow);
  font-size: 0.7rem;
  font-weight: 600;
}
.snt-hero-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.snt-hero-metric {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-md);
  padding: 1rem;
  transition: all 0.25s ease;
}
.snt-hero-metric:hover {
  background: rgba(255,255,255,0.05);
  border-color: var(--snt-border-strong);
  transform: translateY(-1px);
}
html.snt-light .snt-hero-metric {
  background: rgba(0,0,0,0.02);
}
html.snt-light .snt-hero-metric:hover {
  background: rgba(0,0,0,0.03);
}
.snt-hero-metric-value {
  margin: 0;
  background: linear-gradient(135deg, var(--snt-ink), var(--snt-ink-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--snt-font-display);
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.snt-hero-metric-label {
  margin: 0.3rem 0 0;
  color: var(--snt-ink-muted);
  font-size: 0.78rem;
  font-weight: 500;
}
.snt-hero-note {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--snt-border);
  color: var(--snt-ink-faint);
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.snt-hero-note svg { width: 14px; height: 14px; flex-shrink: 0; }

/* ── Sections ───────────────────────────────────────────────────────────── */
.snt-section-head {
  margin-bottom: 2rem;
  text-align: center;
}
.snt-section-kicker {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--snt-accent-glow);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}
.snt-section-kicker::before,
.snt-section-kicker::after {
  content: '';
  width: 24px;
  height: 1px;
  background: var(--snt-accent);
  opacity: 0.4;
}
.snt-section-title {
  font-size: clamp(1.6rem, 3vw, 2.6rem);
  line-height: 1.15;
  margin: 0 0 0.75rem;
  letter-spacing: -0.02em;
  font-weight: 700;
}
.snt-section-desc {
  color: var(--snt-ink-muted);
  font-size: 0.95rem;
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ── Luxury Metrics ─────────────────────────────────────────────────────── */
.snt-lux-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 4rem;
}
.snt-lux-metric {
  background: var(--snt-surface);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-lg);
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.snt-lux-metric::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--snt-accent);
  opacity: 0;
  transition: opacity 0.3s;
}
.snt-lux-metric:hover {
  border-color: var(--snt-border-strong);
  transform: translateY(-3px);
  box-shadow: var(--snt-shadow-md);
}
.snt-lux-metric:hover::before { opacity: 1; }
.snt-lux-metric-val {
  margin: 0;
  background: linear-gradient(135deg, var(--snt-accent), var(--snt-accent-glow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--snt-font-display);
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.snt-lux-metric-lbl {
  margin: 0.4rem 0 0;
  color: var(--snt-ink-muted);
  font-size: 0.85rem;
  font-weight: 500;
}

/* ── Pillars ─────────────────────────────────────────────────────────────── */
.snt-pillars {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 4rem;
}
.snt-pillar {
  background: var(--snt-surface);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-xl);
  padding: 2rem 1.75rem;
  transition: all 0.35s ease;
  position: relative;
  overflow: hidden;
}
.snt-pillar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--snt-accent), transparent);
  opacity: 0;
  transition: opacity 0.35s;
}
.snt-pillar:hover {
  border-color: var(--snt-border-strong);
  transform: translateY(-4px);
  box-shadow: var(--snt-shadow-md);
}
.snt-pillar:hover::after { opacity: 1; }
.snt-pillar-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--snt-accent-mist);
  border: 1px solid rgba(79,124,255,0.12);
  color: var(--snt-accent-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  transition: all 0.3s;
}
.snt-pillar:hover .snt-pillar-icon {
  background: var(--snt-accent);
  color: #FFFFFF;
  border-color: var(--snt-accent);
}
.snt-pillar-num {
  color: var(--snt-ink-faint);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}
.snt-pillar-title {
  color: var(--snt-ink);
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0 0 0.6rem;
  letter-spacing: -0.01em;
}
.snt-pillar-desc {
  color: var(--snt-ink-muted);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

/* ── Timeline ────────────────────────────────────────────────────────────── */
.snt-timeline {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 4rem;
  position: relative;
}
.snt-timeline::before {
  content: '';
  position: absolute;
  top: 32px;
  left: calc(16.67% + 1rem);
  right: calc(16.67% + 1rem);
  height: 2px;
  background: linear-gradient(90deg, var(--snt-accent), var(--snt-accent-mist), var(--snt-accent));
  opacity: 0.3;
}
.snt-timeline-step {
  background: var(--snt-surface);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-lg);
  padding: 1.75rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
}
.snt-timeline-step:hover {
  border-color: var(--snt-border-strong);
  transform: translateY(-2px);
  box-shadow: var(--snt-shadow-sm);
}
.snt-timeline-dot {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: var(--snt-accent-mist);
  border: 2px solid var(--snt-accent);
  color: var(--snt-accent-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  margin: 0 auto 1rem;
  position: relative;
  z-index: 1;
}
.snt-timeline-title {
  color: var(--snt-ink);
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}
.snt-timeline-desc {
  color: var(--snt-ink-muted);
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0;
}

/* ── CTA ─────────────────────────────────────────────────────────────────── */
.snt-cta-lux {
  background: var(--snt-surface);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-2xl);
  padding: 3rem 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  overflow: hidden;
}
.snt-cta-lux::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--snt-accent), var(--snt-gold), var(--snt-accent));
  background-size: 200% 100%;
  animation: sntGradientShift 4s ease infinite;
}
.snt-cta-lux h3 {
  color: var(--snt-ink) !important;
  font-size: 1.8rem !important;
  margin: 0 0 0.75rem !important;
  letter-spacing: -0.02em;
}
.snt-cta-lux p {
  margin: 0 auto 1.5rem;
  max-width: 34rem;
  color: var(--snt-ink-muted);
  font-size: 0.95rem;
}

/* ── Trust Seals ─────────────────────────────────────────────────────────── */
.snt-seals {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-top: 1rem;
  margin-bottom: 2rem;
}
.snt-seal {
  background: var(--snt-surface);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-lg);
  padding: 1.25rem 1rem;
  text-align: center;
  transition: all 0.25s ease;
}
.snt-seal:hover {
  border-color: var(--snt-border-strong);
  transform: translateY(-2px);
}
.snt-seal-ring {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: var(--snt-accent-mist);
  border: 1px solid rgba(79,124,255,0.15);
  color: var(--snt-accent-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.72rem;
  margin: 0 auto 0.75rem;
}
.snt-seal-label {
  color: var(--snt-ink);
  font-weight: 600;
  margin: 0 0 0.2rem;
  font-size: 0.82rem;
}
.snt-seal-sub {
  color: var(--snt-ink-muted);
  font-size: 0.75rem;
  margin: 0;
}

/* ── Footer ─────────────────────────────────────────────────────────────── */
.snt-footer {
  margin-top: 4rem;
  padding-top: 3rem;
  border-top: 1px solid var(--snt-border);
}
.snt-footer-inner {
  display: grid;
  grid-template-columns: 1.8fr 1fr 1fr 1fr;
  gap: 2.5rem;
}
.snt-footer-heading {
  color: var(--snt-ink);
  font-size: 0.78rem;
  font-weight: 700;
  margin: 0 0 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.snt-footer-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 0.6rem; }
.snt-footer-link, .snt-footer-bottom a {
  color: var(--snt-ink-muted);
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.2s;
}
.snt-footer-link:hover, .snt-footer-bottom a:hover { color: var(--snt-accent-glow); }
.snt-footer-col:first-child { display: flex; flex-direction: column; gap: 0.75rem; }
.snt-footer-desc {
  color: var(--snt-ink-muted);
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0;
}
.snt-footer-social { display: flex; gap: 0.65rem; }
.snt-footer-social-link {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--snt-border);
  border-radius: 999px;
  transition: all 0.2s;
  color: var(--snt-ink-muted);
}
.snt-footer-social-link:hover {
  border-color: var(--snt-accent);
  color: var(--snt-accent);
  background: var(--snt-accent-mist);
}
.snt-footer-bottom {
  margin-top: 2.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--snt-border);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  color: var(--snt-ink-faint);
  font-size: 0.78rem;
}
.snt-footer-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  border: 1px solid var(--snt-border);
}
.snt-footer-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--snt-accent);
  animation: sntGlow 2s ease infinite;
}

/* ── Dashboard Components ────────────────────────────────────────────────── */
.snt-dash-hero { margin: 1.5rem 0 1.5rem; padding-bottom: 1rem; }
.snt-control-lux, .snt-score-lux, .snt-chart-panel, .snt-session, .snt-empty {
  background: var(--snt-surface);
  border: 1px solid var(--snt-border);
  border-radius: var(--snt-radius-lg);
  padding: 1.5rem;
}
.snt-score-lux {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2rem;
  align-items: center;
}
.snt-score-ring-wrap { position: relative; width: 140px; height: 140px; margin: 0 auto; }
.snt-score-ring-val {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.snt-score-num { font-family: var(--snt-font-mono); font-size: 2rem; color: var(--snt-ink); }
.snt-score-unit { color: var(--snt-ink-muted); text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.03em; }

.snt-badge {
  display: inline-flex;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  border: 1px solid transparent;
}
.snt-badge-pass, .snt-badge-ok { color: var(--snt-success); background: var(--snt-success-bg); }
.snt-badge-warn { color: var(--snt-warning); background: var(--snt-warning-bg); }
.snt-badge-fail { color: var(--snt-danger); background: var(--snt-danger-bg); }
.snt-badge-neutral { color: var(--snt-ink-muted); background: var(--snt-surface-muted); border-color: var(--snt-border); }

.snt-chart-row { margin-bottom: 1rem; }
.snt-chart-meta { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 0.4rem; }
.snt-chart-label { color: var(--snt-ink-secondary); font-size: 0.85rem; }
.snt-chart-val { font-family: var(--snt-font-mono); color: var(--snt-ink-muted); font-size: 0.8rem; }
.snt-chart-track { height: 8px; background: var(--snt-surface-muted); border-radius: 999px; overflow: hidden; }
.snt-chart-fill { height: 100%; background: linear-gradient(90deg, var(--snt-accent), var(--snt-accent-glow)); border-radius: 999px; }

.snt-session-list { display: grid; gap: 1rem; }
.snt-session-head { display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.snt-session-name { color: var(--snt-ink); font-size: 1rem; font-weight: 600; margin: 0 0 0.2rem; }
.snt-session-meta { color: var(--snt-ink-muted); font-size: 0.82rem; }
.snt-session-reasons { color: var(--snt-danger); font-size: 0.9rem; margin: 0.8rem 0 0; }
.snt-session-ok { color: var(--snt-success); font-size: 0.9rem; margin: 0.8rem 0 0; }
.snt-table-wrap { margin-top: 1rem; overflow: hidden; border: 1px solid var(--snt-border); border-radius: 12px; }
.snt-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.snt-table th {
  text-align: left;
  padding: 0.8rem 1rem;
  background: var(--snt-surface-muted);
  color: var(--snt-ink-muted);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.snt-table td {
  padding: 0.85rem 1rem;
  border-top: 1px solid var(--snt-border);
  color: var(--snt-ink-secondary);
}
.snt-table .fail { color: var(--snt-danger); font-weight: 600; }

.snt-empty { text-align: center; }
.snt-empty-icon {
  width: 54px;
  height: 54px;
  border-radius: 999px;
  background: var(--snt-accent-mist);
  border: 1px solid rgba(79,124,255,0.12);
  color: var(--snt-accent-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-size: 1.3rem;
}
.snt-empty-title { color: var(--snt-ink); font-size: 1rem; font-weight: 600; margin: 0 0 0.4rem; }
.snt-empty-desc { color: var(--snt-ink-muted); font-size: 0.88rem; max-width: 400px; margin: 0 auto; }

.snt-logo-wrap { display: flex; align-items: center; gap: 0.75rem; }
.snt-wordmark { display: flex; flex-direction: column; line-height: 1.15; }
.snt-wordmark-name { color: var(--snt-ink); font-size: 1rem; font-weight: 700; }
.snt-wordmark-tag { color: var(--snt-ink-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }
.snt-wordmark-dark { color: var(--snt-ink) !important; }
.snt-wordmark-tag-dark { color: var(--snt-ink-muted) !important; }

/* ── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .snt-hero-grid, .snt-footer-inner, .snt-score-lux { grid-template-columns: 1fr; }
  .snt-seals { grid-template-columns: repeat(2, 1fr); }
  .snt-timeline { grid-template-columns: 1fr; }
  .snt-timeline::before { display: none; }
  .snt-lux-metrics { grid-template-columns: repeat(2, 1fr); }
  .snt-pillars { grid-template-columns: 1fr; }
  .snt-hero { min-height: auto; padding: 5rem 0 2rem; margin: 0 -1rem; }
  .snt-hero-actions { flex-direction: column; }
  .snt-hero-btn { justify-content: center; }
}

@media (max-width: 720px) {
  .block-container { padding: 0 1rem 4rem !important; }
  .snt-nav-inner { padding: 0.65rem 1rem; }
  .snt-nav-links { gap: 0.15rem; }
  .snt-hero-metric-grid, .snt-lux-metrics, .snt-pillars, .snt-seals { grid-template-columns: 1fr; }
  .snt-hero-panel { padding: 1.25rem; }
  .snt-cta-lux { padding: 2rem 1.5rem; }
  .snt-footer-inner { grid-template-columns: 1fr; gap: 1.5rem; }
}
</style>
<script>
(function() {
  var key = "snt-theme";
  var html = document.documentElement;
  try {
    var saved = localStorage.getItem(key);
    if (saved === "light") { html.classList.add("snt-light"); }
  } catch (e) {}
  document.addEventListener("click", function(e) {
    var btn = e.target.closest(".snt-theme-toggle");
    if (!btn) return;
    html.classList.toggle("snt-light");
    try {
      localStorage.setItem(key, html.classList.contains("snt-light") ? "light" : "dark");
    } catch (err) {}
  });
})();
</script>
""")


def inject_global_styles() -> None:
    """Inject shared CSS into the active Streamlit page."""
    render_html(GLOBAL_STYLES)
