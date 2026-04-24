# utils/email_utils.py
# Email reminder sender using smtplib (built into Python — no extra install)
# ============================================================

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import streamlit as st


def _get_smtp_config():
    """Read SMTP config from Streamlit secrets (for cloud) or st.session_state."""
    try:
        return {
            "host":     st.secrets["SMTP_HOST"],
            "port":     int(st.secrets["SMTP_PORT"]),
            "user":     st.secrets["SMTP_USER"],
            "password": st.secrets["SMTP_PASS"],
            "from":     st.secrets.get("MAIL_FROM", st.secrets["SMTP_USER"]),
        }
    except Exception:
        return None


def build_email_html(name: str, title: str, due: str, priority: str, desc: str) -> str:
    prio_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
    color = prio_colors.get(priority.lower(), "#4f46e5")
    desc_html = f'<p style="color:#64748b;font-size:14px;margin:8px 0 0;">{desc}</p>' if desc else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:40px 20px;">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
      <tr><td style="background:#1e293b;padding:28px 32px;">
        <h1 style="color:#fff;margin:0;font-size:20px;">&#9200; TaskManager Reminder</h1>
      </td></tr>
      <tr><td style="padding:32px;">
        <p style="color:#334155;font-size:16px;margin:0 0 8px;">Hi <strong>{name}</strong>,</p>
        <p style="color:#64748b;font-size:14px;margin:0 0 24px;">You have an upcoming task that needs your attention:</p>
        <div style="background:#f8fafc;border-left:4px solid {color};border-radius:6px;padding:20px 24px;">
          <h2 style="color:#1e293b;font-size:18px;margin:0 0 8px;">{title}</h2>
          {desc_html}
          <p style="margin:16px 0 4px;font-size:13px;color:#94a3b8;">DUE DATE</p>
          <p style="margin:0;font-size:15px;color:#1e293b;font-weight:600;">{due}</p>
          <p style="margin:12px 0 0;">
            <span style="background:{color}22;color:{color};font-size:12px;font-weight:600;
                         padding:3px 10px;border-radius:20px;text-transform:uppercase;">
              {priority} Priority
            </span>
          </p>
        </div>
      </td></tr>
      <tr><td style="background:#f8fafc;padding:20px 32px;border-top:1px solid #e2e8f0;">
        <p style="color:#94a3b8;font-size:12px;margin:0;">
          You're receiving this because you set a reminder in TaskManager. &copy; 2025 TaskManager.
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


def send_reminder_email(to_email: str, to_name: str, task: dict) -> bool:
    cfg = _get_smtp_config()
    if not cfg:
        # No SMTP configured — silently skip (log only)
        print(f"[REMINDER] No SMTP config. Would have emailed {to_email} for task: {task['title']}")
        return False

    try:
        due_str = ""
        if task.get("due_date"):
            due_str = datetime.fromisoformat(task["due_date"]).strftime("%A, %B %d %Y at %I:%M %p")

        html = build_email_html(
            to_name,
            task["title"],
            due_str,
            task.get("priority", "medium"),
            task.get("description", ""),
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[TaskManager] Reminder: {task['title']}"
        msg["From"]    = f"TaskManager <{cfg['from']}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from"], to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def process_pending_reminders():
    """Call this on each app load to dispatch any overdue reminders."""
    from utils.database import get_pending_reminders, mark_reminder_sent
    reminders = get_pending_reminders()
    for r in reminders:
        ok = send_reminder_email(r["email"], r["full_name"], {
            "title":       r["title"],
            "description": r["description"],
            "due_date":    r["due_date"],
            "priority":    r["priority"],
        })
        if ok:
            mark_reminder_sent(r["reminder_id"])
