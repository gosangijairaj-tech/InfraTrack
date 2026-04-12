import streamlit as st
from frontend.utils.api import register_user


def show():
    st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem 0'>
        <h1 style='color:#0077B6; font-size:2.5rem; font-weight:700'>🏗️ InfraTrack</h1>
        <p style='color:#555'>Create your account</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background:#fff; padding:2rem; border-radius:16px; box-shadow:0 2px 16px rgba(0,0,0,0.08)'>", unsafe_allow_html=True)
        st.subheader("Register")
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", use_container_width=True, type="primary"):
            if not username or not email or not password:
                st.error("All fields are required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                code, data = register_user(username, email, password)
                if code == 200:
                    st.success("Account created! Please log in.")
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.error(data.get("detail", "Registration failed"))

        st.markdown("---")
        if st.button("Already have an account? Login", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)