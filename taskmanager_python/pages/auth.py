# pages/auth.py
# Login and Registration — rendered when user is not logged in
# ============================================================

import streamlit as st
from utils.database import get_user_by_email, register_user, verify_password


def show_auth():
    """Entry point — shows login or register tab."""
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:32px 0 20px;">
            <div style="font-size:36px;">⬡</div>
            <h1 style="font-size:26px;font-weight:600;color:#0f172a;margin:8px 0 4px;">TaskManager</h1>
            <p style="color:#64748b;font-size:14px;">Manage tasks. Hit deadlines. Stay reminded.</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            _login_form()

        with tab_register:
            _register_form()


def _login_form():
    with st.form("login_form", clear_on_submit=False):
        st.markdown("#### Welcome back")
        email    = st.text_input("Email Address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            user = get_user_by_email(email)
            if user and verify_password(password, user["password"]):
                st.session_state["user_id"]   = user["id"]
                st.session_state["user_name"] = user["full_name"]
                st.session_state["user_role"] = user["role"]
                st.session_state["page"]      = "dashboard"
                st.rerun()
            else:
                st.error("Invalid email or password.")

    st.markdown("""
    <div style="text-align:center;font-size:13px;color:#64748b;margin-top:12px;">
        Default admin: <code>admin@taskmanager.com</code> / <code>Admin@1234</code>
    </div>
    """, unsafe_allow_html=True)


def _register_form():
    with st.form("register_form", clear_on_submit=True):
        st.markdown("#### Create your free account")
        full_name = st.text_input("Full Name",        placeholder="Your full name")
        email     = st.text_input("Email Address",    placeholder="you@example.com")
        col1, col2 = st.columns(2)
        with col1:
            password  = st.text_input("Password",         type="password", placeholder="Min. 8 chars")
        with col2:
            password2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
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
                    st.success("Account created! Switch to Sign In to log in.")
                else:
                    st.error(result["message"])
