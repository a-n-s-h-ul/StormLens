from __future__ import annotations

import html

import streamlit as st

from utils.config import APP_NAME


_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');

  :root {
    --storm-bg: #070c14;
    --storm-panel: rgba(16, 25, 40, 0.72);
    --storm-panel-strong: rgba(20, 32, 50, 0.9);
    --storm-line: rgba(255, 255, 255, 0.1);
    --storm-text: #f0f4f8;
    --storm-muted: #94a3bc;
    --storm-cyan: #38bdf8;
    --storm-green: #4ade80;
    --storm-amber: #fbbf24;
    --storm-coral: #fb7185;
    --storm-blur: blur(12px);
    --font-outfit: 'Outfit', sans-serif;
  }

  /* Global Reset & Scrollbars */
  html, body, [data-testid="stAppViewContainer"] {
    font-family: var(--font-outfit);
    background: #050a10 !important;
    color: var(--storm-text);
  }

  [data-testid="stAppViewContainer"] {
    background: 
      radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
      radial-gradient(circle at 100% 100%, rgba(251, 113, 133, 0.08) 0%, transparent 40%),
      #050a10 !important;
    overflow-y: overlay !important;
  }

  [data-testid="stAppViewContainer"]::-webkit-scrollbar { width: 8px; }
  [data-testid="stAppViewContainer"]::-webkit-scrollbar-track { background: transparent; }
  [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb { 
    background: rgba(255,255,255,0.1); 
    border-radius: 10px; 
  }
  [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb:hover { background: var(--storm-cyan); }

  /* Hide Streamlit elements */
  [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
  }

  .block-container {
    padding-top: 1.5rem;
    padding-bottom: 6rem;
    max-width: 1400px;
    animation: fadeIn 0.6s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Typography */
  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-outfit);
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
  }

  /* Components: Selectbox & Inputs */
  div[data-baseweb="select"] > div {
    background: var(--storm-panel) !important;
    border: 1px solid var(--storm-line) !important;
    border-radius: 12px !important;
    backdrop-filter: var(--storm-blur);
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  div[data-baseweb="select"]:hover > div {
    border-color: var(--storm-cyan) !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
  }

  /* Buttons */
  div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    border: 1px solid var(--storm-line) !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 0.5rem 1.5rem !important;
  }
  div[data-testid="stButton"] button:hover {
    border-color: var(--storm-cyan) !important;
    transform: translateY(-2px);
    box-shadow: 0 10px 20px -10px rgba(56, 189, 248, 0.5);
  }
  div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--storm-cyan) 0%, #0ea5e9 100%) !important;
    border: none !important;
    color: #0c1c2c !important;
  }

  /* App Bar */
  .sl-appbar {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: var(--storm-blur);
    border: 1px solid var(--storm-line);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  }

  .sl-brand {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .sl-mark {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--storm-cyan), var(--storm-green));
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-weight: 900;
    color: #070c14;
    font-size: 1.2rem;
    box-shadow: 0 8px 16px rgba(56, 189, 248, 0.3);
  }

  .sl-brand-title {
    font-size: 1.6rem;
    font-weight: 900;
    margin: 0;
  }

  .sl-brand-subtitle {
    color: var(--storm-muted);
    font-size: 0.9rem;
  }

  /* Hero Section */
  .sl-hero {
    position: relative;
    background: linear-gradient(135deg, rgba(16, 25, 40, 0.8), rgba(9, 15, 26, 0.6));
    border: 1px solid var(--storm-line);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    overflow: hidden;
  }
  .sl-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.05) 0%, transparent 70%);
    pointer-events: none;
  }

  .sl-hero-title {
    font-size: 2.5rem;
    font-weight: 900;
    margin-bottom: 0.5rem;
    background: linear-gradient(to right, #fff, var(--storm-muted));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .sl-hero-sub {
    font-size: 1.1rem;
    color: var(--storm-muted);
    max-width: 800px;
    line-height: 1.6;
    margin-bottom: 1rem;
  }

  /* Cards */
  .sl-card {
    background: var(--storm-panel);
    border: 1px solid var(--storm-line);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: var(--storm-blur);
    transition: all 0.3s ease;
  }
  .sl-card:hover {
    border-color: rgba(255,255,255,0.2);
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.3);
  }

  /* KPI Strip */
  .sl-kpi-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
  }
  .sl-kpi {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--storm-line);
    padding: 1.2rem;
    border-radius: 14px;
    text-align: center;
  }
  .sl-kpi-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--storm-cyan);
  }
  .sl-kpi-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--storm-muted);
    margin-top: 0.4rem;
  }

  /* Workflow Steps */
  .sl-workflow {
    display: flex;
    gap: 0.8rem;
    overflow-x: auto;
    padding: 0.5rem 0 1.5rem 0;
  }
  .sl-step {
    min-width: 160px;
    background: rgba(255,255,255,0.03);
    border-left: 4px solid var(--storm-cyan);
    padding: 1rem;
    border-radius: 0 10px 10px 0;
  }
  .sl-step-index { font-size: 0.7rem; color: var(--storm-muted); font-weight: 800; }
  .sl-step-title { font-weight: 700; font-size: 0.9rem; }

  /* Pill */
  .sl-pill {
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.2);
    padding: 0.4rem 1rem;
    border-radius: 100px;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--storm-cyan);
    display: inline-block;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
  }

  /* Dataframe Styling */
  [data-testid="stDataFrame"] {
    background: var(--storm-panel);
    border-radius: 12px;
    padding: 0.5rem;
    border: 1px solid var(--storm-line);
  }
  
  [data-testid="stStatusWidget"] {
    display: none;
  }

  /* Smooth scroll */
  * {
    scroll-behavior: smooth;
  }
