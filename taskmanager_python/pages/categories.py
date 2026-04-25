# pages/categories.py
import streamlit as st
from utils.database import get_categories, create_category, delete_category
from utils.ui import page_header, empty_state


def show_categories():
    user_id = st.session_state["user_id"]
    page_header("Categories", "Group your tasks into colour-coded collections")

    cats = get_categories(user_id)

    # ── Add form ─────────────────────────────────────────────
    with st.expander("➕  Create New Category", expanded=len(cats) == 0):
        with st.form("cat_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                name  = st.text_input("Category Name", placeholder="e.g. School, Personal, Work, Research")
            with col2:
                color = st.color_picker("Colour", "#4338ca")
            with col3:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Create →", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("Category name is required.")
                else:
                    create_category(user_id, name.strip(), color)
                    st.success(f"✅ Category '{name}' created!")
                    st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Category list ────────────────────────────────────────
    if not cats:
        empty_state("🏷️", "No categories yet", "Create your first category above to group your tasks.")
        return

    # Header
    st.markdown("""
    <div style="display:grid;grid-template-columns:0.6fr 3fr 1.5fr 1fr;gap:12px;
                padding:0 4px 10px;border-bottom:1px solid #e8e4d9;margin-bottom:4px;">
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Color</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Name</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Tasks</span>
        <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#9ca3af;">Action</span>
    </div>
    """, unsafe_allow_html=True)

    for c in cats:
        rc = st.columns([0.6, 3, 1.5, 1])

        with rc[0]:
            st.markdown(
                f'<div style="width:32px;height:32px;border-radius:8px;background:{c["color"]};'
                f'margin-top:2px;box-shadow:0 2px 6px {c["color"]}44;"></div>',
                unsafe_allow_html=True
            )
        with rc[1]:
            hex_code = c["color"]
            st.markdown(
                f'<div style="padding-top:4px;">'
                f'<span style="font-weight:500;color:#111827;font-size:15px;">{c["name"]}</span>'
                f'<span style="font-size:11px;color:#9ca3af;font-family:\'DM Mono\',monospace;'
                f'margin-left:10px;">{hex_code}</span></div>',
                unsafe_allow_html=True
            )
        with rc[2]:
            count = c["task_count"] or 0
            st.markdown(
                f'<div style="padding-top:6px;font-size:14px;color:#374151;">'
                f'{count} task{"s" if count != 1 else ""}</div>',
                unsafe_allow_html=True
            )
        with rc[3]:
            if st.button("🗑️ Delete", key=f"delcat_{c['id']}", use_container_width=True):
                delete_category(c["id"], user_id)
                st.success(f"Deleted '{c['name']}'.")
                st.rerun()

        st.markdown('<hr style="margin:8px 0;border-color:#f3f4f6;">', unsafe_allow_html=True)
