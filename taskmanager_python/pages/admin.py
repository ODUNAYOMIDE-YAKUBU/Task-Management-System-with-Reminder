# pages/admin.py
import streamlit as st
from utils.database import get_all_users, toggle_user_active, delete_user, get_system_totals
from utils.ui import page_header, empty_state


def show_admin():
    if st.session_state.get("user_role") != "admin":
        st.error("🔒 Access denied. This page is for admins only.")
        return

    page_header("Admin Panel", "System overview and user management")

    totals = get_system_totals()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Users",   totals.get("users",     0))
    c2.metric("Total Tasks",   totals.get("tasks",     0))
    c3.metric("Reminders Set", totals.get("reminders", 0))
    c4.metric("Emails Sent",   totals.get("sent",      0))

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:600;
                color:#111827;margin-bottom:14px;">👥 All Users</div>
    """, unsafe_allow_html=True)

    users = get_all_users()
    if not users:
        empty_state("👤", "No users found", "No registered users yet.")
        return

    # Header
    st.markdown("""
    <div style="display:grid;grid-template-columns:2.5fr 3fr 0.8fr 0.8fr 1fr 2fr;gap:12px;
                padding:0 4px 10px;border-bottom:1px solid #e8e4d9;margin-bottom:4px;">
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Name</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Email</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Role</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Tasks</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Status</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Actions</span>
    </div>
    """, unsafe_allow_html=True)

    current_id = st.session_state["user_id"]

    for u in users:
        rc = st.columns([2.5, 3, 0.8, 0.8, 1, 2])

        with rc[0]:
            st.markdown(
                f'<div style="font-weight:500;color:#111827;font-size:14px;padding-top:4px;">{u["full_name"]}</div>',
                unsafe_allow_html=True
            )
        with rc[1]:
            st.markdown(
                f'<div style="font-size:13px;color:#6b7280;padding-top:5px;">{u["email"]}</div>',
                unsafe_allow_html=True
            )
        with rc[2]:
            r_color = "#e85d4a" if u["role"] == "admin" else "#2db87a"
            st.markdown(
                f'<div style="padding-top:4px;"><span style="background:{r_color}18;color:{r_color};'
                f'font-size:10px;font-weight:600;padding:3px 9px;border-radius:99px;text-transform:uppercase;">'
                f'{u["role"]}</span></div>',
                unsafe_allow_html=True
            )
        with rc[3]:
            st.markdown(
                f'<div style="font-size:14px;color:#374151;padding-top:5px;">{u["task_count"] or 0}</div>',
                unsafe_allow_html=True
            )
        with rc[4]:
            active = bool(u["is_active"])
            a_color = "#2db87a" if active else "#9ca3af"
            a_label = "Active" if active else "Inactive"
            st.markdown(
                f'<div style="padding-top:4px;"><span style="background:{a_color}18;color:{a_color};'
                f'font-size:10px;font-weight:600;padding:3px 9px;border-radius:99px;">'
                f'{a_label}</span></div>',
                unsafe_allow_html=True
            )
        with rc[5]:
            if u["id"] == current_id:
                st.markdown('<div style="font-size:12px;color:#9ca3af;padding-top:6px;">← You</div>', unsafe_allow_html=True)
            else:
                ac1, ac2 = st.columns(2)
                with ac1:
                    btn_l = "Deactivate" if u["is_active"] else "Activate"
                    if st.button(btn_l, key=f"tog_{u['id']}", use_container_width=True):
                        toggle_user_active(u["id"])
                        st.rerun()
                with ac2:
                    if st.button("Delete", key=f"delusr_{u['id']}", use_container_width=True):
                        delete_user(u["id"])
                        st.success("User deleted.")
                        st.rerun()

        st.markdown('<hr style="margin:8px 0;border-color:#f3f4f6;">', unsafe_allow_html=True)
