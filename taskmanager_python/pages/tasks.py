# pages/tasks.py
# Task Management — CRUD + Manual Reminder Picker + Browser Push Notifications
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from utils.database import (
    get_tasks, get_task, create_task, update_task, delete_task, get_categories,
)
from utils.ui import (
    page_header, format_due, is_overdue,
    PRIORITY_COLORS, STATUS_COLORS, empty_state,
)

STATUS_LIST   = ["pending", "in_progress", "completed", "cancelled"]
PRIORITY_LIST = ["high", "medium", "low"]


# ════════════════════════════════════════════════════════════
# BROWSER NOTIFICATION PLUGIN
# Injects JS that:
#  1. Shows a branded permission request banner
#  2. Schedules browser push notifications at the exact remind_at time
#  3. Fires a visible toast inside the app on confirmation
# ════════════════════════════════════════════════════════════
NOTIFICATION_PLUGIN = """
<style>
/* ── Permission Banner ── */
#tm-notif-banner {
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 99999;
    background: #1a1924;
    border: 1px solid rgba(99,102,241,.5);
    border-radius: 16px;
    padding: 20px 24px;
    max-width: 360px;
    box-shadow: 0 16px 48px rgba(0,0,0,.5);
    display: flex;
    flex-direction: column;
    gap: 14px;
    animation: tm-slide-in .35s cubic-bezier(.16,1,.3,1);
    font-family: 'DM Sans', sans-serif;
}
@keyframes tm-slide-in {
    from { transform: translateY(32px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}
#tm-notif-banner .tm-nb-icon {
    font-size: 28px; line-height: 1;
}
#tm-notif-banner .tm-nb-title {
    font-weight: 600; font-size: 15px; color: #f9fafb; margin-bottom: 2px;
}
#tm-notif-banner .tm-nb-body {
    font-size: 13px; color: #9ca3af; line-height: 1.5;
}
#tm-notif-banner .tm-nb-btns {
    display: flex; gap: 10px;
}
#tm-nb-allow {
    flex: 1; padding: 10px 0; border: none; border-radius: 9px;
    background: #4338ca; color: #fff; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: background .18s;
    font-family: 'DM Sans', sans-serif;
}
#tm-nb-allow:hover { background: #3730a3; }
#tm-nb-dismiss {
    padding: 10px 16px; border: 1px solid rgba(255,255,255,.12);
    border-radius: 9px; background: transparent; color: #6b7280;
    font-size: 13px; cursor: pointer; font-family: 'DM Sans', sans-serif;
}
#tm-nb-dismiss:hover { background: rgba(255,255,255,.06); color: #9ca3af; }

/* ── Toast ── */
#tm-toast {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 99999;
    background: #1a1924;
    border: 1px solid rgba(99,102,241,.4);
    border-radius: 12px;
    padding: 14px 20px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: #f9fafb;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 8px 24px rgba(0,0,0,.4);
    animation: tm-slide-in .3s ease;
    max-width: 340px;
}
#tm-toast .tm-toast-icon { font-size: 20px; }
#tm-toast .tm-toast-msg  { line-height: 1.4; }
#tm-toast .tm-toast-msg strong { color: #a5b4fc; }
</style>

<script>
(function() {

    var ICON_URL = "https://cdn-icons-png.flaticon.com/512/1946/1946429.png";
    var scheduledReminders = JSON.parse(localStorage.getItem('tm_reminders') || '[]');
    var timeoutIds = [];

    // ── Toast helper ─────────────────────────────────────────
    function showToast(icon, html, durationMs) {
        var existing = document.getElementById('tm-toast');
        if (existing) existing.remove();
        var el = document.createElement('div');
        el.id = 'tm-toast';
        el.innerHTML = '<span class="tm-toast-icon">' + icon + '</span>'
                     + '<span class="tm-toast-msg">' + html + '</span>';
        document.body.appendChild(el);
        setTimeout(function() {
            el.style.transition = 'opacity .4s';
            el.style.opacity = '0';
            setTimeout(function() { el.remove(); }, 400);
        }, durationMs || 4000);
    }

    // ── Restore scheduled reminders from localStorage ────────
    function restoreScheduledReminders() {
        var now = Date.now();
        scheduledReminders = scheduledReminders.filter(function(r) {
            return new Date(r.remindAt).getTime() > now;
        });
        localStorage.setItem('tm_reminders', JSON.stringify(scheduledReminders));

        if (Notification.permission === 'granted') {
            scheduledReminders.forEach(function(r) {
                var delay = new Date(r.remindAt).getTime() - now;
                if (delay > 0 && delay < 2147483647) {
                    var tid = setTimeout(function() {
                        fireNotification(r.title, r.remindAt, r.dueAt);
                    }, delay);
                    timeoutIds.push(tid);
                }
            });
        }
    }

    // ── Fire a browser push notification ─────────────────────
    function fireNotification(taskTitle, remindAt, dueAt) {
        if (Notification.permission !== 'granted') return;
        var dueDate = dueAt ? new Date(dueAt).toLocaleString() : 'soon';
        var n = new Notification('⏰  Task Reminder — TaskManager', {
            body: '📌  ' + taskTitle + '\nDue: ' + dueDate,
            icon: ICON_URL,
            badge: ICON_URL,
            requireInteraction: true,
            tag: 'tm-' + taskTitle.replace(/\s/g, '-').toLowerCase(),
            vibrate: [200, 100, 200]
        });
        n.onclick = function() { window.focus(); n.close(); };
        // Remove from stored list
        scheduledReminders = scheduledReminders.filter(function(r) {
            return r.title !== taskTitle;
        });
        localStorage.setItem('tm_reminders', JSON.stringify(scheduledReminders));
    }

    // ── Schedule a new reminder ───────────────────────────────
    function scheduleReminder(taskTitle, remindAtISO, dueAtISO) {
        var remindTime = new Date(remindAtISO).getTime();
        var now        = Date.now();
        var delay      = remindTime - now;

        // Persist to localStorage so it survives page refresh
        scheduledReminders = scheduledReminders.filter(function(r) {
            return r.title !== taskTitle;
        });
        scheduledReminders.push({ title: taskTitle, remindAt: remindAtISO, dueAt: dueAtISO });
        localStorage.setItem('tm_reminders', JSON.stringify(scheduledReminders));

        if (Notification.permission !== 'granted') {
            showToast('💾', '<strong>Reminder saved.</strong><br>Enable notifications to receive it.', 5000);
            return;
        }
        if (delay <= 0) {
            showToast('⚠️', 'Reminder time is already in the past. Please choose a future time.', 5000);
            return;
        }
        if (delay > 2147483647) {
            showToast('💾', '<strong>Reminder saved</strong> — more than 24 days away, will fire when you next open the app.', 5000);
            return;
        }

        var tid = setTimeout(function() {
            fireNotification(taskTitle, remindAtISO, dueAtISO);
        }, delay);
        timeoutIds.push(tid);

        // Confirmation toast
        var d = new Date(remindAtISO);
        var timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        var dateStr = d.toLocaleDateString([], { month: 'short', day: 'numeric' });
        showToast('🔔', '<strong>Reminder scheduled</strong><br>' + dateStr + ' at ' + timeStr + ' for: ' + taskTitle, 5000);
        console.log('[TaskManager] Reminder set: ' + taskTitle + ' → ' + remindAtISO);
    }

    // ── Show permission banner ────────────────────────────────
    function showPermissionBanner() {
        if (document.getElementById('tm-notif-banner')) return;
        var el = document.createElement('div');
        el.id = 'tm-notif-banner';
        el.innerHTML = [
            '<div>',
              '<div class="tm-nb-icon">🔔</div>',
            '</div>',
            '<div>',
              '<div class="tm-nb-title">Enable Task Reminders</div>',
              '<div class="tm-nb-body">',
                'Allow TaskManager to send you browser notifications so you never miss a deadline — even when this tab is in the background.',
              '</div>',
            '</div>',
            '<div class="tm-nb-btns">',
              '<button id="tm-nb-allow">✓  Allow Notifications</button>',
              '<button id="tm-nb-dismiss">Not now</button>',
            '</div>'
        ].join('');
        document.body.appendChild(el);

        document.getElementById('tm-nb-allow').onclick = function() {
            Notification.requestPermission().then(function(perm) {
                el.remove();
                if (perm === 'granted') {
                    showToast('✅', '<strong>Notifications enabled!</strong><br>You\'ll be alerted before every deadline.', 5000);
                    restoreScheduledReminders();
                    // Fire a test notification
                    setTimeout(function() {
                        new Notification('✅  TaskManager', {
                            body: 'Notifications are active. You\'ll be reminded before your deadlines.',
                            icon: ICON_URL
                        });
                    }, 600);
                } else {
                    showToast('❌', 'Notifications blocked. You can enable them in your browser settings.', 6000);
                }
            });
        };
        document.getElementById('tm-nb-dismiss').onclick = function() {
            el.remove();
            localStorage.setItem('tm_notif_dismissed', '1');
        };
    }

    // ── Initialise ────────────────────────────────────────────
    function init() {
        if (!('Notification' in window)) return;

        if (Notification.permission === 'granted') {
            restoreScheduledReminders();
        } else if (Notification.permission === 'default') {
            var dismissed = localStorage.getItem('tm_notif_dismissed');
            if (!dismissed) {
                setTimeout(showPermissionBanner, 1800);
            }
        }
    }

    // ── Public API ────────────────────────────────────────────
    window.TM = {
        scheduleReminder:    scheduleReminder,
        showPermissionBanner: showPermissionBanner,
        showToast:           showToast,
    };

    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
</script>
"""


