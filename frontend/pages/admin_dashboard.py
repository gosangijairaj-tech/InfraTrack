import streamlit as st
import pandas as pd
from frontend.utils.api import get_all_reports, update_report_status, get_admin_stats
from frontend.utils.map_utils import build_report_map
from streamlit_folium import st_folium


def show():
    st.markdown("<h2 style='color:#0077B6'>🛠️ Admin Dashboard</h2>", unsafe_allow_html=True)
    token = st.session_state.get("token")
    role = st.session_state.get("role")
    if not token or role != "admin":
        st.error("Admin access required.")
        return

    # Stats
    _, stats = get_admin_stats(token)
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("Total", stats.get("total", 0), "#0077B6"),
        ("Pending", stats.get("pending", 0), "#adb5bd"),
        ("In Progress", stats.get("in_progress", 0), "#4895ef"),
        ("Resolved", stats.get("resolved", 0), "#2a9d8f"),
        ("High Risk", stats.get("high_risk", 0), "#e63946"),
    ]
    for col, (label, val, color) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.markdown(f"""<div style='background:{color};color:#fff;padding:0.8rem;border-radius:12px;text-align:center'>
                <h3>{val}</h3><small>{label}</small></div>""", unsafe_allow_html=True)

    st.markdown("---")

    code, data = get_all_reports(token)
    if code != 200 or not data:
        st.info("No reports found.")
        return

    df = pd.DataFrame(data)

    # Filters
    st.markdown("### 🔍 Filter Reports")
    col1, col2, col3 = st.columns(3)
    with col1:
        cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", cats)
    with col2:
        prios = ["All", "High", "Medium", "Low"]
        sel_prio = st.selectbox("Priority", prios)
    with col3:
        statuses = ["All", "Pending", "In Progress", "Resolved"]
        sel_status = st.selectbox("Status", statuses)

    filtered = df.copy()
    if sel_cat != "All":
        filtered = filtered[filtered["category"] == sel_cat]
    if sel_prio != "All":
        filtered = filtered[filtered["priority"] == sel_prio]
    if sel_status != "All":
        filtered = filtered[filtered["status"] == sel_status]

    st.markdown(f"### 🗺️ Filtered Reports Map ({len(filtered)} reports)")
    m = build_report_map(filtered.to_dict("records"))
    st_folium(m, width=700, height=400)

    st.markdown("### 📋 All Reports")
    for _, row in filtered.sort_values("risk_score", ascending=False).iterrows():
        r = row.to_dict()
        with st.expander(f"[{r.get('category','N/A')}] {r.get('username','?')} — Risk {r.get('risk_score','?')}/100"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**User:** {r.get('username','')}")
                st.write(f"**Description:** {r.get('description','')}")
                st.write(f"**Location:** {r.get('location_label', '')}")
                st.write(f"**Submitted:** {str(r.get('created_at',''))[:10]}")
            with col2:
                new_status = st.selectbox(
                    "Update Status",
                    ["Pending", "In Progress", "Resolved"],
                    index=["Pending", "In Progress", "Resolved"].index(r.get("status", "Pending")),
                    key=f"status_{r['_id']}"
                )
                if st.button("Update", key=f"btn_{r['_id']}"):
                    scode, sdata = update_report_status(token, r["_id"], new_status)
                    if scode == 200:
                        st.success("Status updated!")
                        st.rerun()
                    else:
                        st.error("Update failed")