</style>
"""

def apply_global_style() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

def app_header(selected_page: str) -> None:
    st.markdown(
        f"""
<div class="sl-appbar">
  <div class="sl-brand">
    <div class="sl-mark">SL</div>
    <div>
      <div class="sl-brand-title">{APP_NAME}</div>
      <div class="sl-brand-subtitle">Automated Atmospheric Intelligence</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

def hero(title: str, subtitle: str, meta: str) -> None:
    st.markdown(
        f"""
<div class="sl-hero">
  <div class="sl-hero-title">{html.escape(title)}</div>
  <div class="sl-hero-sub">{html.escape(subtitle)}</div>
  <div class="sl-pill">{html.escape(meta)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

def pill_row(*labels: str) -> None:
    pills = "".join([f'<span class="sl-pill">{html.escape(label)}</span>' for label in labels])
    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)

def card(title: str, body: str) -> None:
    st.markdown(
        f"""
<div class="sl-card">
  <h3 style="margin-top:0;">{html.escape(title)}</h3>
  <p style="margin-bottom:0; color: var(--storm-muted); font-size:0.95rem;">{html.escape(body)}</p>
</div>
""",
        unsafe_allow_html=True,
    )

def kpi_strip(items: list[tuple[str, str]]) -> None:
    cells = "".join(
        f"""
<div class="sl-kpi">
  <div class="sl-kpi-value">{html.escape(value)}</div>
  <div class="sl-kpi-label">{html.escape(label)}</div>
</div>
"""
        for value, label in items
    )
    st.markdown(f'<div class="sl-kpi-strip">{cells}</div>', unsafe_allow_html=True)

def workflow_strip(items: list[tuple[str, str]]) -> None:
    cells = "".join(
        f"""
<div class="sl-step">
  <div class="sl-step-index">STEP {index}</div>
  <div class="sl-step-title">{html.escape(title)}</div>
</div>
"""
        for index, (title, _description) in enumerate(items, start=1)
    )
    st.markdown(f'<div class="sl-workflow">{cells}</div>', unsafe_allow_html=True)

def next_step_button(page: str, label: str, key: str) -> None:
    if st.button(label, type="primary", use_container_width=True, key=key):
        st.session_state["stormlens_page"] = page
        st.rerun()
