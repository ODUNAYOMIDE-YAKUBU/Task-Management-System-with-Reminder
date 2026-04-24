# pages/tasks.py
# Task management — list, create, edit, delete
# ============================================================

import streamlit as st
from datetime import datetime, timedelta
from utils.database import (
    get_tasks, get_task, create_task, update_task, delete_task,
    get_categories,
)
from utils.ui import (
    page_header, format_due, is_overdue,
    PRIORITY_COLORS, STATUS_COLORS, STATUS_EMOJI, PRIORITY_EMOJI,
)

REMINDER_OPTIONS = {
    "No reminder":    0,
    "1 hour before":  1,
    "3 hours before": 3,
    "6 hours before": 6,
    "12 hours before":12,
    "1 day before":   24,
    "2 days before":  48,
}

STATUS_LIST   = ["pending", "in_progress", "completed", "cancelled"]
PRIORITY_LIST = ["high", "medium", "low"]


def show_tasks():
    user_id = st.session_state["user_id"]
    cats    = get_categories(user_id)
    cat_map = {c["id"]: c for c in cats}

    page_header("My Tasks", "Create, track and manage all your tasks")

    # ---- Top action bar ------------------------------------
    col_btn, col_space = st.columns([1, 4])
    with col_btn:
        if st.button("➕ New Task", type="primary", use_container_width=True):
            st.session_state["task_form_mode"] = "add"
            st.session_state["edit_task_id"]   = None

    # ---- Filters -------------------------------------------
    with st.expander("🔍 Filter & Search", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            search = st.text_input("Search", placeholder="Task title or description…", label_visibility="collapsed")
        with fc2:
            f_status = st.selectbox("Status",   ["All"] + [s.replace("_"," ").title() for s in STATUS_LIST], label_visibility="collapsed")
        with fc3:
            f_prio   = st.selectbox("Priority", ["All"] + [p.title() for p in PRIORITY_LIST], label_visibility="collapsed")
        with fc4:
            cat_names = ["All"] + [c["name"] for c in cats]
            f_cat    = st.selectbox("Category", cat_names, label_visibility="collapsed")

    filters = {
        "search":   search,
        "status":   "" if f_status == "All" else f_status.lower().replace(" ", "_"),
        "priority": "" if f_prio   == "All" else f_prio.lower(),
        "category_id": 0 if f_cat == "All" else next((c["id"] for c in cats if c["name"] == f_cat), 0),
    }

    tasks = get_tasks(user_id, filters)

    # ---- Add / Edit Form -----------------------------------
    mode = st.session_state.get("task_form_mode")
    if mode in ("add", "edit"):
        _task_form(user_id, cats, mode)
        st.markdown("---")

    # ---- Task List -----------------------------------------
    st.markdown(f"**{len(tasks)} task{'s' if len(tasks) != 1 else ''} found**")

    if not tasks:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#64748b;">
            <div style="font-size:40px;margin-bottom:12px;">⬡</div>
            <h3 style="color:#334155;">No tasks found</h3>
            <p>Create your first task to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Table header
    hc = st.columns([3, 1, 1, 2, 1, 1])
    for col, label in zip(hc, ["Title", "Priority", "Status", "Due Date", "Category", "Actions"]):
        col.markdown(f"<small style='color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:600;'>{label}</small>", unsafe_allow_html=True)
    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

    for t in tasks:
        tc = st.columns([3, 1, 1, 2, 1, 1])

        with tc[0]:
            overdue = is_overdue(t["due_date"]) and t["status"] not in ("completed", "cancelled")
            st.markdown(
                f"**{t['title']}**"
                + (f"<br><small style='color:#ef4444;'>⚠️ Overdue</small>" if overdue else ""),
                unsafe_allow_html=True,
            )

        with tc[1]:
            p = t["priority"]
            st.markdown(
                f'<span style="background:{PRIORITY_COLORS[p]}22;color:{PRIORITY_COLORS[p]};'
                f'font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;'
                f'text-transform:uppercase;">{p}</span>',
                unsafe_allow_html=True,
            )

        with tc[2]:
            s = t["status"]
            label = s.replace("_", " ").title()
            st.markdown(
                f'<span style="background:{STATUS_COLORS[s]}22;color:{STATUS_COLORS[s]};'
                f'font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;">{label}</span>',
                unsafe_allow_html=True,
            )

        with tc[3]:
            due = format_due(t["due_date"]) if t["due_date"] else "—"
            st.markdown(f"<small style='color:#64748b;'>{due}</small>", unsafe_allow_html=True)

        with tc[4]:
            cat = cat_map.get(t["category_id"])
            if cat:
                st.markdown(
                    f'<span style="font-size:12px;"><span style="display:inline-block;width:8px;height:8px;'
                    f'border-radius:50%;background:{cat["color"]};margin-right:4px;"></span>'
                    f'{cat["name"]}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<small style='color:#cbd5e1;'>—</small>", unsafe_allow_html=True)

        with tc[5]:
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("✏️", key=f"edit_{t['id']}", help="Edit"):
                    st.session_state["task_form_mode"] = "edit"
                    st.session_state["edit_task_id"]   = t["id"]
                    st.rerun()
            with ac2:
                if st.button("🗑️", key=f"del_{t['id']}", help="Delete"):
                    delete_task(t["id"], user_id)
                    st.success("Task deleted.")
                    st.rerun()

        st.markdown('<hr style="margin:4px 0;border-color:#f1f5f9;">', unsafe_allow_html=True)


def _task_form(user_id: int, cats: list, mode: str):
    """Render the Add / Edit task form inline."""
    edit_id   = st.session_state.get("edit_task_id")
    edit_data = get_task(edit_id, user_id) if (mode == "edit" and edit_id) else {}

    title_label = "✏️ Edit Task" if mode == "edit" else "➕ Create New Task"
    st.markdown(f"#### {title_label}")

    with st.form("task_form", clear_on_submit=(mode == "add")):
        title = st.text_input(
            "Task Title *",
            value=edit_data.get("title", ""),
            placeholder="e.g. Complete research chapter 3",
            max_chars=255,
        )
        description = st.text_area(
            "Description",
            value=edit_data.get("description", "") or "",
            placeholder="Optional — add notes or context…",
            max_chars=1000,
        )

        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox(
                "Priority",
                PRIORITY_LIST,
                index=PRIORITY_LIST.index(edit_data.get("priority", "medium")),
                format_func=lambda x: x.title(),
            )
        with col2:
            cat_options = [None] + [c["id"] for c in cats]
            cat_labels  = ["None"] + [c["name"] for c in cats]
            current_cat = edit_data.get("category_id")
            cat_idx     = cat_options.index(current_cat) if current_cat in cat_options else 0
            cat_sel     = st.selectbox("Category", range(len(cat_options)),
                                       index=cat_idx, format_func=lambda i: cat_labels[i])
            selected_cat_id = cat_options[cat_sel]

        col3, col4 = st.columns(2)
        with col3:
            # Pre-fill due date
            default_due = None
            if edit_data.get("due_date"):
                try:
                    default_due = datetime.fromisoformat(edit_data["due_date"])
                except Exception:
                    pass
            due_date = st.date_input("Due Date", value=default_due.date() if default_due else None)
            due_time = st.time_input("Due Time", value=default_due.time() if default_due else datetime.now().replace(hour=9, minute=0, second=0).time())

        with col4:
            reminder_label = st.selectbox("Send Reminder", list(REMINDER_OPTIONS.keys()))
            reminder_hours = REMINDER_OPTIONS[reminder_label]
            if mode == "edit":
                status = st.selectbox(
                    "Status",
                    STATUS_LIST,
                    index=STATUS_LIST.index(edit_data.get("status", "pending")),
                    format_func=lambda s: s.replace("_", " ").title(),
                )
            else:
                status = "pending"

        col_sub, col_can = st.columns([1, 1])
        with col_sub:
            submitted = st.form_submit_button(
                "Save Changes" if mode == "edit" else "Create Task",
                type="primary", use_container_width=True,
            )
        with col_can:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if cancelled:
            st.session_state["task_form_mode"] = None
            st.rerun()

        if submitted:
            if not title.strip():
                st.error("Task title is required.")
                return

            due_dt_str = None
            if due_date:
                due_dt = datetime.combine(due_date, due_time)
                due_dt_str = due_dt.isoformat()

            data = {
                "category_id":    selected_cat_id,
                "title":          title.strip(),
                "description":    description.strip() or None,
                "priority":       priority,
                "status":         status,
                "due_date":       due_dt_str,
                "reminder_hours": reminder_hours,
            }

            if mode == "add":
                create_task(user_id, data)
                st.success("✅ Task created successfully!")
            else:
                update_task(edit_id, user_id, data)
                st.success("✅ Task updated.")

            st.session_state["task_form_mode"] = None
            st.session_state["edit_task_id"]   = None
            st.rerun()
