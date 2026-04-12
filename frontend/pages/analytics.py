import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.utils.api import get_analytics
from frontend.utils.map_utils import build_heatmap
from streamlit_folium import st_folium


def show():
    st.markdown("<h2 style='color:#0077B6'>🌍 Analytics Dashboard</h2>", unsafe_allow_html=True)
    token = st.session_state.get("token")
    role = st.session_state.get("role")
    if not token or role != "admin":
        st.error("Admin access required.")
        return

    code, data = get_analytics(token)
    if code != 200:
        st.error("Could not load analytics.")
        return

    cat_stats = data.get("category_stats", [])
    prio_stats = data.get("priority_stats", [])
    map_data = data.get("map_data", [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Reports by Category")
        if cat_stats:
            cat_df = pd.DataFrame(cat_stats).rename(columns={"_id": "Category", "count": "Count", "avg_risk": "Avg Risk"})
            fig = px.bar(cat_df, x="Category", y="Count", color="Avg Risk",
                         color_continuous_scale="RdYlGn_r",
                         title="Reports per Category")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#333")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Priority Distribution")
        if prio_stats:
            prio_df = pd.DataFrame(prio_stats).rename(columns={"_id": "Priority", "count": "Count"})
            color_map = {"High": "#e63946", "Medium": "#f4a261", "Low": "#2a9d8f"}
            fig2 = px.pie(prio_df, names="Priority", values="Count",
                          color="Priority", color_discrete_map=color_map,
                          title="Priority Breakdown")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 🔥 Risk Heatmap — High-Risk Zones")
    if map_data:
        hm = build_heatmap(map_data)
        st_folium(hm, width=720, height=450)
    else:
        st.info("No geolocation data available yet.")

    st.markdown("#### 📈 Average Risk Score by Category")
    if cat_stats:
        cat_df = pd.DataFrame(cat_stats).rename(columns={"_id": "Category", "avg_risk": "Avg Risk Score"})
        fig3 = go.Figure(go.Bar(
            x=cat_df["Category"],
            y=cat_df["Avg Risk Score"].round(1),
            marker_color=["#e63946", "#f4a261", "#2a9d8f", "#4895ef", "#a8dadc"],
        ))
        fig3.update_layout(title="Avg Risk Score per Category",
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, use_container_width=True)