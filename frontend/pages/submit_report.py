"""
FIX #3 — Three location modes:
  1. Browser GPS (navigator.geolocation — real device coordinates)
  2. Manual coordinate input
  3. Interactive map click (Folium)
FIX #1 — Displays full AI analysis result including reasoning,
          affected population, and recommended action.
FIX #8 — Category list fetched from backend (DB-driven).
"""

import base64
import io
import json
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from frontend.utils.api import submit_report, get_categories
from frontend.utils.map_utils import build_report_map
from frontend.components.ui import alert, section_header, priority_badge, ai_badge
from streamlit_folium import st_folium


# ── GPS Component (FIX #3) ────────────────────────────────────────────────────
GPS_HTML = """
<style>
  body{margin:0;font-family:'Segoe UI',sans-serif}
  #btn{background:#0077B6;color:#fff;border:none;padding:10px 18px;
       border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;width:100%}
  #btn:hover{background:#005f8e}
  #btn:disabled{background:#94a3b8;cursor:not-allowed}
  #st{margin-top:8px;font-size:12px;padding:6px 10px;border-radius:6px;display:none}
  .ok{background:#d1fae5;color:#065f46}
  .er{background:#fee2e2;color:#991b1b}
  .ld{background:#dbeafe;color:#1e40af}
</style>
<button id="btn" onclick="go()">📡 Capture GPS Location</button>
<div id="st"></div>
<script>
function go(){
  const btn=document.getElementById('btn'),st=document.getElementById('st');
  if(!navigator.geolocation){
    st.textContent='❌ Geolocation not supported by your browser.';
    st.className='er';st.style.display='block';return;
  }
  btn.disabled=true;btn.textContent='⏳ Acquiring GPS…';
  st.textContent='Requesting location from device…';st.className='ld';st.style.display='block';
  navigator.geolocation.getCurrentPosition(
    p=>{
      const lat=p.coords.latitude.toFixed(6),
            lon=p.coords.longitude.toFixed(6),
            acc=Math.round(p.coords.accuracy);
      st.textContent=`✅ Lat: ${lat}  Lon: ${lon}  (±${acc} m accuracy)`;
      st.className='ok';
      btn.textContent='✅ GPS Captured';
      window.parent.postMessage(
        {type:'streamlit:setComponentValue',
         value:JSON.stringify({lat:parseFloat(lat),lon:parseFloat(lon),accuracy:acc})},
        '*'
      );
    },
    e=>{
      const msgs={1:'Permission denied — allow location in browser settings.',
                  2:'Position unavailable. Check GPS/Wi-Fi.',
                  3:'Timed out. Try again.'};
      st.textContent='❌ '+(msgs[e.code]||'Unknown error');
      st.className='er';btn.disabled=false;btn.textContent='📡 Capture GPS Location';
    },
    {enableHighAccuracy:true,timeout:12000,maximumAge:0}
  );
}
</script>
"""


