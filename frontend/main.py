import os
import sys
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebarNav"] {display:none;}

[data-testid="stAppViewContainer"] {
    background: #0a0c10;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
    180deg,
    rgb(10, 25, 47) 0%,
    rgb(2, 6, 23) 100%
);
}
            
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); }

.brand-box {
    padding: 20px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.brand-title {
    font-size: 16px;
    font-weight: 700;
    color: #f1f5f9;
}
.brand-sub {
    font-size: 10px;
    color: #334155;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.profile-card {
    margin: 14px;
    padding: 12px;
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
}
.avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #1e293b;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #38bdf8;
}
.username {
    font-size: 13px;
    font-weight: 600;
    color: #e2e8f0;
}
.role-badge {
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 5px;
    background: rgba(56,189,248,0.1);
    color: #38bdf8;
    border: 1px solid rgba(56,189,248,0.2);
}

.nav-section {
    padding: 10px 14px;
}

.stButton > button {
    background: transparent;
    border: none;
    color: #64748b;
    text-align: left;
    padding: 10px;
    border-radius: 10px;
    width: 100%;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.03);
    color: #e2e8f0;
    transform: translateX(3px);
}

.logout button {
    background: rgba(239,68,68,0.05) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    color: #ef4444 !important;
}
.logout button:hover {
    background: rgba(239,68,68,0.1) !important;
}
</style>
""", unsafe_allow_html=True)
defaults = {
    "page": "login",
    "token": None,
    "role": None,
    "username": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
from frontend._pages import (
    login, register, submit_report,
    user_dashboard, admin_dashboard, analytics
)
if st.session_state.get("token"):

    with st.sidebar:

        # BRAND
        st.markdown("""
        <div class="brand-box">
            <div style="display:flex;align-items:center;gap:10px">
                <span style="font-size:22px">🏬</span>
                <div>
                    <div class="brand-title">InfraTrack</div>
                    <div class="brand-sub">Geo-Tagged Infrastructure</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PROFILE
        uname = st.session_state.get("username", "User")
        role = st.session_state.get("role", "user")
        initials = uname[:2].upper()

        st.markdown(f"""
        <div class="profile-card">
            <div style="display:flex;align-items:center;gap:10px">
                <div class="avatar">{initials}</div>
                <div>
                    <div class="username">{uname}</div>
                    <div class="role-badge">{role.upper()}</div>
                    <div style="font-size:9px;color:#334155;text-transform:uppercase;letter-spacing:0.08em;margin-top:2px;">Smart Infrastructure</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # NAVIGATION
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)

        nav_items = [
            ("submit_report", "📍  Submit Report"),
            ("user_dashboard", "📊  Dashboard"),
        ]

        if role == "admin":
            nav_items += [
                ("admin_dashboard", "🛠  Admin Panel"),
                ("analytics", "📈  Analytics"),
            ]

        current = st.session_state.get("page")

        for key, label in nav_items:
            btn = st.button(label, key=f"nav_{key}", use_container_width=True)
            if btn:
                st.session_state["page"] = key
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # LOGOUT
        st.markdown('<div class="logout">', unsafe_allow_html=True)
        if st.button("🔓  Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
PAGE_MAP = {
    "login": login.show,
    "register": register.show,
    "submit_report": submit_report.show,
    "user_dashboard": user_dashboard.show,
    "admin_dashboard": admin_dashboard.show,
    "analytics": analytics.show,
}

page_fn = PAGE_MAP.get(st.session_state["page"])

if page_fn:
    page_fn()
else:
    st.session_state["page"] = "login"
    st.rerun()
