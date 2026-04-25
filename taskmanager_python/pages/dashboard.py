# pages/dashboard.py
import streamlit as st
from datetime import datetime
from utils.database import get_dashboard_stats
from utils.ui import page_header, section_title, format_due, is_overdue, priority_badge, PRIORITY_COLORS, STATUS_COLORS


def show_dashboard():
    user_id   = st.session_state["user_id"]
    first_name = st.session_state["user_name"].split()[0]
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    page_header(
        f"{greeting}, {first_name} 👋",
        f"Here's your task overview · {datetime.now().strftime('%A, %B %d %Y')}"
    )

    stats = get_dashboard_stats(user_id)

    # ── Stat Cards ──────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Tasks",  stats.get("total",       0) or 0)
    c2.metric("In Progress",  stats.get("in_progress", 0) or 0)
    c3.metric("Pending",      stats.get("pending",     0) or 0)
    c4.metric("Completed",    stats.get("completed",   0) or 0)
    c5.metric("⚠️ Overdue",   stats.get("overdue",     0) or 0)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 1], gap="large")

    # ── Upcoming Tasks ───────────────────────────────────────
    with col_left:
        section_title("📅 Upcoming — Next 7 Days")
        upcoming = stats.get("upcoming", [])

        if not upcoming:
            st.markdown("""
            <div style="background:#fff;border:1px solid #e8e4d9;border-radius:14px;
                        padding:32px;text-align:center;color:#9ca3af;">
                <div style="font-size:32px;margin-bottom:10px;">🎉</div>
                <div style="font-weight:500;color:#374151;">All clear!</div>
                <div style="font-size:13px;margin-top:4px;">No upcoming tasks in the next 7 days.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for t in upcoming:
                overdue = is_overdue(t["due_date"])
                p_color = PRIORITY_COLORS.get(t["priority"], "#8b8fa8")
                due_fmt = format_due(t["due_date"])
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e8e4d9;
                            border-left:3px solid {p_color};
                            border-radius:12px;padding:14px 18px;margin-bottom:10px;
                            box-shadow:0 1px 3px rgba(0,0,0,.04);
                            transition:box-shadow .2s;">
                    <div style="font-weight:500;color:#111827;font-size:14px;margin-bottom:4px;">
                        {t['title']}
                    </div>
                    <div style="font-size:12px;color:{'#e85d4a' if overdue else '#6b7280'};">
                        {'⚠️ Overdue · ' if overdue else '⏰ '}{due_fmt}
                    </div>
                    <div style="margin-top:8px;">
                        <span style="background:{p_color}18;color:{p_color};font-size:10px;
                                     font-weight:600;padding:2px 9px;border-radius:99px;
                                     text-transform:uppercase;letter-spacing:.4px;">
                            {t['priority']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Category Progress ────────────────────────────────────
    with col_right:
        section_title("📊 Progress by Category")
        cat_stats = stats.get("category_stats", [])

        if not cat_stats:
            st.markdown("""
            <div style="background:#fff;border:1px solid #e8e4d9;border-radius:14px;
                        padding:32px;text-align:center;color:#9ca3af;">
                <div style="font-size:32px;margin-bottom:10px;">🏷️</div>
                <div style="font-size:13px;">No categories yet.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#fff;border:1px solid #e8e4d9;border-radius:14px;padding:20px;">', unsafe_allow_html=True)
            for i, c in enumerate(cat_stats):
                total = c["total"] or 0
                done  = c["done"]  or 0
                pct   = int((done / total) * 100) if total > 0 else 0
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(
                        f'<div style="font-size:13px;color:#374151;font-weight:500;margin-bottom:5px;">'
                        f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;'
                        f'background:{c["color"]};margin-right:8px;vertical-align:middle;"></span>'
                        f'{c["name"]}</div>',
                        unsafe_allow_html=True
                    )
                with col_b:
                    st.markdown(
                        f'<div style="font-size:12px;color:#9ca3af;text-align:right;margin-bottom:5px;">'
                        f'{done}/{total} &nbsp;<strong style="color:#374151;">{pct}%</strong></div>',
                        unsafe_allow_html=True
                    )
                st.progress(pct / 100)
                if i < len(cat_stats) - 1:
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Quick Actions ────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:600;
                color:#111827;margin-bottom:14px;">⚡ Quick Actions</div>
    """, unsafe_allow_html=True)
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("➕  New Task", type="primary", use_container_width=True):
            st.session_state["page"] = "tasks"
            st.session_state["task_form_mode"] = "add"
            st.rerun()
    with qa2:
        if st.button("🔄  In Progress Tasks", use_container_width=True):
            st.session_state["page"] = "tasks"
            st.session_state["filter_status"] = "in_progress"
            st.rerun()
    with qa3:
        if st.button("🏷️  Manage Categories", use_container_width=True):
            st.session_state["page"] = "categories"
            st.rerun()
    with qa4:
        if st.button("📋  All Tasks", use_container_width=True):
            st.session_state["page"] = "tasks"
            st.rerun()
