# app.py
# Task Management System with Reminder
# Main Streamlit entry point
# Run: streamlit run app.py
# ============================================================

import streamlit as st

# ---- Page config (must be first Streamlit call) -----------
st.set_page_config(
    page_title="TaskManager",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Imports ----------------------------------------------
from utils.database  import init_db
from utils.ui        import inject_css
from utils.email_utils import process_pending_reminders

from pages.auth        import show_auth
from pages.dashboard   import show_dashboard
from pages.tasks       import show_tasks
from pages.categories  import show_categories
from pages.admin       import show_admin

# ---- Init DB (runs once per cold start) -------------------
init_db()

# ---- Inject global CSS ------------------------------------
inject_css()

# ---- Process any pending email reminders ------------------
# Runs on every page load — lightweight SQLite query
if st.session_state.get("user_id"):
    process_pending_reminders()

# ===========================================================
# ROUTING
# ===========================================================

def is_logged_in() -> bool:
    return bool(st.session_state.get("user_id"))


def sidebar_nav():
    """Render sidebar navigation and return chosen page."""
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 0 28px;text-align:center;">
            <div style="font-size:32px;">⬡</div>
            <div style="font-size:18px;font-weight:600;color:#fff;margin-top:6px;">TaskManager</div>
            <div style="font-size:12px;color:#64748b;margin-top:2px;">Final Year Project</div>
        </div>
        """, unsafe_allow_html=True)

        user_name = st.session_state.get("user_name", "User")
        user_role = st.session_state.get("user_role", "user")

        st.markdown(f"""
        <div style="background:rgba(255,255,255,.07);border-radius:10px;padding:10px 14px;margin-bottom:20px;">
            <div style="font-size:13px;color:#94a3b8;">Signed in as</div>
            <div style="font-size:14px;font-weight:500;color:#fff;">{user_name}</div>
            <div style="font-size:11px;color:#4f46e5;text-transform:uppercase;letter-spacing:.5px;">{user_role}</div>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            "🏠 Dashboard":   "dashboard",
            "✅ My Tasks":    "tasks",
            "🏷️ Categories":  "categories",
        }
        if user_role == "admin":
            pages["⚙️ Admin Panel"] = "admin"

        current = st.session_state.get("page", "dashboard")

        for label, key in pages.items():
            active_style = "background:rgba(79,70,229,.25);color:#a5b4fc;" if key == current else "color:#94a3b8;"
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                help=label.split(" ", 1)[-1],
            ):
                st.session_state["page"] = key
                st.rerun()

        st.markdown("<br>" * 4, unsafe_allow_html=True)
        st.markdown('<hr style="border-color:rgba(255,255,255,.1);">', unsafe_allow_html=True)

        if st.button("🚪 Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    return st.session_state.get("page", "dashboard")


# ===========================================================
# MAIN RENDER
# ===========================================================

if not is_logged_in():
    show_auth()
else:
    page = sidebar_nav()

    if page == "dashboard":
        show_dashboard()
    elif page == "tasks":
        show_tasks()
    elif page == "categories":
        show_categories()
    elif page == "admin":
        show_admin()
    else:
        show_dashboard()
