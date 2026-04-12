import streamlit as st
import base64
from PIL import Image
import io
from frontend.utils.api import submit_report
from frontend.utils.map_utils import build_report_map
from streamlit_folium import st_folium


def show():
    st.markdown("<h2 style='color:#0077B6'>📍 Submit Infrastructure Report</h2>", unsafe_allow_html=True)

    token = st.session_state.get("token")
    if not token:
        st.warning("Please log in first.")
        return

    st.markdown("### 📸 Upload Photo")
    uploaded_file = st.file_uploader("Upload image of the issue", type=["jpg", "jpeg", "png"])
    image_b64 = ""
    if uploaded_file:
        img = Image.open(uploaded_file)
        img.thumbnail((800, 800))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        st.image(img, caption="Uploaded Image", use_column_width=True)

    st.markdown("### 📝 Description")
    description = st.text_area(
        "Describe the issue",
        placeholder="e.g. Large pothole on main road causing vehicle damage...",
        height=120
    )

    st.markdown("### 📍 Location")
    location_mode = st.radio("How would you like to provide location?",
                              ["Use My GPS Coordinates", "Enter Manually", "Pick on Map"],
                              horizontal=True)

    lat, lon, location_label = None, None, ""

    if location_mode == "Use My GPS Coordinates":
        st.info("Enter your current GPS coordinates (you can get them from Google Maps or your phone).")
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=17.385, format="%.6f")
        with col2:
            lon = st.number_input("Longitude", value=78.487, format="%.6f")
        location_label = f"{lat:.4f}, {lon:.4f}"

    elif location_mode == "Enter Manually":
        location_label = st.text_input("Location name / address", placeholder="e.g. Banjara Hills, Hyderabad")
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=17.385, format="%.6f")
        with col2:
            lon = st.number_input("Longitude", value=78.487, format="%.6f")

    elif location_mode == "Pick on Map":
        st.info("Click anywhere on the map to set the location. Then copy the coordinates.")
        m = build_report_map([], center_lat=17.385, center_lon=78.487, zoom=12)
        map_data = st_folium(m, width=700, height=400)
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            location_label = f"{lat:.4f}, {lon:.4f}"
            st.success(f"Selected: {lat:.4f}, {lon:.4f}")
        else:
            lat, lon = 17.385, 78.487

    st.markdown("---")
    if st.button("🚀 Submit Report", use_container_width=True, type="primary"):
        if not description:
            st.error("Please provide a description.")
        elif lat is None or lon is None:
            st.error("Please provide a valid location.")
        else:
            with st.spinner("Analysing issue and submitting..."):
                code, data = submit_report(token, description, lat, lon, location_label, image_b64)
            if code == 200:
                report = data["report"]
                st.success("✅ Report submitted successfully!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Category", report["category"])
                with col2:
                    st.metric("Risk Score", f"{report['risk_score']}/100")
                with col3:
                    color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(report["priority"], "⚪")
                    st.metric("Priority", f"{color} {report['priority']}")
            else:
                st.error(data.get("detail", "Submission failed"))