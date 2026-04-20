import streamlit as st
import base64
import os
from frontend.utils.api import register_user


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


def show():
    # Dynamic image path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    img_path = os.path.join(BASE_DIR, "images", "abc.jpg")

    img = get_base64_image(img_path)

    # 🎨 Background + blur styling
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(
                rgba(0,0,0,0.35),
                rgba(0,0,0,0.55)
            ),
            url("data:image/jpeg;base64,{img}");

        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Blur layer */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 2rem;
        max-width: 1100px;
    }}

    .main-title {{
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0;
    }}

    .sub-title {{
        text-align: center;
        color: #e2e8f0;
        margin-bottom: 2rem;
    }}

    .register-box {{
        background: rgba(10, 18, 32, 0.75);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }}

    label {{
        color: white !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stTextInput"] input {{
        background: rgba(255,255,255,0.08);
        color: white !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    div.stButton > button[kind="primary"] {{
        background: linear-gradient(90deg,#0077B6,#00B4D8);
        color: white;
        font-weight: 700;
    }}

    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("""
    <h1 class="main-title">🏗️ InfraTrack</h1>
    <p class="sub-title">Create your citizen account</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown("<div class='register-box'>", unsafe_allow_html=True)

        st.subheader("Register")

        username = st.text_input("Username", placeholder="Letters & numbers only, min 3 chars")
        email    = st.text_input("Email", placeholder="your@email.com")
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
