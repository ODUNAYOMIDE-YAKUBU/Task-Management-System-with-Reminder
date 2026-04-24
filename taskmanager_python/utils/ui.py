# utils/ui.py
# Shared Streamlit UI helpers — CSS, cards, badges, alerts
# ============================================================

import streamlit as st


PRIORITY_COLORS = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
STATUS_COLORS   = {
    "pending":     "#94a3b8",
    "in_progress": "#0ea5e9",
    "completed":   "#22c55e",
    "cancelled":   "#cbd5e1",
}
PRIORITY_EMOJI  = {"high": "🔴", "medium": "🟡", "low": "🟢"}
STATUS_EMOJI    = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,.06);
    }
    [data-testid="metric-container"] > div:first-child {
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: .5px;
        color: #64748b !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; font-size: 14px; }
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { color: #fff !important; }

    /* Buttons */
    .stButton > button {
        border-radius: 9px !important;
        font-weight: 500 !important;
        font-family: 'DM Sans', sans-serif !important;
        transition: all .15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: #4f46e5 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3730a3 !important;
    }

    /* Forms */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(79,70,229,.1) !important;
    }

    /* Progress bars */
    .stProgress > div > div { background-color: #4f46e5 !important; border-radius: 99px; }

    /* Dividers */
    hr { border-color: #e2e8f0 !important; }

    /* Task card */
    .task-card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,.05);
    }
    .task-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.08); }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .4px;
    }
    .overdue-tag { color: #ef4444; font-size: 12px; font-weight: 500; }
    .page-title { font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 4px; }
    .page-sub   { font-size: 14px; color: #64748b; margin-bottom: 24px; }
    </style>
    """, unsafe_allow_html=True)


def badge_html(text: str, bg: str, fg: str = "#fff") -> str:
    return f'<span class="badge" style="background:{bg}22;color:{bg};">{text}</span>'


def priority_badge(p: str) -> str:
    return badge_html(p.upper(), PRIORITY_COLORS.get(p, "#64748b"))


def status_badge(s: str) -> str:
    label = s.replace("_", " ").title()
    return badge_html(label, STATUS_COLORS.get(s, "#64748b"))


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)


def success_msg(msg: str):
    st.success(f"✅ {msg}")


def error_msg(msg: str):
    st.error(f"❌ {msg}")


def format_due(due_str: str) -> str:
    if not due_str:
        return "—"
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(due_str)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return due_str


def is_overdue(due_str: str) -> bool:
    if not due_str:
        return False
    from datetime import datetime
    try:
        return datetime.fromisoformat(due_str) < datetime.now()
    except Exception:
        return False
