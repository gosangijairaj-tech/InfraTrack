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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
  [data-testid="collapsedControl"]          { display: none !important; }
  [data-testid="stSidebarCollapseButton"]   { display: none !important; }
  section[data-testid="stSidebar"]          { transform: none !important; visibility: visible !important; }
  section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    margin-left: 0 !important;
    width: 280px !important;
  }
  [data-testid="stSidebarNav"],
  section[data-testid="stSidebarNav"],
  div[data-testid="stSidebarNavItems"]      { display: none !important; }
  [data-testid="stAppViewContainer"] { 
    background: linear-gradient(135deg, #0a0c10 0%, #0f1117 100%);
  }
  .block-container { padding-top: 2rem; }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(18,22,35,0.98) 0%, rgba(12,15,25,0.98) 100%) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(59,130,246,0.15) !important;
    padding: 0 !important;
    width: 280px !important;
    min-width: 280px !important;
    box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  }
  section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
  }
  .glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
  }
  section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #8b95a6 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.7rem 1.2rem !important;
    border-radius: 12px !important;
    width: 100% !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    justify-content: flex-start !important;
    margin-bottom: 4px !important;
    letter-spacing: -0.01em;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(90deg, rgba(59,130,246,0.1) 0%, rgba(59,130,246,0.05) 100%) !important;
    color: #e8eaf0 !important;
    transform: translateX(4px) !important;
    border-left: 2px solid #3b82f6 !important;
  }
  section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(59,130,246,0.15) 0%, rgba(59,130,246,0.05) 100%) !important;
    color: #60a5fa !important;
    border-left: 3px solid #3b82f6 !important;
    padding-left: calc(1.2rem - 3px) !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.15);
  }
  h1, h2, h3, h4, p, label { 
    color: #e8eaf0; 
    font-family: 'Space Grotesk', sans-serif !important;
  }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
  ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #3b82f6, #06b6d4); border-radius: 4px; }
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .nav-item {
    animation: slideIn 0.3s ease-out forwards;
  }
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
        st.markdown("""
        <style>
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
          }
          .logo-icon {
            animation: float 3s ease-in-out infinite;
          }
        </style>
        <div style='padding:2rem 1.5rem 1.5rem;border-bottom:1px solid rgba(59,130,246,0.15);
                    background: linear-gradient(135deg, rgba(59,130,246,0.05) 0%, rgba(6,182,212,0.02) 100%);'>
          <div style='display:flex;align-items:center;gap:12px'>
            <div class='logo-icon' style='background:linear-gradient(135deg,#3b82f6,#06b6d4);
                        width:45px;height:45px;border-radius:14px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.3rem;flex-shrink:0;
                        box-shadow:0 8px 20px rgba(59,130,246,0.3);
                        transition:transform 0.3s ease'>
              🏗️
            </div>
            <div>
              <div style='color:#e8eaf0;font-weight:800;font-size:1.2rem;
                          font-family:Space Grotesk,sans-serif;line-height:1.2;
                          background:linear-gradient(135deg,#e8eaf0,#60a5fa);
                          -webkit-background-clip:text;
                          -webkit-text-fill-color:transparent'>
                InfraTrack
              </div>
              <div style='color:#6b7280;font-size:0.7rem;font-family:Space Grotesk,sans-serif;
                          letter-spacing:0.02em'>
                Smart Infrastructure Monitor
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        role = st.session_state.get("role", "user")
        uname = st.session_state.get("username", "")
        role_color = "#f59e0b" if role == "admin" else "#60a5fa"
        role_bg = "linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.05))" if role == "admin" else "linear-gradient(135deg, rgba(96,165,250,0.15), rgba(96,165,250,0.05))"
        role_icon = "⚡" if role == "admin" else "👤"
        initials = uname[:2].upper() if uname else "??"
        st.markdown(f"""
        <style>
          .profile-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
            border: 1px solid rgba(59,130,246,0.2);
            transition: all 0.3s ease;
          }}
          .profile-card:hover {{
            border-color: rgba(59,130,246,0.4);
            transform: translateY(-2px);
          }}
        </style>
        <div class='profile-card' style='margin:1.25rem 1.2rem;padding:0.9rem;
                    border-radius:16px;display:flex;align-items:center;gap:12px;
                    position:relative;overflow:hidden'>
          <div style='position:absolute;top:0;left:0;right:0;bottom:0;
                      background:radial-gradient(circle at top right, {role_color}10, transparent 70%)'>
          </div>
          <div style='background:linear-gradient(135deg,{role_color}44,{role_color}22);
                      width:42px;height:42px;border-radius:12px;flex-shrink:0;
                      display:flex;align-items:center;justify-content:center;
                      color:{role_color};font-weight:700;font-size:0.9rem;
                      font-family:Space Grotesk,sans-serif;border:1px solid {role_color}44;
                      backdrop-filter:blur(5px)'>
            {initials}
          </div>
          <div style='min-width:0;flex:1'>
            <div style='color:#e8eaf0;font-size:0.9rem;font-weight:700;
                        font-family:Space Grotesk,sans-serif;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;
                        letter-spacing:-0.01em'>{uname}</div>
            <div style='display:flex;align-items:center;gap:6px;margin-top:4px'>
              <span style='color:{role_color};font-size:0.7rem'>{role_icon}</span>
              <span style='color:{role_color};font-size:0.7rem;font-family:Space Grotesk,sans-serif;
                           text-transform:uppercase;letter-spacing:0.08em;font-weight:600'>{role}</span>
              <div style='width:4px;height:4px;background:{role_color};border-radius:50%;opacity:0.5'></div>
              <span style='color:#6b7280;font-size:0.65rem'>● Active</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='padding:0.5rem 1.5rem 0.25rem;margin-top:0.5rem;
                    color:#374151;font-size:0.7rem;font-family:Space Grotesk,sans-serif;
                    text-transform:uppercase;letter-spacing:0.12em;font-weight:700'>
          MAIN MENU
        </div>
        """, unsafe_allow_html=True)
        cur = st.session_state.get("page", "")
        nav_items = [
            ("submit_report",   "📍",  "Submit Report", "Report infrastructure issues"),
            ("user_dashboard",  "📊",  "My Dashboard", "Track your reports"),
        ]
        if role == "admin":
            nav_items += [
                ("admin_dashboard", "🛠️", "Admin Panel", "Manage infrastructure"),
                ("analytics",       "📈",  "Analytics", "Insights & metrics"),
            ]

        for idx, (page_key, icon, label, desc) in enumerate(nav_items):
            is_active = cur == page_key
            # Add animation delay for each item
            st.markdown(f'<div class="nav-item" style="animation-delay: {idx * 0.05}s">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", use_container_width=True,
                         key=f"nav_{page_key}",
                         type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_key
                st.rerun()
            if not is_active:
                st.markdown(f"<div style='margin-top:-8px;margin-bottom:4px;margin-left:32px;color:#4b5563;font-size:0.65rem;font-family:Space Grotesk,sans-serif'>{desc}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='margin:1.5rem 1.2rem 0;border-top:1px solid rgba(59,130,246,0.15);
                    padding-top:1rem'></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <style>
          button[key="logout_btn"] {
            background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.05)) !important;
            border: 1px solid rgba(239,68,68,0.2) !important;
            transition: all 0.3s ease !important;
          }
          button[key="logout_btn"]:hover {
            background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.1)) !important;
            border-color: rgba(239,68,68,0.4) !important;
            transform: translateX(4px) !important;
          }
        </style>
        """, unsafe_allow_html=True)

        if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "login"
            st.rerun()
        st.markdown("""
        <div style='padding:1.5rem 1.2rem 1.2rem;margin-top:auto;
                    margin-top:2rem'>
          <div style='background:linear-gradient(135deg, rgba(59,130,246,0.05), rgba(6,182,212,0.02));
                      border-radius:12px;padding:0.75rem;text-align:center'>
            <div style='color:#4b5563;font-size:0.75rem;font-family:Space Grotesk,sans-serif;
                        font-weight:600;letter-spacing:0.05em'>
              INFRASTRUCTURE v2.0
            </div>
            <div style='color:#374151;font-size:0.65rem;font-family:Space Grotesk,sans-serif;
                        margin-top:4px'>
              ● System Operational
            </div>
            <div style='display:flex;gap:6px;justify-content:center;margin-top:8px'>
              <div style='width:6px;height:6px;background:#10b981;border-radius:50%;box-shadow:0 0 6px #10b981'></div>
              <div style='width:6px;height:6px;background:#3b82f6;border-radius:50%;box-shadow:0 0 6px #3b82f6'></div>
              <div style='width:6px;height:6px;background:#f59e0b;border-radius:50%;box-shadow:0 0 6px #f59e0b'></div>
            </div>
          </div>
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