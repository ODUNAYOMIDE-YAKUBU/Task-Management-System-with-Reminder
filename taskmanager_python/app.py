# app.py — TaskManager · Python + Streamlit
# Run: python -m streamlit run app.py
# ============================================================

import streamlit as st

st.set_page_config(
    page_title="TaskManager",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.database    import init_db
from utils.ui          import inject_css
from utils.email_utils import process_pending_reminders
from pages.auth        import show_auth
from pages.dashboard   import show_dashboard
from pages.tasks       import show_tasks
from pages.categories  import show_categories
from pages.admin       import show_admin

# ── Bootstrap ────────────────────────────────────────────────
init_db()
inject_css()

if st.session_state.get("user_id"):
    process_pending_reminders()


# ── Sidebar nav ──────────────────────────────────────────────
def sidebar_nav():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:28px 20px 24px;border-bottom:1px solid rgba(255,255,255,.06);">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:38px;height:38px;background:#4338ca;border-radius:11px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:18px;box-shadow:0 4px 14px rgba(67,56,202,.4);">⬡</div>
                <div>
                    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:700;
                                color:#f9fafb;letter-spacing:-.2px;">TaskManager</div>
                    <div style="font-size:10px;color:#4b5563;text-transform:uppercase;
                                letter-spacing:.8px;margin-top:1px;">Final Year Project</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        name = st.session_state.get("user_name", "User")
        role = st.session_state.get("user_role", "user")
        initial = name[0].upper()
        role_color = "#6366f1" if role == "admin" else "#2db87a"
        st.markdown(f"""
        <div style="padding:16px 20px;border-bottom:1px solid rgba(255,255,255,.05);">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:34px;height:34px;border-radius:10px;background:#1e1d2e;
                            display:flex;align-items:center;justify-content:center;
                            font-family:'Sora',sans-serif;font-size:15px;font-weight:600;
                            color:#a5b4fc;border:1px solid rgba(255,255,255,.08);">{initial}</div>
                <div>
                    <div style="font-size:13px;font-weight:500;color:#e5e7eb;">{name}</div>
                    <div style="font-size:10px;color:{role_color};text-transform:uppercase;
                                letter-spacing:.6px;font-weight:600;margin-top:2px;">{role}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Nav items
        st.markdown('<div style="padding:12px 12px 0;">', unsafe_allow_html=True)

        nav_items = [
            ("🏠", "Dashboard",   "dashboard"),
            ("✅", "My Tasks",    "tasks"),
            ("🏷️", "Categories",  "categories"),
        ]
        if role == "admin":
            nav_items.append(("⚙️", "Admin Panel", "admin"))

        current = st.session_state.get("page", "dashboard")

        for icon, label, key in nav_items:
            is_active = key == current
            active_bg = "rgba(67,56,202,.25)" if is_active else "transparent"
            active_color = "#a5b4fc" if is_active else "#6b7280"

            st.markdown(f"""
            <style>
            div[data-testid="stButton"] button[title="{key}"] {{
                background: {active_bg} !important;
                color: {active_color} !important;
            }}
            </style>
            """, unsafe_allow_html=True)

            if st.button(f"  {icon}  {label}", key=f"nav_{key}",
                         use_container_width=True, help=key):
                st.session_state["page"] = key
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Spacer + sign out
        st.markdown("""
        <div style="height:1px;background:rgba(255,255,255,.05);margin:16px 12px;"></div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div style="padding:0 12px 20px;">', unsafe_allow_html=True)
            if st.button("  🚪  Sign Out", use_container_width=True, key="signout"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    return current


# ── Router ───────────────────────────────────────────────────
if not st.session_state.get("user_id"):
    show_auth()
else:
    page = sidebar_nav()
    if   page == "dashboard":  show_dashboard()
    elif page == "tasks":      show_tasks()
    elif page == "categories": show_categories()
    elif page == "admin":      show_admin()
    else:                      show_dashboard()
