# pages/admin.py
# Admin panel — system overview and user management
# ============================================================

import streamlit as st
from utils.database import get_all_users, toggle_user_active, delete_user, get_system_totals
from utils.ui import page_header


def show_admin():
    if st.session_state.get("user_role") != "admin":
        st.error("Access denied. Admins only.")
        return

    page_header("⚙️ Admin Panel", "System overview and user management")

    # ---- System Stats --------------------------------------
    totals = get_system_totals()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Users",    totals["users"])
    c2.metric("Total Tasks",    totals["tasks"])
    c3.metric("Reminders Set",  totals["reminders"])
    c4.metric("Emails Sent",    totals["sent"])

    st.markdown("---")
    st.markdown("#### 👥 All Users")

    users = get_all_users()
    if not users:
        st.info("No users found.")
        return

    # Header
    hc = st.columns([3, 3, 1, 1, 2, 2])
    for col, label in zip(hc, ["Name", "Email", "Role", "Tasks", "Status", "Actions"]):
        col.markdown(f"<small style='color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:600;'>{label}</small>", unsafe_allow_html=True)
    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

    current_id = st.session_state["user_id"]

    for u in users:
        rc = st.columns([3, 3, 1, 1, 2, 2])

        with rc[0]:
            st.markdown(f"**{u['full_name']}**")
        with rc[1]:
            st.markdown(f"<small style='color:#64748b;'>{u['email']}</small>", unsafe_allow_html=True)
        with rc[2]:
            color = "#ef4444" if u["role"] == "admin" else "#22c55e"
            st.markdown(
                f'<span style="background:{color}22;color:{color};font-size:11px;font-weight:600;'
                f'padding:2px 9px;border-radius:20px;">{u["role"]}</span>',
                unsafe_allow_html=True,
            )
        with rc[3]:
            st.markdown(str(u["task_count"] or 0))
        with rc[4]:
            active = bool(u["is_active"])
            color2 = "#22c55e" if active else "#94a3b8"
            label  = "Active" if active else "Inactive"
            st.markdown(
                f'<span style="background:{color2}22;color:{color2};font-size:11px;font-weight:600;'
                f'padding:2px 9px;border-radius:20px;">{label}</span>',
                unsafe_allow_html=True,
            )
        with rc[5]:
            if u["id"] == current_id:
                st.markdown("<small style='color:#cbd5e1;'>You</small>", unsafe_allow_html=True)
            else:
                ac1, ac2 = st.columns(2)
                with ac1:
                    btn_label = "Deactivate" if u["is_active"] else "Activate"
                    if st.button(btn_label, key=f"tog_{u['id']}", use_container_width=True):
                        toggle_user_active(u["id"])
                        st.rerun()
                with ac2:
                    if st.button("Delete", key=f"delusr_{u['id']}", use_container_width=True):
                        delete_user(u["id"])
                        st.success("User deleted.")
                        st.rerun()

        st.markdown('<hr style="margin:4px 0;border-color:#f1f5f9;">', unsafe_allow_html=True)
