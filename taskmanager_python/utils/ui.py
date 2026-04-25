# utils/ui.py
# Enhanced UI — clean editorial design, sharp typography, pro-grade aesthetics
# Font: Sora (display) + DM Sans (body) — geometric, modern, academic-appropriate
# Theme: Warm off-white canvas, deep charcoal navy, electric indigo accents
# ============================================================

import streamlit as st

PRIORITY_COLORS = {"high": "#e85d4a", "medium": "#f0a500", "low": "#2db87a"}
STATUS_COLORS   = {
    "pending":     "#8b8fa8",
    "in_progress": "#4f8ef7",
    "completed":   "#2db87a",
    "cancelled":   "#c9cdd6",
}

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'DM Sans', sans-serif !important;
        background: #f5f4f0 !important;
    }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1180px !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #111118 !important;
        border-right: 1px solid rgba(255,255,255,.05) !important;
    }
    [data-testid="stSidebar"] > div { padding: 0 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        border-radius: 10px !important;
        color: #6b7280 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 11px 16px !important;
        width: 100% !important;
        transition: all .18s !important;
        margin-bottom: 2px !important;
        justify-content: flex-start !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,.07) !important;
        color: #e5e7eb !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        transition: all .18s ease !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
    }
    .stButton > button[kind="primary"] {
        background: #4338ca !important;
        color: #fff !important;
        box-shadow: 0 2px 8px rgba(67,56,202,.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3730a3 !important;
        box-shadow: 0 4px 16px rgba(67,56,202,.4) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind]) {
        background: #fff !important;
        color: #374151 !important;
        border-color: #e5e7eb !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind]):hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: #fff !important;
        border: 1px solid #e8e4d9 !important;
        border-radius: 14px !important;
        padding: 20px 22px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,.04) !important;
        transition: box-shadow .2s, transform .2s !important;
    }
    [data-testid="metric-container"]:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,.08) !important;
        transform: translateY(-2px) !important;
    }
    [data-testid="metric-container"] label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: .8px !important;
        color: #9ca3af !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Sora', sans-serif !important;
        font-size: 34px !important;
        font-weight: 700 !important;
        color: #111827 !important;
        line-height: 1.1 !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #fff !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
        color: #111827 !important;
        padding: 10px 14px !important;
        transition: border-color .18s, box-shadow .18s !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4338ca !important;
        box-shadow: 0 0 0 3px rgba(67,56,202,.1) !important;
    }
    .stTextInput label, .stTextArea label,
    .stSelectbox label, .stDateInput label, .stTimeInput label {
        font-size: 13px !important; font-weight: 500 !important; color: #374151 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #e8e4d9 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 2px !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        color: #6b7280 !important;
        padding: 9px 24px !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #fff !important;
        color: #111827 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,.1) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #fff !important;
        border: 1px solid #e8e4d9 !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        color: #374151 !important;
        padding: 14px 18px !important;
    }
    .streamlit-expanderContent {
        background: #fff !important;
        border: 1px solid #e8e4d9 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 20px !important;
    }

    /* ── Forms ── */
    [data-testid="stForm"] {
        background: #fff !important;
        border: 1px solid #e8e4d9 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,.04) !important;
    }

    /* ── Progress ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #4338ca, #6366f1) !important;
        border-radius: 99px !important;
    }
    .stProgress > div > div {
        background: #e8e4d9 !important;
        border-radius: 99px !important;
        height: 7px !important;
    }

    /* ── Alerts ── */
    .stSuccess { background: #f0fdf4 !important; border-left: 3px solid #2db87a !important; border-radius: 10px !important; }
    .stError   { background: #fef2f2 !important; border-left: 3px solid #e85d4a !important; border-radius: 10px !important; }
    .stInfo    { background: #eff6ff !important; border-left: 3px solid #4f8ef7 !important; border-radius: 10px !important; }

    hr { border-color: #e8e4d9 !important; margin: 20px 0 !important; }

    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 99px; }
    </style>
    """, unsafe_allow_html=True)


def badge(text: str, color: str) -> str:
    return (f'<span style="display:inline-flex;align-items:center;padding:3px 11px;'
            f'border-radius:99px;font-size:11px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:.5px;background:{color}18;color:{color};'
            f'font-family:\'DM Sans\',sans-serif;">{text}</span>')

def priority_badge(p: str) -> str:
    icons = {"high": "↑", "medium": "→", "low": "↓"}
    return badge(f'{icons.get(p,"")} {p}', PRIORITY_COLORS.get(p, "#8b8fa8"))

def status_badge(s: str) -> str:
    return badge(s.replace("_", " "), STATUS_COLORS.get(s, "#8b8fa8"))

def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<div style="font-family:\'Sora\',sans-serif;font-size:26px;font-weight:700;'
        f'color:#111827;margin-bottom:4px;line-height:1.2;">{title}</div>',
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(
            f'<div style="font-size:14px;color:#6b7280;margin-bottom:28px;">{subtitle}</div>',
            unsafe_allow_html=True
        )

def section_title(title: str):
    st.markdown(
        f'<div style="font-family:\'Sora\',sans-serif;font-size:16px;font-weight:600;'
        f'color:#111827;margin-bottom:14px;">{title}</div>',
        unsafe_allow_html=True
    )

def col_header(*labels):
    cols = st.columns([3,1,1,2,1,1]) if len(labels) == 6 else st.columns(len(labels))
    for col, label in zip(cols, labels):
        col.markdown(
            f'<div style="font-size:11px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:.7px;color:#9ca3af;padding-bottom:8px;">{label}</div>',
            unsafe_allow_html=True
        )
    st.markdown('<hr style="margin:0 0 8px;border-color:#e8e4d9;">', unsafe_allow_html=True)
    return cols

def row_divider():
    st.markdown('<hr style="margin:6px 0;border-color:#f3f4f6;">', unsafe_allow_html=True)

def empty_state(icon: str, title: str, desc: str):
    st.markdown(f"""
    <div style="text-align:center;padding:64px 24px;color:#9ca3af;">
        <div style="font-size:44px;margin-bottom:14px;">{icon}</div>
        <div style="font-family:'Sora',sans-serif;font-size:18px;font-weight:600;
                    color:#374151;margin-bottom:8px;">{title}</div>
        <div style="font-size:14px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

def format_due(due_str: str) -> str:
    if not due_str: return "—"
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(due_str)
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except: return due_str

def format_due_short(due_str: str) -> str:
    if not due_str: return "—"
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(due_str)
        return dt.strftime("%b %d")
    except: return due_str

def is_overdue(due_str: str) -> bool:
    if not due_str: return False
    from datetime import datetime
    try: return datetime.fromisoformat(due_str) < datetime.now()
    except: return False
