# Task Management System with Reminder
### Final Year Project — Python + Streamlit + SQLite

---

## Project Structure

```
taskmanager_python/
├── app.py                        ← Main entry point — run this
├── requirements.txt              ← Python dependencies
│
├── .streamlit/
│   ├── config.toml               ← Theme (indigo/navy)
│   └── secrets.toml              ← SMTP email config (do NOT commit to GitHub)
│
├── utils/
│   ├── database.py               ← SQLite DB: all models + queries
│   ├── email_utils.py            ← Email sender (smtplib)
│   └── ui.py                     ← CSS injection, badges, helpers
│
└── pages/
    ├── auth.py                   ← Login + Register
    ├── dashboard.py              ← Stats, upcoming tasks, category progress
    ├── tasks.py                  ← Task list: create, edit, delete, filter
    ├── categories.py             ← Category management
    └── admin.py                  ← Admin panel (admin role only)
```

---

## Run Locally (No XAMPP, No PHP, No MySQL)

### Step 1 — Install Python
Download from https://www.python.org/downloads/ (version 3.10 or higher)
During install, check **"Add Python to PATH"**

### Step 2 — Open Terminal / Command Prompt
In VS Code: press `Ctrl + `` ` (backtick) to open the integrated terminal

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

Your browser will automatically open to: **http://localhost:8501**

**Default admin login:**
- Email: `admin@taskmanager.com`
- Password: `Admin@1234`

> The database file (`taskmanager.db`) is created automatically on first run.
> No setup required.

---

## Deploy to Streamlit Cloud (Free Global Hosting)

### Step 1 — Push to GitHub
1. Create a free account at https://github.com
2. Create a new repository (e.g. `taskmanager-fyp`)
3. Upload all project files to the repository
   - **Important:** Add `.streamlit/secrets.toml` to `.gitignore` — never upload your passwords

### Step 2 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **New app**
4. Choose your repository → set main file as `app.py`
5. Click **Deploy**

Your app will be live at: `https://your-app-name.streamlit.app`

### Step 3 — Add Email Secrets (for reminders to work)
1. In Streamlit Cloud dashboard, click your app → **Settings → Secrets**
2. Paste this (fill in your Gmail details):
```toml
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your_gmail@gmail.com"
SMTP_PASS = "your_app_password"
MAIL_FROM = "your_gmail@gmail.com"
```
3. Save — the app restarts automatically

---

## Getting a Gmail App Password (for email reminders)

1. Go to your Google Account → Security
2. Enable **2-Step Verification** (required)
3. Search for **App Passwords** → create one for "Mail"
4. Copy the 16-character password → paste it as `SMTP_PASS` in secrets

---

## Technologies Used

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Frontend    | Streamlit (Python web framework)  |
| Backend     | Python 3.10+                      |
| Database    | SQLite (built into Python)        |
| Email       | smtplib (built into Python)       |
| Hosting     | Streamlit Cloud (free)            |
| Passwords   | bcrypt hashing                    |

---

## Key Features
- ✅ User registration & login with bcrypt passwords
- ✅ Task creation with title, description, priority, due date, category
- ✅ Task statuses: Pending → In Progress → Completed / Cancelled
- ✅ Email reminders: 1hr / 3hr / 6hr / 12hr / 1day / 2days before due date
- ✅ Category management with colour picker
- ✅ Dashboard with stats and progress charts
- ✅ Admin panel for user management
- ✅ Responsive Streamlit UI with custom CSS
- ✅ Zero-setup SQLite database (no MySQL, no XAMPP)
- ✅ One-click deploy to Streamlit Cloud
