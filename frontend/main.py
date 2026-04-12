import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="InfraTrack",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS
st.markdown("""
<style>
    body { background-color: #f0f4f8; }
    .block-container { padding-top: 1.5rem; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button[kind="primary"] {
        background: #0077B6;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: #005f8e;
    }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    .stExpander { border-radius: 10px; border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

from frontend.pages import login, register, submit_report, user_dashboard, admin_dashboard, analytics

# Initialise session state
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "token" not in st.session_state:
    st.session_state["token"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# Sidebar navigation (only when logged in)
if st.session_state.get("token"):
    with st.sidebar:
        st.markdown(f"### 👋 {st.session_state['username']}")
        st.markdown(f"*Role: {st.session_state['role']}*")
        st.markdown("---")

        if st.button("📍 Submit Report", use_container_width=True):
            st.session_state["page"] = "submit_report"
            st.rerun()

        if st.button("👤 My Dashboard", use_container_width=True):
            st.session_state["page"] = "user_dashboard"
            st.rerun()

        if st.session_state.get("role") == "admin":
            if st.button("🛠️ Admin Panel", use_container_width=True):
                st.session_state["page"] = "admin_dashboard"
                st.rerun()
            if st.button("🌍 Analytics", use_container_width=True):
                st.session_state["page"] = "analytics"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ["token", "username", "role"]:
                st.session_state[key] = None
            st.session_state["page"] = "login"
            st.rerun()

# Page router
page = st.session_state.get("page", "login")

if page == "login":
    login.show()
elif page == "register":
    register.show()
elif page == "submit_report":
    submit_report.show()
elif page == "user_dashboard":
    user_dashboard.show()
elif page == "admin_dashboard":
    admin_dashboard.show()
elif page == "analytics":
    analytics.show()