def _inject_notification_plugin():
    """Inject the notification plugin once per session."""
    if not st.session_state.get("_notif_plugin_injected"):
        components.html(NOTIFICATION_PLUGIN, height=0, scrolling=False)
        st.session_state["_notif_plugin_injected"] = True


def _schedule_browser_reminder(title: str, remind_at: datetime, due_at: datetime):
    """Call JS to schedule a browser notification for this task."""
    components.html(f"""
    <script>
    (function waitForTM() {{
        if (window.TM && window.TM.scheduleReminder) {{
            window.TM.scheduleReminder(
                {title!r},
                {remind_at.isoformat()!r},
                {due_at.isoformat()!r}
            );
        }} else {{
            setTimeout(waitForTM, 120);
        }}
    }})();
    </script>
    """, height=0, scrolling=False)


def _total_minutes(days: int, hours: int, minutes: int) -> int:
    return int(days * 1440 + hours * 60 + minutes)


def _reminder_preview(days: int, hours: int, minutes: int) -> tuple[str, str]:
    total = _total_minutes(days, hours, minutes)
    if total == 0:
        return "No reminder set", "#9ca3af"
    parts = []
    if days:    parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:   parts.append(f"{hours} hr{'s' if hours != 1 else ''}")
    if minutes: parts.append(f"{minutes} min")
    return f"⏰  Remind me {', '.join(parts)} before due date", "#4338ca"


