# utils/database.py
# SQLite database — zero setup, file-based, works on Streamlit Cloud
# ============================================================

import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "taskmanager.db"


def get_conn():
    """Return a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist. Called once on app start."""
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'user',
            is_active   INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            color       TEXT    NOT NULL DEFAULT '#4f46e5',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            category_id     INTEGER,
            title           TEXT    NOT NULL,
            description     TEXT,
            priority        TEXT    NOT NULL DEFAULT 'medium',
            status          TEXT    NOT NULL DEFAULT 'pending',
            due_date        TEXT,
            completed_at    TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            remind_at   TEXT    NOT NULL,
            sent        INTEGER NOT NULL DEFAULT 0,
            sent_at     TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # Seed default admin if no users exist
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        hashed = bcrypt.hashpw(b"Admin@1234", bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
            ("System Admin", "admin@taskmanager.com", hashed, "admin"),
        )
        admin_id = cur.lastrowid
        cur.execute(
            "INSERT INTO categories (user_id, name, color) VALUES (?, ?, ?)",
            (admin_id, "General", "#4f46e5"),
        )

    conn.commit()
    conn.close()


# ===========================================================
# USER HELPERS
# ===========================================================

def get_user_by_email(email: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ? AND is_active = 1",
                       (email.lower().strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def register_user(full_name: str, email: str, password: str) -> dict:
    email = email.lower().strip()
    conn = get_conn()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return {"success": False, "message": "Email already registered."}
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
        (full_name.strip(), email, hashed),
    )
    user_id = cur.lastrowid
    cur.execute(
        "INSERT INTO categories (user_id, name, color) VALUES (?, 'General', '#4f46e5')",
        (user_id,),
    )
    conn.commit()
    conn.close()
    return {"success": True}


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def get_all_users():
    conn = get_conn()
    rows = conn.execute("""
        SELECT u.*, COUNT(t.id) AS task_count
        FROM users u
        LEFT JOIN tasks t ON t.user_id = u.id
        GROUP BY u.id ORDER BY u.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_user_active(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET is_active = NOT is_active WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def delete_user(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# ===========================================================
# TASK HELPERS
# ===========================================================

def get_tasks(user_id: int, filters: dict = None) -> list:
    filters = filters or {}
    sql = """
        SELECT t.*, c.name AS category_name, c.color AS category_color
        FROM tasks t
        LEFT JOIN categories c ON c.id = t.category_id
        WHERE t.user_id = ?
    """
    params = [user_id]

    if filters.get("status"):
        sql += " AND t.status = ?"
        params.append(filters["status"])
    if filters.get("priority"):
        sql += " AND t.priority = ?"
        params.append(filters["priority"])
    if filters.get("category_id"):
        sql += " AND t.category_id = ?"
        params.append(filters["category_id"])
    if filters.get("search"):
        sql += " AND (t.title LIKE ? OR t.description LIKE ?)"
        q = f"%{filters['search']}%"
        params += [q, q]

    sql += """
        ORDER BY
            CASE t.status
                WHEN 'in_progress' THEN 1
                WHEN 'pending'     THEN 2
                WHEN 'completed'   THEN 3
                ELSE 4 END,
            CASE t.priority
                WHEN 'high'   THEN 1
                WHEN 'medium' THEN 2
                ELSE 3 END,
            t.due_date ASC
    """
    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task(task_id: int, user_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_task(user_id: int, data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (user_id, category_id, title, description, priority, status, due_date)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (
        user_id,
        data.get("category_id") or None,
        data["title"],
        data.get("description") or None,
        data.get("priority", "medium"),
        data.get("due_date") or None,
    ))
    task_id = cur.lastrowid

    # Auto-schedule reminder
    if data.get("due_date") and data.get("reminder_hours", 0):
        _schedule_reminder(cur, task_id, user_id, data["due_date"], int(data["reminder_hours"]))

    conn.commit()
    conn.close()
    return task_id


def update_task(task_id: int, user_id: int, data: dict) -> bool:
    completed_at = datetime.now().isoformat() if data.get("status") == "completed" else None
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tasks SET
            category_id  = ?,
            title        = ?,
            description  = ?,
            priority     = ?,
            status       = ?,
            due_date     = ?,
            completed_at = ?,
            updated_at   = datetime('now')
        WHERE id = ? AND user_id = ?
    """, (
        data.get("category_id") or None,
        data["title"],
        data.get("description") or None,
        data.get("priority", "medium"),
        data.get("status", "pending"),
        data.get("due_date") or None,
        completed_at,
        task_id, user_id,
    ))

    if data.get("due_date") and data.get("reminder_hours", 0):
        cur.execute("DELETE FROM reminders WHERE task_id = ? AND sent = 0", (task_id,))
        _schedule_reminder(cur, task_id, user_id, data["due_date"], int(data["reminder_hours"]))

    conn.commit()
    conn.close()
    return True


def delete_task(task_id: int, user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()


# ===========================================================
# CATEGORY HELPERS
# ===========================================================

def get_categories(user_id: int) -> list:
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.*, COUNT(t.id) AS task_count
        FROM categories c
        LEFT JOIN tasks t ON t.category_id = c.id AND t.status != 'cancelled'
        WHERE c.user_id = ?
        GROUP BY c.id ORDER BY c.name
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_category(user_id: int, name: str, color: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO categories (user_id, name, color) VALUES (?, ?, ?)",
        (user_id, name, color),
    )
    cat_id = cur.lastrowid
    conn.commit()
    conn.close()
    return cat_id


def delete_category(cat_id: int, user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", (cat_id, user_id))
    conn.commit()
    conn.close()


# ===========================================================
# REMINDER HELPERS
# ===========================================================

def _schedule_reminder(cur, task_id, user_id, due_date_str, hours_before):
    from datetime import timedelta
    try:
        due = datetime.fromisoformat(due_date_str)
        remind_at = due - timedelta(hours=hours_before)
        if remind_at > datetime.now():
            cur.execute(
                "INSERT INTO reminders (task_id, user_id, remind_at) VALUES (?, ?, ?)",
                (task_id, user_id, remind_at.isoformat()),
            )
    except Exception:
        pass


def get_pending_reminders() -> list:
    conn = get_conn()
    rows = conn.execute("""
        SELECT r.id AS reminder_id, r.remind_at,
               t.title, t.description, t.due_date, t.priority, t.status,
               u.full_name, u.email
        FROM reminders r
        JOIN tasks t ON t.id = r.task_id
        JOIN users u ON u.id = r.user_id
        WHERE r.sent = 0
          AND r.remind_at <= datetime('now')
          AND t.status NOT IN ('completed','cancelled')
        ORDER BY r.remind_at ASC
        LIMIT 50
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_reminder_sent(reminder_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE reminders SET sent = 1, sent_at = datetime('now') WHERE id = ?",
        (reminder_id,),
    )
    conn.commit()
    conn.close()


# ===========================================================
# DASHBOARD STATS
# ===========================================================

def get_dashboard_stats(user_id: int) -> dict:
    conn = get_conn()

    totals = conn.execute("""
        SELECT
            COUNT(*)                                                AS total,
            SUM(CASE WHEN status='pending'     THEN 1 ELSE 0 END)  AS pending,
            SUM(CASE WHEN status='in_progress' THEN 1 ELSE 0 END)  AS in_progress,
            SUM(CASE WHEN status='completed'   THEN 1 ELSE 0 END)  AS completed,
            SUM(CASE WHEN status NOT IN ('completed','cancelled')
                      AND due_date < datetime('now') THEN 1 ELSE 0 END) AS overdue
        FROM tasks WHERE user_id = ?
    """, (user_id,)).fetchone()

    upcoming = conn.execute("""
        SELECT * FROM tasks
        WHERE user_id = ?
          AND status NOT IN ('completed','cancelled')
          AND due_date BETWEEN datetime('now') AND datetime('now','+7 days')
        ORDER BY due_date ASC LIMIT 5
    """, (user_id,)).fetchall()

    cat_stats = conn.execute("""
        SELECT c.name, c.color,
               COUNT(t.id) AS total,
               SUM(CASE WHEN t.status='completed' THEN 1 ELSE 0 END) AS done
        FROM categories c
        LEFT JOIN tasks t ON t.category_id = c.id
        WHERE c.user_id = ?
        GROUP BY c.id ORDER BY total DESC LIMIT 6
    """, (user_id,)).fetchall()

    conn.close()
    return {
        **dict(totals),
        "upcoming": [dict(r) for r in upcoming],
        "category_stats": [dict(r) for r in cat_stats],
    }


def get_system_totals() -> dict:
    conn = get_conn()
    row = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM users)                      AS users,
            (SELECT COUNT(*) FROM tasks)                      AS tasks,
            (SELECT COUNT(*) FROM reminders)                  AS reminders,
            (SELECT COUNT(*) FROM reminders WHERE sent=1)     AS sent
    """).fetchone()
    conn.close()
    return dict(row)
