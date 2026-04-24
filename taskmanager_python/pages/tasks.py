# pages/tasks.py
import streamlit as st
from datetime import datetime
from utils.database import (
    get_tasks, get_task, create_task, update_task, delete_task, get_categories,
)
from utils.ui import (
    page_header, section_title, format_due, is_overdue,
    priority_badge, status_badge, PRIORITY_COLORS, STATUS_COLORS, row_divider, empty_state,
)

REMINDER_OPTIONS = {
    "No reminder": 0, "1 hour before": 1, "3 hours before": 3,
    "6 hours before": 6, "12 hours before": 12, "1 day before": 24, "2 days before": 48,
}
STATUS_LIST   = ["pending", "in_progress", "completed", "cancelled"]
PRIORITY_LIST = ["high", "medium", "low"]


def show_tasks():
    user_id = st.session_state["user_id"]
    cats    = get_categories(user_id)
    cat_map = {c["id"]: c for c in cats}

    page_header("My Tasks", "Create, track and manage all your tasks in one place")

    # ── Top bar ──────────────────────────────────────────────
    tb1, tb2 = st.columns([1, 4])
    with tb1:
        if st.button("➕  New Task", type="primary", use_container_width=True):
            st.session_state["task_form_mode"] = "add"
            st.session_state["edit_task_id"] = None

    # ── Inline form ──────────────────────────────────────────
    mode = st.session_state.get("task_form_mode")
    if mode in ("add", "edit"):
        _task_form(user_id, cats, mode)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────
    with st.expander("🔍  Filter & Search Tasks", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            search = st.text_input("Search", placeholder="Title or description…", label_visibility="collapsed")
        with fc2:
            pre_status = st.session_state.pop("filter_status", "")
            status_opts = ["All"] + [s.replace("_", " ").title() for s in STATUS_LIST]
            pre_idx = status_opts.index(pre_status.replace("_", " ").title()) if pre_status else 0
            f_status = st.selectbox("Status", status_opts, index=pre_idx, label_visibility="collapsed")
        with fc3:
            f_prio = st.selectbox("Priority", ["All"] + [p.title() for p in PRIORITY_LIST], label_visibility="collapsed")
        with fc4:
            cat_names = ["All"] + [c["name"] for c in cats]
            f_cat = st.selectbox("Category", cat_names, label_visibility="collapsed")
        fc5, fc6 = st.columns([1, 4])
        with fc5:
            if st.button("Reset Filters", use_container_width=True):
                st.rerun()

    filters = {
        "search":      search,
        "status":      "" if f_status == "All" else f_status.lower().replace(" ", "_"),
        "priority":    "" if f_prio   == "All" else f_prio.lower(),
        "category_id": 0  if f_cat   == "All" else next((c["id"] for c in cats if c["name"] == f_cat), 0),
    }
    tasks = get_tasks(user_id, filters)

    # ── Task count summary ───────────────────────────────────
    st.markdown(
        f'<div style="font-size:13px;color:#6b7280;margin-bottom:14px;">'
        f'Showing <strong style="color:#111827;">{len(tasks)}</strong> task{"s" if len(tasks)!=1 else ""}</div>',
        unsafe_allow_html=True
    )

    if not tasks:
        empty_state("📭", "No tasks found", "Create a new task or adjust your filters.")
        return

    # ── Table header ─────────────────────────────────────────
    st.markdown("""
    <div style="display:grid;grid-template-columns:3fr 1fr 1fr 2fr 1.2fr 0.8fr;
                gap:12px;padding:0 4px 10px;border-bottom:1px solid #e8e4d9;margin-bottom:4px;">
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Task</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Priority</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Status</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Due Date</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Category</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Actions</span>
    </div>
    """, unsafe_allow_html=True)

    for t in tasks:
        overdue = is_overdue(t["due_date"]) and t["status"] not in ("completed", "cancelled")
        p       = t["priority"]
        s       = t["status"]
        p_color = PRIORITY_COLORS.get(p, "#8b8fa8")
        s_color = STATUS_COLORS.get(s,   "#8b8fa8")
        cat     = cat_map.get(t["category_id"])
        due_str = format_due(t["due_date"]) if t["due_date"] else "—"

        # Row card
        rc = st.columns([3, 1, 1, 2, 1.2, 0.8])

        with rc[0]:
            overdue_tag = ' <span style="font-size:11px;color:#e85d4a;font-weight:500;">⚠️ Overdue</span>' if overdue else ""
            desc = t.get("description") or ""
            desc_snip = (desc[:55] + "…") if len(desc) > 55 else desc
            st.markdown(
                f'<div style="padding:2px 0;">'
                f'<div style="font-weight:500;color:#111827;font-size:14px;">{t["title"]}{overdue_tag}</div>'
                + (f'<div style="font-size:12px;color:#9ca3af;margin-top:2px;">{desc_snip}</div>' if desc_snip else "")
                + '</div>',
                unsafe_allow_html=True
            )

        with rc[1]:
            icons = {"high": "↑", "medium": "→", "low": "↓"}
            st.markdown(
                f'<div style="padding-top:2px;">'
                f'<span style="background:{p_color}18;color:{p_color};font-size:11px;font-weight:600;'
                f'padding:3px 10px;border-radius:99px;text-transform:uppercase;letter-spacing:.4px;">'
                f'{icons.get(p,"")} {p}</span></div>',
                unsafe_allow_html=True
            )

        with rc[2]:
            st.markdown(
                f'<div style="padding-top:2px;">'
                f'<span style="background:{s_color}18;color:{s_color};font-size:11px;font-weight:600;'
                f'padding:3px 10px;border-radius:99px;">'
                f'{s.replace("_"," ")}</span></div>',
                unsafe_allow_html=True
            )

        with rc[3]:
            due_color = "#e85d4a" if overdue else "#6b7280"
            st.markdown(
                f'<div style="font-size:13px;color:{due_color};padding-top:4px;">{due_str}</div>',
                unsafe_allow_html=True
            )

        with rc[4]:
            if cat:
                st.markdown(
                    f'<div style="font-size:13px;color:#374151;padding-top:4px;">'
                    f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
                    f'background:{cat["color"]};margin-right:6px;vertical-align:middle;"></span>'
                    f'{cat["name"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div style="color:#d1d5db;padding-top:4px;">—</div>', unsafe_allow_html=True)

        with rc[5]:
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("✏️", key=f"edit_{t['id']}", help="Edit this task"):
                    st.session_state["task_form_mode"] = "edit"
                    st.session_state["edit_task_id"]   = t["id"]
                    st.rerun()
            with ac2:
                if st.button("🗑️", key=f"del_{t['id']}", help="Delete this task"):
                    delete_task(t["id"], user_id)
                    st.success("Task deleted.")
                    st.rerun()

        st.markdown('<hr style="margin:8px 0;border-color:#f3f4f6;">', unsafe_allow_html=True)


def _task_form(user_id: int, cats: list, mode: str):
    edit_id   = st.session_state.get("edit_task_id")
    edit_data = get_task(edit_id, user_id) if (mode == "edit" and edit_id) else {}
    label     = "✏️  Edit Task" if mode == "edit" else "➕  Create New Task"

    st.markdown(f"""
    <div style="background:#fff;border:1px solid #e8e4d9;border-radius:16px;
                padding:24px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.05);">
    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:600;
                color:#111827;margin-bottom:20px;">{label}</div>
    """, unsafe_allow_html=True)

    with st.form("task_form", clear_on_submit=(mode == "add")):
        title = st.text_input("Task Title *", value=edit_data.get("title", ""),
                              placeholder="e.g. Complete research chapter 3", max_chars=255)
        description = st.text_area("Description (optional)", value=edit_data.get("description", "") or "",
                                   placeholder="Add notes, references, or context…", max_chars=1000)

        col1, col2, col3 = st.columns(3)
        with col1:
            priority = st.selectbox("Priority", PRIORITY_LIST,
                                    index=PRIORITY_LIST.index(edit_data.get("priority", "medium")),
                                    format_func=str.title)
        with col2:
            cat_opts   = [None] + [c["id"] for c in cats]
            cat_labels = ["None"] + [c["name"] for c in cats]
            cur_cat    = edit_data.get("category_id")
            cat_idx    = cat_opts.index(cur_cat) if cur_cat in cat_opts else 0
            cat_sel    = st.selectbox("Category", range(len(cat_opts)),
                                      index=cat_idx, format_func=lambda i: cat_labels[i])
            selected_cat = cat_opts[cat_sel]
        with col3:
            reminder_label = st.selectbox("Reminder", list(REMINDER_OPTIONS.keys()))
            reminder_hours = REMINDER_OPTIONS[reminder_label]

        col4, col5 = st.columns(2)
        default_due = None
        if edit_data.get("due_date"):
            try: default_due = datetime.fromisoformat(edit_data["due_date"])
            except: pass

        with col4:
            due_date = st.date_input("Due Date", value=default_due.date() if default_due else None)
        with col5:
            due_time = st.time_input("Due Time",
                                     value=default_due.time() if default_due
                                     else datetime.now().replace(hour=9, minute=0, second=0).time())

        if mode == "edit":
            status = st.selectbox("Status", STATUS_LIST,
                                  index=STATUS_LIST.index(edit_data.get("status", "pending")),
                                  format_func=lambda s: s.replace("_", " ").title())
        else:
            status = "pending"

        col_s, col_c = st.columns(2)
        with col_s:
            submitted = st.form_submit_button(
                "Save Changes" if mode == "edit" else "Create Task",
                type="primary", use_container_width=True)
        with col_c:
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
                due_dt_str = datetime.combine(due_date, due_time).isoformat()

            data = {
                "category_id": selected_cat, "title": title.strip(),
                "description": description.strip() or None, "priority": priority,
                "status": status, "due_date": due_dt_str, "reminder_hours": reminder_hours,
            }
            if mode == "add":
                create_task(user_id, data)
                st.success("✅ Task created!")
            else:
                update_task(edit_id, user_id, data)
                st.success("✅ Task updated.")

            st.session_state["task_form_mode"] = None
            st.session_state["edit_task_id"]   = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
