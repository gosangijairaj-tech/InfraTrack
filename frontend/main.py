import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="InfraTrack",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f0f4f8; }
  [data-testid="stSidebar"]          { background: #ffffff; border-right: 1px solid #e2e8f0; }
  .block-container                   { padding-top: 1.5rem; }
  .stButton > button                 { border-radius: 8px; font-weight: 600; transition: all .15s; }
  .stButton > button[kind="primary"] { background: #0077B6; border: none; }
  .stButton > button[kind="primary"]:hover { background: #005f8e; }
  h1, h2, h3, h4                    { font-family: 'Segoe UI', sans-serif; }
  .stExpander                        { border-radius: 10px !important; border: 1px solid #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

defaults = {
    "page": "login", "token": None,
    "role": None,    "username": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

from frontend.pages import login, register, submit_report, user_dashboard, admin_dashboard, analytics

if st.session_state.get("token"):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 0.5rem 0'>
          <span style='font-size:2rem'>🏗️</span>
          <h3 style='margin:0;color:#0077B6;font-weight:800'>InfraTrack</h3>
          <p style='font-size:0.75rem;color:#64748b;margin:0'>Infrastructure Monitor</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"<div style='background:#f0f9ff;border-radius:8px;padding:8px 12px;"
            f"margin:8px 0;font-size:0.85rem'>"
            f"👤 <b>{st.session_state['username']}</b><br>"
            f"<span style='color:#64748b;font-size:0.75rem'>Role: {st.session_state['role']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        if st.button("📍 Submit Report",  use_container_width=True):
            st.session_state["page"] = "submit_report"
            st.rerun()

        if st.button("👤 My Dashboard",   use_container_width=True):
            st.session_state["page"] = "user_dashboard"
            st.rerun()

        if st.session_state.get("role") == "admin":
            if st.button("🛠️ Admin Panel",  use_container_width=True):
                st.session_state["page"] = "admin_dashboard"
                st.rerun()
            if st.button("🌍 Analytics",    use_container_width=True):
                st.session_state["page"] = "analytics"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "login"
            st.rerun()

PAGE_MAP = {
    "login":           login.show,
    "register":        register.show,
    "submit_report":   submit_report.show,
    "user_dashboard":  user_dashboard.show,
    "admin_dashboard": admin_dashboard.show,
    "analytics":       analytics.show,
}

page_fn = PAGE_MAP.get(st.session_state["page"])
if page_fn:
    page_fn()
else:
    st.session_state["page"] = "login"
    st.rerun()
