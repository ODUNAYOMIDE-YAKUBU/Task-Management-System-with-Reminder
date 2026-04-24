# pages/categories.py
# Category management page
# ============================================================

import streamlit as st
from utils.database import get_categories, create_category, delete_category
from utils.ui import page_header


def show_categories():
    user_id = st.session_state["user_id"]
    page_header("Categories", "Organise your tasks into colour-coded groups")

    cats = get_categories(user_id)

    # ---- Add Category Form ---------------------------------
    with st.expander("➕ Create New Category", expanded=len(cats) == 0):
        with st.form("cat_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                name = st.text_input("Category Name", placeholder="e.g. School, Personal, Work")
            with col2:
                color = st.color_picker("Colour", "#4f46e5")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Create", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("Category name is required.")
                else:
                    create_category(user_id, name.strip(), color)
                    st.success(f"Category '{name}' created!")
                    st.rerun()

    st.markdown("---")

    # ---- Category List -------------------------------------
    if not cats:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#64748b;">
            <div style="font-size:36px;margin-bottom:12px;">🏷️</div>
            <h3 style="color:#334155;">No categories yet</h3>
            <p>Create a category above to group your tasks.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Header row
    hc = st.columns([1, 3, 2, 2])
    for col, label in zip(hc, ["Colour", "Name", "Tasks", "Action"]):
        col.markdown(f"<small style='color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:600;'>{label}</small>", unsafe_allow_html=True)
    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

    for c in cats:
        rc = st.columns([1, 3, 2, 2])

        with rc[0]:
            st.markdown(
                f'<div style="width:28px;height:28px;border-radius:6px;background:{c["color"]};'
                f'margin-top:4px;"></div>',
                unsafe_allow_html=True,
            )
        with rc[1]:
            st.markdown(f"**{c['name']}**")
        with rc[2]:
            count = c["task_count"] or 0
            st.markdown(f"{count} task{'s' if count != 1 else ''}")
        with rc[3]:
            if st.button("🗑️ Delete", key=f"delcat_{c['id']}"):
                delete_category(c["id"], user_id)
                st.success(f"Category '{c['name']}' deleted.")
                st.rerun()

        st.markdown('<hr style="margin:4px 0;border-color:#f1f5f9;">', unsafe_allow_html=True)
