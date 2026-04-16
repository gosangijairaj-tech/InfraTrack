import streamlit as st
from frontend.utils.api import login_user, health_check


def show():
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem 0'>
      <h1 style='color:#0077B6;font-size:2.5rem;font-weight:800'>🏗️ InfraTrack</h1>
      <p style='color:#64748b'>Geotagged Infrastructure Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    ok, hdata = health_check()
    if not ok:
        st.error("❌ Cannot reach backend. Start FastAPI on port 8000.")
        return

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background:#fff;padding:2rem;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08)'>", unsafe_allow_html=True)
        st.subheader("Sign In")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("Login", use_container_width=True, type="primary"):
            if not username or not password:
                st.warning("Please fill in all fields.")
            else:
                with st.spinner("Logging in..."):
                    success, data = login_user(username, password)
                if success:
                    st.session_state["token"]    = data["access_token"]
                    st.session_state["username"] = data["username"]
                    st.session_state["role"]     = data["role"]
                    st.session_state["page"]     = "user_dashboard"
                    st.rerun()
                else:
                    msg = data.get("error") or data.get("detail", "Login failed.")
                    st.error(f"❌ {msg}")

        st.markdown("---")
        if st.button("Don't have an account? Register →", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
