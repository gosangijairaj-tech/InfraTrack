import time
import base64
import streamlit as st
import pandas as pd

from frontend.utils.api import get_my_reports
from frontend.utils.map_utils import build_report_map
from frontend.components.ui import (
    priority_badge, status_badge, ai_badge,
    metric_card, section_header, alert,
)
from streamlit_folium import st_folium

REFRESH_INTERVAL = 30


def show():
    token = st.session_state.get("token")
    if not token:
        alert("Please log in.", "error")
        return

    st.markdown("<h2 style='color:#0077B6'>👤 My Reports Dashboard</h2>",
                unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns([2, 1, 1])
    with col_r1:
        last_ts = st.session_state.get("user_last_refresh", time.time())
        st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S', time.localtime(last_ts))}")
    with col_r2:
        auto_on = st.toggle("Auto-refresh", value=True, key="user_auto_refresh")
    with col_r3:
        if st.button("↺ Refresh Now", use_container_width=True):
            st.session_state["user_last_refresh"] = time.time()
            st.rerun()

    with st.spinner("Loading your reports…"):
        success, data = get_my_reports(token)

    if not success:
        alert(data.get("error", "Could not load reports."), "error")
        return

    reports = data.get("reports", [])

    if not reports:
        alert("You haven't submitted any reports yet.", "info")
        if st.button("📍 Submit Your First Report", type="primary"):
            st.session_state["page"] = "submit_report"
            st.rerun()
        return

    df = pd.DataFrame(reports)

    section_header("Summary", "📊")
    cols = st.columns(4)
    with cols[0]:
        st.markdown(metric_card("Total Reports", len(df), "#0077B6"), unsafe_allow_html=True)
    with cols[1]:
        high = int((df["priority"] == "High").sum()) if "priority" in df else 0
        st.markdown(metric_card("High Priority", high, "#e63946"), unsafe_allow_html=True)
    with cols[2]:
        resolved = int((df["status"] == "Resolved").sum()) if "status" in df else 0
        st.markdown(metric_card("Resolved", resolved, "#2a9d8f"), unsafe_allow_html=True)
    with cols[3]:
        avg = round(df["risk_score"].mean(), 1) if "risk_score" in df else 0
        st.markdown(metric_card("Avg Risk Score", avg, "#f4a261"), unsafe_allow_html=True)

    section_header("My Reports on Map", "🗺️")
    valid = [r for r in reports if r.get("latitude") and r.get("longitude")]
    if valid:
        center_lat = sum(r["latitude"]  for r in valid) / len(valid)
        center_lon = sum(r["longitude"] for r in valid) / len(valid)
        m = build_report_map(valid, center_lat=center_lat, center_lon=center_lon)
        st_folium(m, width=700, height=400)
    else:
        alert("No geolocated reports to display.", "info")

    section_header("Report History", "📋")
    if "priority" in df:
        sel_prio = st.selectbox("Filter by priority", ["All", "High", "Medium", "Low"])
        filtered = reports if sel_prio == "All" else [r for r in reports if r.get("priority") == sel_prio]
    else:
        filtered = reports

    for r in sorted(filtered, key=lambda x: x.get("risk_score", 0), reverse=True):
        exp_label = (
            f"[{r.get('category','?')}]  "
            f"Risk {r.get('risk_score','?')}/100  |  "
            f"{r.get('created_at','')[:10]}"
        )
        with st.expander(exp_label):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Description:** {r.get('description','')}")

                loc = r.get("location_label") or "{}, {}".format(
                    r.get("latitude", "?"), r.get("longitude", "?")
                )
                st.write(f"**Location:** {loc}")

                src_map = {"gps": "📡 GPS", "manual": "✏️ Manual", "map_click": "🗺️ Map click"}
                src_label = src_map.get(r.get("location_source", "manual"), "Manual")
                acc = r.get("location_accuracy")
                acc_str = f" (±{acc:.0f}m)" if acc else ""
                st.write(f"**Location source:** {src_label}{acc_str}")

                st.markdown(
                    f"**Priority:** {priority_badge(r.get('priority',''))}  "
                    f"&nbsp;**Status:** {status_badge(r.get('status',''))}",
                    unsafe_allow_html=True,
                )
                st.markdown(ai_badge(r.get("ai_powered", False)), unsafe_allow_html=True)

                if r.get("reasoning"):
                    st.caption(f"🤖 {r['reasoning']}")
                if r.get("recommended_action"):
                    st.caption(f"🔧 {r['recommended_action']}")

            with c2:
                if r.get("image_base64"):
                    try:
                        st.image(base64.b64decode(r["image_base64"]), width=160)
                    except Exception:
                        st.caption("Image unavailable")
    if auto_on:
        remaining = max(0, REFRESH_INTERVAL - (time.time() - st.session_state.get("user_last_refresh", 0)))
        st.caption(f"⏱ Next auto-refresh in {int(remaining)}s")
        time.sleep(1)
        st.rerun()