# ════════════════════════════════════════════════════════════
# MAIN PAGE
# ════════════════════════════════════════════════════════════

def show_tasks():
    user_id = st.session_state["user_id"]
    cats    = get_categories(user_id)
    cat_map = {c["id"]: c for c in cats}

    page_header("My Tasks", "Create, track and manage all your tasks in one place")

    # Inject notification plugin (runs once per session)
    _inject_notification_plugin()

    # ── New Task button ──────────────────────────────────────
    tb1, tb2, _ = st.columns([1, 1.4, 4])
    with tb1:
        if st.button("➕  New Task", type="primary", use_container_width=True):
            st.session_state["task_form_mode"] = "add"
            st.session_state["edit_task_id"]   = None
    with tb2:
        # Manual "re-open" notification banner button
        if st.button("🔔  Notification Settings", use_container_width=True):
            components.html("""
            <script>
            if (window.TM) {
                if (Notification.permission === 'granted') {
                    window.TM.showToast('✅', '<strong>Notifications already enabled</strong><br>You\\'re all set!', 4000);
                } else {
                    window.TM.showPermissionBanner();
                }
            }
            </script>
            """, height=0)

    # ── Task form (add / edit) ───────────────────────────────
    mode = st.session_state.get("task_form_mode")
    if mode in ("add", "edit"):
        _task_form(user_id, cats, mode)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Filters ─────────────────────────────────────────────
    with st.expander("🔍  Filter & Search Tasks", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            search = st.text_input("Search", placeholder="Title or description…", label_visibility="collapsed")
        with fc2:
            pre_status  = st.session_state.pop("filter_status", "")
            status_opts = ["All"] + [s.replace("_", " ").title() for s in STATUS_LIST]
            pre_idx     = status_opts.index(pre_status.replace("_", " ").title()) if pre_status else 0
            f_status    = st.selectbox("Status", status_opts, index=pre_idx, label_visibility="collapsed")
        with fc3:
            f_prio = st.selectbox("Priority", ["All"] + [p.title() for p in PRIORITY_LIST], label_visibility="collapsed")
        with fc4:
            cat_names = ["All"] + [c["name"] for c in cats]
            f_cat     = st.selectbox("Category", cat_names, label_visibility="collapsed")
        _, rc = st.columns([5, 1])
        with rc:
            if st.button("Reset", use_container_width=True):
                st.rerun()

    filters = {
        "search":      search,
        "status":      "" if f_status == "All" else f_status.lower().replace(" ", "_"),
        "priority":    "" if f_prio   == "All" else f_prio.lower(),
        "category_id": 0  if f_cat   == "All" else next((c["id"] for c in cats if c["name"] == f_cat), 0),
    }
    tasks = get_tasks(user_id, filters)

    st.markdown(
        f'<div style="font-size:13px;color:#6b7280;margin-bottom:14px;">'
        f'Showing <strong style="color:#111827;">{len(tasks)}</strong> '
        f'task{"s" if len(tasks) != 1 else ""}</div>',
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
        icons   = {"high": "↑", "medium": "→", "low": "↓"}

        rc = st.columns([3, 1, 1, 2, 1.2, 0.8])

        with rc[0]:
            overdue_tag = (' <span style="font-size:11px;color:#e85d4a;font-weight:500;">⚠️ Overdue</span>'
                           if overdue else "")
            desc      = t.get("description") or ""
            desc_snip = (desc[:55] + "…") if len(desc) > 55 else desc
            st.markdown(
                f'<div style="padding:2px 0;">'
                f'<div style="font-weight:500;color:#111827;font-size:14px;">{t["title"]}{overdue_tag}</div>'
                + (f'<div style="font-size:12px;color:#9ca3af;margin-top:2px;">{desc_snip}</div>' if desc_snip else "")
                + '</div>',
                unsafe_allow_html=True,
            )

        with rc[1]:
            st.markdown(
                f'<div style="padding-top:2px;">'
                f'<span style="background:{p_color}18;color:{p_color};font-size:11px;font-weight:600;'
                f'padding:3px 10px;border-radius:99px;text-transform:uppercase;letter-spacing:.4px;">'
                f'{icons.get(p,"")} {p}</span></div>',
                unsafe_allow_html=True,
            )

        with rc[2]:
            st.markdown(
                f'<div style="padding-top:2px;">'
                f'<span style="background:{s_color}18;color:{s_color};font-size:11px;font-weight:600;'
                f'padding:3px 10px;border-radius:99px;">{s.replace("_"," ")}</span></div>',
                unsafe_allow_html=True,
            )

        with rc[3]:
            due_color = "#e85d4a" if overdue else "#6b7280"
            st.markdown(
                f'<div style="font-size:13px;color:{due_color};padding-top:4px;">{due_str}</div>',
                unsafe_allow_html=True,
            )

        with rc[4]:
            if cat:
                st.markdown(
                    f'<div style="font-size:13px;color:#374151;padding-top:4px;">'
                    f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
                    f'background:{cat["color"]};margin-right:6px;vertical-align:middle;"></span>'
                    f'{cat["name"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div style="color:#d1d5db;padding-top:4px;">—</div>', unsafe_allow_html=True)

        with rc[5]:
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("✏️", key=f"edit_{t['id']}", help="Edit task"):
                    st.session_state["task_form_mode"] = "edit"
                    st.session_state["edit_task_id"]   = t["id"]
                    st.rerun()
            with ac2:
                if st.button("🗑️", key=f"del_{t['id']}", help="Delete task"):
                    delete_task(t["id"], user_id)
                    st.success("Task deleted.")
                    st.rerun()

        st.markdown('<hr style="margin:8px 0;border-color:#f3f4f6;">', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TASK FORM — Add / Edit
# ════════════════════════════════════════════════════════════

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

        # ── Title & Description ──────────────────────────────
        title = st.text_input(
            "Task Title *",
            value=edit_data.get("title", ""),
            placeholder="e.g. Complete research chapter 3",
            max_chars=255,
        )
        description = st.text_area(
            "Description (optional)",
            value=edit_data.get("description", "") or "",
            placeholder="Add notes, references, or context…",
            max_chars=1000,
        )

        # ── Priority / Category / Status ─────────────────────
        col1, col2, col3 = st.columns(3)
        with col1:
            priority = st.selectbox(
                "Priority", PRIORITY_LIST,
                index=PRIORITY_LIST.index(edit_data.get("priority", "medium")),
                format_func=str.title,
            )
        with col2:
            cat_opts   = [None] + [c["id"] for c in cats]
            cat_labels = ["None"] + [c["name"] for c in cats]
            cur_cat    = edit_data.get("category_id")
            cat_idx    = cat_opts.index(cur_cat) if cur_cat in cat_opts else 0
            cat_sel    = st.selectbox("Category", range(len(cat_opts)),
                                      index=cat_idx, format_func=lambda i: cat_labels[i])
            selected_cat = cat_opts[cat_sel]
        with col3:
            if mode == "edit":
                status = st.selectbox(
                    "Status", STATUS_LIST,
                    index=STATUS_LIST.index(edit_data.get("status", "pending")),
                    format_func=lambda s: s.replace("_", " ").title(),
                )
            else:
                status = "pending"
                st.selectbox("Status", ["Pending"], disabled=True)

        # ── Due Date & Time ──────────────────────────────────
        st.markdown("""
        <div style="font-size:13px;font-weight:600;color:#374151;
                    margin:16px 0 6px;">📅  Due Date & Time</div>
        """, unsafe_allow_html=True)

        default_due = None
        if edit_data.get("due_date"):
            try: default_due = datetime.fromisoformat(edit_data["due_date"])
            except: pass

        dc1, dc2 = st.columns(2)
        with dc1:
            due_date = st.date_input("Due Date", value=default_due.date() if default_due else None)
        with dc2:
            due_time = st.time_input(
                "Due Time",
                value=default_due.time() if default_due
                      else datetime.now().replace(hour=9, minute=0, second=0).time(),
            )

        # ════════════════════════════════════════════════════
        # MANUAL REMINDER PICKER
        # ════════════════════════════════════════════════════
        st.markdown("""
        <div style="background:#f5f4f0;border:1.5px solid #e8e4d9;border-radius:14px;
                    padding:18px 20px;margin:18px 0 8px;">
            <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:3px;">
                🔔  Set Reminder
            </div>
            <div style="font-size:12px;color:#9ca3af;margin-bottom:14px;">
                Enter any combination of days, hours, and minutes before the due date.
                Leave all at 0 for no reminder.
            </div>
        """, unsafe_allow_html=True)

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            remind_days = st.number_input(
                "Days before",
                min_value=0, max_value=365, value=0, step=1,
                help="e.g. 2 = remind me 2 days before the deadline",
            )
        with mc2:
            remind_hours = st.number_input(
                "Hours before",
                min_value=0, max_value=23, value=0, step=1,
                help="e.g. 3 = remind me 3 hours before (stacks with days)",
            )
        with mc3:
            remind_mins = st.number_input(
                "Minutes before",
                min_value=0, max_value=59, value=0, step=5,
                help="e.g. 30 = remind me 30 minutes before (stacks with days + hours)",
            )

        # Live preview
        total_mins = _total_minutes(int(remind_days), int(remind_hours), int(remind_mins))
        preview_text, preview_color = _reminder_preview(
            int(remind_days), int(remind_hours), int(remind_mins)
        )

        # Show computed reminder time if due_date is filled
        reminder_time_preview = ""
        if due_date and total_mins > 0:
            due_dt_preview = datetime.combine(due_date, due_time)
            remind_at_preview = due_dt_preview - timedelta(minutes=total_mins)
            reminder_time_preview = (
                f" &nbsp;·&nbsp; fires at "
                f"<strong>{remind_at_preview.strftime('%b %d, %Y %I:%M %p')}</strong>"
            )

        st.markdown(f"""
        <div style="margin-top:6px;padding:11px 16px;background:#fff;
                    border:1.5px solid {'#e0e7ff' if total_mins > 0 else '#e8e4d9'};
                    border-radius:10px;font-size:13px;font-weight:500;color:{preview_color};
                    transition:border-color .2s;">
            {preview_text}{reminder_time_preview}
        </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Submit / Cancel ──────────────────────────────────
        col_s, col_c = st.columns(2)
        with col_s:
            submitted = st.form_submit_button(
                "Save Changes" if mode == "edit" else "Create Task",
                type="primary", use_container_width=True,
            )
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
            due_dt_obj = None
            if due_date:
                due_dt_obj = datetime.combine(due_date, due_time)
                due_dt_str = due_dt_obj.isoformat()

            # Convert to fractional hours for DB _schedule_reminder
            reminder_fractional_hours = int(remind_days) * 24 + int(remind_hours) + int(remind_mins) / 60

            data = {
                "category_id":    selected_cat,
                "title":          title.strip(),
                "description":    description.strip() or None,
                "priority":       priority,
                "status":         status,
                "due_date":       due_dt_str,
                "reminder_hours": reminder_fractional_hours,
            }

            if mode == "add":
                create_task(user_id, data)
                st.success("✅ Task created successfully!")
            else:
                update_task(edit_id, user_id, data)
                st.success("✅ Task updated.")

            # Schedule browser notification if reminder is set
            if due_dt_obj and total_mins > 0:
                remind_at_obj = due_dt_obj - timedelta(minutes=total_mins)
                _schedule_browser_reminder(title.strip(), remind_at_obj, due_dt_obj)

            st.session_state["task_form_mode"] = None
            st.session_state["edit_task_id"]   = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
