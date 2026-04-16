import streamlit as st
from frontend.utils.api import register_user


def show():
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem 0'>
      <h1 style='color:#0077B6;font-size:2.5rem;font-weight:800'>🏗️ InfraTrack</h1>
      <p style='color:#64748b'>Create your citizen account</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background:#fff;padding:2rem;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08)'>", unsafe_allow_html=True)
        st.subheader("Register")
        username = st.text_input("Username", placeholder="Letters & numbers only, min 3 chars")
        email    = st.text_input("Email",    placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        confirm  = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", use_container_width=True, type="primary"):
            if not all([username, email, password, confirm]):
                st.warning("All fields are required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                with st.spinner("Creating account..."):
                    success, data = register_user(username, email, password)
                if success:
                    st.success("✅ Account created! Redirecting to login...")
                    import time; time.sleep(1)
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    msg = data.get("error") or data.get("detail", "Registration failed.")
                    st.error(f"❌ {msg}")

        st.markdown("---")
        if st.button("Already have an account? Login →", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
