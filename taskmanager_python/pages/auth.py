# pages/auth.py
import streamlit as st
from utils.database import get_user_by_email, register_user, verify_password


def show_auth():
    # Full-bleed auth layout
    st.markdown("""
    <style>
    .stApp { background: #111118 !important; }
    .block-container { max-width: 480px !important; padding: 0 !important; margin: 0 auto !important; }
    [data-testid="stSidebar"] { display: none !important; }
    section[data-testid="stSidebarContent"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    # Logo / Brand
    st.markdown("""
    <div style="text-align:center;margin-bottom:36px;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    width:56px;height:56px;background:#4338ca;border-radius:16px;
                    font-size:26px;margin-bottom:16px;box-shadow:0 8px 24px rgba(67,56,202,.4);">
            ⬡
        </div>
        <div style="font-family:'Sora',sans-serif;font-size:28px;font-weight:700;
                    color:#fff;letter-spacing:-.5px;">TaskManager</div>
        <div style="font-size:14px;color:#6b7280;margin-top:6px;">
            Manage tasks · Hit deadlines · Stay reminded
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Auth card
    st.markdown("""
    <div style="background:#1a1924;border:1px solid rgba(255,255,255,.08);
                border-radius:20px;padding:32px;box-shadow:0 24px 64px rgba(0,0,0,.4);">
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        _login_form()
    with tab2:
        _register_form()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:24px;font-size:12px;color:#4b5563;">
        Final Year Project &mdash; Task Management System with Reminder
    </div>
    """, unsafe_allow_html=True)


def _login_form():
    st.markdown("""
    <style>
    [data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-size:18px;font-weight:600;
                    color:#f9fafb;margin-bottom:20px;">Welcome back</div>
        """, unsafe_allow_html=True)
        email    = st.text_input("Email Address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        submitted = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                user = get_user_by_email(email)
                if user and verify_password(password, user["password"]):
                    st.session_state.update({
                        "user_id":   user["id"],
                        "user_name": user["full_name"],
                        "user_role": user["role"],
                        "page":      "dashboard",
                    })
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    st.markdown("""
    <div style="margin-top:16px;padding:12px 14px;background:rgba(67,56,202,.15);
                border:1px solid rgba(67,56,202,.3);border-radius:10px;font-size:12px;color:#a5b4fc;">
        <strong>Default admin:</strong> admin@taskmanager.com &nbsp;/&nbsp; Admin@1234
    </div>
    """, unsafe_allow_html=True)


def _register_form():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=True):
        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-size:18px;font-weight:600;
                    color:#f9fafb;margin-bottom:20px;">Create your account</div>
        """, unsafe_allow_html=True)
        full_name = st.text_input("Full Name", placeholder="Your full name")
        email     = st.text_input("Email Address", placeholder="you@example.com")
        col1, col2 = st.columns(2)
        with col1:
            password  = st.text_input("Password",         type="password", placeholder="Min. 8 chars")
        with col2:
            password2 = st.text_input("Confirm Password", type="password", placeholder="Repeat")
        submitted = st.form_submit_button("Create Account →", type="primary", use_container_width=True)

        if submitted:
            if not all([full_name, email, password, password2]):
                st.error("All fields are required.")
            elif len(full_name.strip()) < 2:
                st.error("Full name must be at least 2 characters.")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != password2:
                st.error("Passwords do not match.")
            else:
                result = register_user(full_name, email, password)
                if result["success"]:
                    st.success("✅ Account created! Switch to Sign In to log in.")
                else:
                    st.error(result["message"])