def show():
    token = st.session_state.get("token")
    if not token:
        alert("Please log in first.", "error")
        return

    st.markdown("<h2 style='color:#0077B6'>📍 Submit Infrastructure Report</h2>",
                unsafe_allow_html=True)

    # ── Photo Upload ──────────────────────────────────────────────────────────
    section_header("Upload Photo", "📸")
    uploaded = st.file_uploader("Photo of the issue (JPG/PNG)", type=["jpg", "jpeg", "png"])
    image_b64 = ""
    if uploaded:
        img = Image.open(uploaded)
        img.thumbnail((900, 900))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        image_b64 = base64.b64encode(buf.getvalue()).decode()
        st.image(img, caption="Preview", use_column_width=True)

    # ── Description ───────────────────────────────────────────────────────────
    section_header("Description", "📝")
    description = st.text_area(
        "Describe the issue in detail",
        placeholder="e.g. Large pothole on Main Street near the bus stop causing vehicle damage and flooding during rain…",
        height=130,
    )
    if description:
        wc = len(description.split())
        color = "#2a9d8f" if wc >= 10 else "#e63946"
        st.markdown(
            f"<small style='color:{color}'>{wc} words — {'Good detail ✓' if wc >= 10 else 'Add more detail for better AI analysis'}</small>",
            unsafe_allow_html=True,
        )

    # ── Location (FIX #3) ─────────────────────────────────────────────────────
    section_header("Location", "📍")
    mode = st.radio(
        "Location source",
        ["📡 Browser GPS (recommended)", "✏️ Enter Coordinates", "🗺️ Pick on Map"],
        horizontal=True,
    )

    lat, lon, location_label, location_source, location_accuracy = (
        None, None, "", "manual", None
    )

    if mode == "📡 Browser GPS (recommended)":
        alert("Click the button below. Your browser will ask for permission.", "info")

        # FIX #3 — real browser geolocation
        gps_result = components.html(GPS_HTML, height=90)

        if gps_result:
            try:
                gps = json.loads(gps_result)
                lat              = gps["lat"]
                lon              = gps["lon"]
                location_accuracy = gps.get("accuracy")
                location_source  = "gps"
                location_label   = f"{lat:.5f}, {lon:.5f}"
                st.session_state["gps_lat"] = lat
                st.session_state["gps_lon"] = lon
                st.session_state["gps_acc"] = location_accuracy
            except Exception:
                pass

        # Persist GPS result across reruns
        if "gps_lat" in st.session_state and lat is None:
            lat              = st.session_state["gps_lat"]
            lon              = st.session_state["gps_lon"]
            location_accuracy = st.session_state.get("gps_acc")
            location_source  = "gps"
            location_label   = f"{lat:.5f}, {lon:.5f}"

        if lat:
            st.success(f"📡 GPS locked: {lat:.5f}, {lon:.5f}" +
                       (f" (±{location_accuracy:.0f}m)" if location_accuracy else ""))
        else:
            alert("GPS not yet captured. You can also use manual input below.", "warning")
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude  (fallback)", value=17.385044, format="%.6f", key="fb_lat")
            with col2:
                lon = st.number_input("Longitude (fallback)", value=78.486671, format="%.6f", key="fb_lon")
            location_source = "manual"
            location_label  = f"{lat:.5f}, {lon:.5f}"

    elif mode == "✏️ Enter Coordinates":
        alert("Enter coordinates manually. Get them from Google Maps (right-click → 'What's here?').", "info")
        location_label = st.text_input("Location name / address", placeholder="e.g. Banjara Hills, Hyderabad")
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude",  value=17.385044, format="%.6f")
        with col2:
            lon = st.number_input("Longitude", value=78.486671, format="%.6f")
        location_source = "manual"
        if not location_label:
            location_label = f"{lat:.5f}, {lon:.5f}"

    elif mode == "🗺️ Pick on Map":
        alert("Click anywhere on the map to drop a pin.", "info")
        default_lat = st.session_state.get("map_lat", 17.385044)
        default_lon = st.session_state.get("map_lon", 78.486671)
        m        = build_report_map([], center_lat=default_lat, center_lon=default_lon, zoom=13)
        map_data = st_folium(m, width=700, height=420, key="picker_map")

        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            st.session_state["map_lat"] = lat
            st.session_state["map_lon"] = lon
            location_source = "map_click"
            location_label  = f"{lat:.5f}, {lon:.5f}"
            st.success(f"📌 Pinned: {lat:.5f}, {lon:.5f}")
        elif "map_lat" in st.session_state:
            lat = st.session_state["map_lat"]
            lon = st.session_state["map_lon"]
            location_source = "map_click"
            location_label  = f"{lat:.5f}, {lon:.5f}"

    # ── Submit ────────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🚀 Submit Report", use_container_width=True, type="primary"):
        errors = []
        if not description or len(description.strip()) < 10:
            errors.append("Description must be at least 10 characters.")
        if lat is None or lon is None:
            errors.append("Location is required.")
        if not (-90 <= (lat or 0) <= 90) or not (-180 <= (lon or 0) <= 180):
            errors.append("Invalid coordinates.")

        if errors:
            for e in errors:
                alert(e, "error")
        else:
            with st.spinner("🤖 Running AI analysis and submitting…"):
                success, data = submit_report(
                    token, description, lat, lon,
                    location_label, image_b64,
                    location_source=location_source,
                    location_accuracy=location_accuracy,
                )

            if success:
                r = data["report"]
                st.balloons()
                st.markdown(
                    "<div style='background:#d1fae5;color:#065f46;padding:1rem;"
                    "border-radius:10px;font-weight:600;text-align:center'>"
                    "✅ Report submitted successfully!</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("#### 🤖 AI Analysis Result")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Category",   r["category"])
                with col2:
                    st.metric("Risk Score", f"{r['risk_score']}/100")
                with col3:
                    icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(r["priority"], "⚪")
                    st.metric("Priority",   f"{icon} {r['priority']}")

                # Full AI reasoning (FIX #1)
                if r.get("reasoning"):
                    st.info(f"**AI Reasoning:** {r['reasoning']}")
                if r.get("affected_population"):
                    st.write(f"👥 **Affected population:** {r['affected_population']}")
                if r.get("recommended_action"):
                    st.write(f"🔧 **Recommended action:** {r['recommended_action']}")

                st.markdown(
                    ai_badge(r.get("ai_powered", False)) +
                    f"&nbsp; Source: <code>{r.get('location_source','manual')}</code>",
                    unsafe_allow_html=True,
                )

                # Clear GPS state after submission
                for k in ["gps_lat", "gps_lon", "gps_acc", "map_lat", "map_lon"]:
                    st.session_state.pop(k, None)

            else:
                msg = data.get("error") or data.get("detail", "Submission failed.")
                alert(f"❌ {msg}", "error")