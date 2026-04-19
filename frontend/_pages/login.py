import streamlit as st
import base64
import os
from frontend.utils.api import login_user, health_check


def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


def show():
    # Dynamic path for local + cloud deployment
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    img_path = os.path.join(BASE_DIR, "images", "background.jpg")

    img = get_base64_image(img_path)

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(
                rgba(0,0,0,0.15),
                rgba(0,0,0,0.28)
            ),
            url("data:image/jpeg;base64,{img}");

        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stSidebar"] {{
        background: rgba(0,0,0,0);
    }}

    .block-container {{
        padding-top: 2rem;
        max-width: 1200px;
    }}

    .main-title {{
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0;
        text-shadow: 0 6px 18px rgba(0,0,0,0.45);
    }}

    .blue {{
        color: #00B4D8;
    }}

    .sub-title {{
        text-align: center;
        color: #e2e8f0;
        margin-top: -5px;
        margin-bottom: 2rem;
        font-size: 1rem;
        text-shadow: 0 4px 10px rgba(0,0,0,0.35);
    }}

    .login-box {{
        background: rgba(10, 18, 32, 0.68);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2rem;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 18px 45px rgba(0,0,0,0.45);
    }}

    label {{
        color: white !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stTextInput"] input {{
        background: rgba(255,255,255,0.08);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 0.7rem;
    }}

    div[data-testid="stTextInput"] input::placeholder {{
        color: rgba(255,255,255,0.65);
    }}

    div[data-testid="stTextInput"] input:focus {{
        border: 1px solid #00B4D8;
        box-shadow: 0 0 0 1px #00B4D8;
    }}

    div.stButton > button {{
        width: 100%;
        height: 3rem;
        border-radius: 10px;
        border: none;
        font-size: 1rem;
        font-weight: 700;
        transition: 0.2s ease;
    }}

    div.stButton > button[kind="primary"] {{
        background: linear-gradient(90deg,#ff4b4b,#ff6b6b);
        color: white;
    }}

    div.stButton > button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 10px 24px rgba(255,75,75,0.35);
    }}

    div.stButton > button:not([kind="primary"]) {{
        background: rgba(255,255,255,0.05);
        color: white;
        border: 1px solid rgba(255,255,255,0.08);
    }}

    div.stButton > button:not([kind="primary"]):hover {{
        background: rgba(255,255,255,0.08);
    }}

    hr {{
        border: 1px solid rgba(255,255,255,0.08);
    }}

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div>
        <h1 class="main-title">🏗️ <span class="blue">Infra</span>Track</h1>
        <p class="sub-title">Geotagged Infrastructure Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    ok, hdata = health_check()

    if not ok:
        st.error(f"❌ Cannot reach backend: {hdata}")
        return

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        st.subheader("Sign In")

        username = st.text_input(
            "Username",
            placeholder="Enter username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True, type="primary"):

            if not username or not password:
                st.warning("Please fill in all fields.")
            else:
                with st.spinner("Logging in..."):
                    success, data = login_user(username, password)

                if success:
                    st.session_state["token"] = data["access_token"]
                    st.session_state["username"] = data["username"]
                    st.session_state["role"] = data["role"]
                    st.session_state["page"] = "user_dashboard"
                    st.rerun()
                else:
                    msg = data.get("error") or data.get("detail", "Login failed.")
                    st.error(f"❌ {msg}")

        st.markdown("---")

        if st.button("Don't have an account? Register →", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
