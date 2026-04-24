# pages/dashboard.py
# Dashboard — stats, upcoming tasks, category progress
# ============================================================

import streamlit as st
from datetime import datetime
from utils.database import get_dashboard_stats
from utils.ui import page_header, format_due, is_overdue, priority_badge, PRIORITY_COLORS


def show_dashboard():
    user_id   = st.session_state["user_id"]
    user_name = st.session_state["user_name"].split()[0]

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    page_header(
        f"{greeting}, {user_name} 👋",
        f"Here's your task overview for {datetime.now().strftime('%A, %B %d')}"
    )

    stats = get_dashboard_stats(user_id)

    # ---- Stat Cards ----------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tasks",  stats["total"]       or 0)
    col2.metric("In Progress",  stats["in_progress"] or 0)
    col3.metric("Pending",      stats["pending"]      or 0)
    col4.metric("Completed",    stats["completed"]    or 0)
    col5.metric("⚠️ Overdue",   stats["overdue"]      or 0)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # ---- Upcoming Tasks ------------------------------------
    with col_left:
        st.markdown("#### 📅 Upcoming (Next 7 Days)")
        upcoming = stats.get("upcoming", [])
        if not upcoming:
            st.info("No upcoming tasks. Great job! 🎉")
        else:
            for t in upcoming:
                overdue = is_overdue(t["due_date"])
                color   = PRIORITY_COLORS.get(t["priority"], "#64748b")
                due_fmt = format_due(t["due_date"])
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e2e8f0;border-left:3px solid {color};
                            border-radius:10px;padding:12px 16px;margin-bottom:10px;">
                    <strong style="color:#0f172a;font-size:14px;">{t['title']}</strong><br>
                    <span style="font-size:12px;color:{'#ef4444' if overdue else '#64748b'};">
                        {'⚠️ Overdue — ' if overdue else '⏰ '}{due_fmt}
                    </span>
                    &nbsp;
                    <span style="background:{color}22;color:{color};font-size:10px;font-weight:600;
                                 padding:2px 8px;border-radius:20px;text-transform:uppercase;">
                        {t['priority']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # ---- Category Progress ---------------------------------
    with col_right:
        st.markdown("#### 📊 Progress by Category")
        cat_stats = stats.get("category_stats", [])
        if not cat_stats:
            st.info("No categories yet. Create one in the Categories page.")
        else:
            for c in cat_stats:
                total = c["total"] or 0
                done  = c["done"]  or 0
                pct   = int((done / total) * 100) if total > 0 else 0
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(
                        f'<span style="font-size:13px;color:#334155;">'
                        f'<span style="display:inline-block;width:10px;height:10px;'
                        f'border-radius:50%;background:{c["color"]};margin-right:6px;"></span>'
                        f'{c["name"]}</span>',
                        unsafe_allow_html=True
                    )
                with col_b:
                    st.markdown(
                        f'<span style="font-size:12px;color:#64748b;">{done}/{total} — {pct}%</span>',
                        unsafe_allow_html=True
                    )
                st.progress(pct / 100)

    # ---- Quick Actions -------------------------------------
    st.markdown("---")
    st.markdown("#### ⚡ Quick Actions")
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("➕ New Task", use_container_width=True, type="primary"):
            st.session_state["page"] = "tasks"
            st.session_state["open_add"] = True
            st.rerun()
    with qc2:
        if st.button("🏷️ Manage Categories", use_container_width=True):
            st.session_state["page"] = "categories"
            st.rerun()
    with qc3:
        if st.button("📋 View All Tasks", use_container_width=True):
            st.session_state["page"] = "tasks"
            st.rerun()
