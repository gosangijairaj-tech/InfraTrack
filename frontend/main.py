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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* ── Force sidebar always visible, hide collapse button ── */
  [data-testid="collapsedControl"]          { display: none !important; }
  [data-testid="stSidebarCollapseButton"]   { display: none !important; }
  section[data-testid="stSidebar"]          { transform: none !important; visibility: visible !important; }
  section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    margin-left: 0 !important;
    width: 260px !important;
  }

  /* ── Hide default Streamlit nav ── */
  [data-testid="stSidebarNav"],
  section[data-testid="stSidebarNav"],
  div[data-testid="stSidebarNavItems"]      { display: none !important; }

  /* ── App background ── */
  [data-testid="stAppViewContainer"]        { background: #0f1117; }
  .block-container                          { padding-top: 2rem; }

  /* ── Sidebar base ── */
  section[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    padding: 0 !important;
    width: 260px !important;
    min-width: 260px !important;
  }
  section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
  }

  /* ── Nav buttons ── */
  section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #8b95a6 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
    justify-content: flex-start !important;
    margin-bottom: 2px !important;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #e8eaf0 !important;
    transform: translateX(2px) !important;
  }

  /* ── Active page highlight ── */
  section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(59,130,246,0.12) !important;
    color: #60a5fa !important;
    border-left: 3px solid #3b82f6 !important;
    padding-left: calc(1.2rem - 3px) !important;
  }

  /* ── Main content text colors ── */
  h1, h2, h3, h4, p, label { color: #e8eaf0; font-family: 'Inter', sans-serif !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

defaults = {
    "page": "login", "token": None,
    "role": None,    "username": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

from frontend._pages import login, register, submit_report, user_dashboard, admin_dashboard, analytics

if st.session_state.get("token"):
    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────────
        st.markdown("""
        <div style='padding:1.5rem 1.2rem 1rem;border-bottom:1px solid rgba(255,255,255,0.06)'>
          <div style='display:flex;align-items:center;gap:10px'>
            <div style='background:linear-gradient(135deg,#3b82f6,#06b6d4);
                        width:38px;height:38px;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.1rem;flex-shrink:0;
                        box-shadow:0 4px 12px rgba(59,130,246,0.35)'>🏗️</div>
            <div>
              <div style='color:#e8eaf0;font-weight:700;font-size:1.05rem;
                          font-family:Inter,sans-serif;line-height:1.2'>InfraTrack</div>
              <div style='color:#4b5563;font-size:0.7rem;font-family:Inter,sans-serif'>
                Smart Infrastructure Monitor</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── User card ─────────────────────────────────────────────────────────
        role  = st.session_state.get("role", "user")
        uname = st.session_state.get("username", "")
        role_color = "#f59e0b" if role == "admin" else "#60a5fa"
        role_bg    = "rgba(245,158,11,0.12)" if role == "admin" else "rgba(96,165,250,0.12)"
        role_icon  = "⚡" if role == "admin" else "👤"
        initials   = uname[:2].upper() if uname else "??"

        st.markdown(f"""
        <div style='margin:0.75rem 1rem;padding:0.75rem;
                    background:rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.07);
                    border-radius:10px;display:flex;align-items:center;gap:10px'>
          <div style='background:linear-gradient(135deg,{role_color}33,{role_color}22);
                      width:36px;height:36px;border-radius:9px;flex-shrink:0;
                      display:flex;align-items:center;justify-content:center;
                      color:{role_color};font-weight:700;font-size:0.8rem;
                      font-family:Inter,sans-serif;border:1px solid {role_color}33'>{initials}</div>
          <div style='min-width:0'>
            <div style='color:#e8eaf0;font-size:0.85rem;font-weight:600;
                        font-family:Inter,sans-serif;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis'>{uname}</div>
            <div style='display:flex;align-items:center;gap:4px;margin-top:1px'>
              <span style='color:{role_color};font-size:0.65rem'>{role_icon}</span>
              <span style='color:{role_color};font-size:0.65rem;font-family:Inter,sans-serif;
                           text-transform:uppercase;letter-spacing:0.08em'>{role}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Nav section label ─────────────────────────────────────────────────
        st.markdown("""
        <div style='padding:0.25rem 1.2rem 0.25rem;margin-top:0.25rem;
                    color:#374151;font-size:0.65rem;font-family:Inter,sans-serif;
                    text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>
          Navigation
        </div>
        """, unsafe_allow_html=True)

        # ── Nav items ─────────────────────────────────────────────────────────
        cur = st.session_state.get("page", "")
        nav_items = [
            ("submit_report",   "📍",  "Submit Report"),
            ("user_dashboard",  "📊",  "My Dashboard"),
        ]
        if role == "admin":
            nav_items += [
                ("admin_dashboard", "🛠️", "Admin Panel"),
                ("analytics",       "📈", "Analytics"),
            ]

        for page_key, icon, label in nav_items:
            is_active = cur == page_key
            if st.button(f"{icon}  {label}", use_container_width=True,
                         key=f"nav_{page_key}",
                         type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_key
                st.rerun()

        # ── Logout ────────────────────────────────────────────────────────────
        st.markdown("""
        <div style='margin:1rem 1rem 0;border-top:1px solid rgba(255,255,255,0.06);
                    padding-top:0.75rem'></div>
        """, unsafe_allow_html=True)

        if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "login"
            st.rerun()

        # ── Footer ────────────────────────────────────────────────────────────
        st.markdown("""
        <div style='padding:1.25rem 1.2rem 1rem;margin-top:auto;
                    color:#2d3748;font-size:0.68rem;font-family:Inter,sans-serif;
                    text-align:center;border-top:1px solid rgba(255,255,255,0.04);
                    margin-top:2rem'>
          InfraTrack v2.0
        </div>
        """, unsafe_allow_html=True)

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
