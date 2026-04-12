import streamlit as st
import pandas as pd
from frontend.utils.api import get_my_reports
from frontend.utils.map_utils import build_report_map
from streamlit_folium import st_folium


def priority_badge(p):
    colors = {"High": "#e63946", "Medium": "#f4a261", "Low": "#2a9d8f"}
    c = colors.get(p, "#888")
    return f"<span style='background:{c};color:#fff;padding:2px 10px;border-radius:12px;font-size:0.8rem'>{p}</span>"


def status_badge(s):
    colors = {"Pending": "#adb5bd", "In Progress": "#4895ef", "Resolved": "#2a9d8f"}
    c = colors.get(s, "#888")
    return f"<span style='background:{c};color:#fff;padding:2px 10px;border-radius:12px;font-size:0.8rem'>{s}</span>"


def show():
    st.markdown("<h2 style='color:#0077B6'>👤 My Reports Dashboard</h2>", unsafe_allow_html=True)
    token = st.session_state.get("token")
    if not token:
        st.warning("Please log in.")
        return

    code, data = get_my_reports(token)
    if code != 200:
        st.error("Could not load reports.")
        return

    if not data:
        st.info("You haven't submitted any reports yet.")
        if st.button("Submit Your First Report"):
            st.session_state["page"] = "submit_report"
            st.rerun()
        return

    # Summary cards
    df = pd.DataFrame(data)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div style='background:#0077B6;color:#fff;padding:1rem;border-radius:12px;text-align:center'>
            <h3>{len(df)}</h3><p>Total Reports</p></div>""", unsafe_allow_html=True)
    with col2:
        high = len(df[df["priority"] == "High"]) if "priority" in df else 0
        st.markdown(f"""<div style='background:#e63946;color:#fff;padding:1rem;border-radius:12px;text-align:center'>
            <h3>{high}</h3><p>High Priority</p></div>""", unsafe_allow_html=True)
    with col3:
        resolved = len(df[df["status"] == "Resolved"]) if "status" in df else 0
        st.markdown(f"""<div style='background:#2a9d8f;color:#fff;padding:1rem;border-radius:12px;text-align:center'>
            <h3>{resolved}</h3><p>Resolved</p></div>""", unsafe_allow_html=True)
    with col4:
        avg_score = round(df["risk_score"].mean(), 1) if "risk_score" in df else 0
        st.markdown(f"""<div style='background:#f4a261;color:#fff;padding:1rem;border-radius:12px;text-align:center'>
            <h3>{avg_score}</h3><p>Avg Risk Score</p></div>""", unsafe_allow_html=True)

    st.markdown("### 🗺️ My Reports on Map")
    m = build_report_map(data)
    st_folium(m, width=700, height=400)

    st.markdown("### 📋 Report List")
    for r in sorted(data, key=lambda x: x.get("risk_score", 0), reverse=True):
        with st.expander(f"[{r.get('category','N/A')}] — Risk {r.get('risk_score','?')}/100 | {r.get('created_at','')[:10]}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Description:** {r.get('description','')}")
                st.write(f"**Location:** {r.get('location_label', f\"{r.get('latitude','?')}, {r.get('longitude','?')}\")}")
                st.markdown(f"**Priority:** {priority_badge(r.get('priority',''))}", unsafe_allow_html=True)
                st.markdown(f"**Status:** {status_badge(r.get('status',''))}", unsafe_allow_html=True)
            with col2:
                if r.get("image_base64"):
                    import base64
                    st.image(base64.b64decode(r["image_base64"]), width=180)