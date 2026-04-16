import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from frontend.utils.api import get_analytics, get_admin_stats
from frontend.utils.map_utils import build_heatmap
from frontend.components.ui import section_header, alert, metric_card
from streamlit_folium import st_folium

REFRESH_INTERVAL = 30


def show():
    token = st.session_state.get("token")
    if not token or st.session_state.get("role") not in ["admin", "authority"]:
        alert("Access denied.", "error")
        return

    st.markdown("<h2 style='color:#0077B6'>🌍 Analytics Dashboard</h2>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        last_ts = st.session_state.get("analytics_last_refresh", time.time())
        st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S', time.localtime(last_ts))}")
    with c2:
        auto_on = st.toggle("Auto-refresh", value=True, key="analytics_auto")
    with c3:
        if st.button("↺ Refresh Now", use_container_width=True):
            st.session_state["analytics_last_refresh"] = time.time()
            st.rerun()

    with st.spinner("Loading analytics…"):
        ok,  data  = get_analytics(token)
        ok2, stats = get_admin_stats(token)

    if not ok:
        alert(data.get("error", "Cannot load analytics."), "error")
        return

    cat_stats  = data.get("category_stats", [])
    prio_stats = data.get("priority_stats", [])
    stat_stats = data.get("status_stats",   [])
    map_data   = data.get("map_data",       [])

    section_header("Key Metrics", "📊")
    kcols = st.columns(4)
    kpi = [
        ("Total Reports", stats.get("total",     0), "#0077B6"),
        ("High Risk",     stats.get("high_risk",  0), "#e63946"),
        ("AI Scored",     stats.get("ai_scored",  0), "#7b2ff7"),
        ("Resolved",      stats.get("resolved",   0), "#2a9d8f"),
    ]
    for col, (lbl, val, clr) in zip(kcols, kpi):
        with col:
            st.markdown(metric_card(lbl, val, clr), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Reports by Category", "📂")
        if cat_stats:
            cdf = pd.DataFrame(cat_stats).rename(
                columns={"_id": "Category", "count": "Reports", "avg_risk": "Avg Risk"}
            )
            cdf["Avg Risk"] = cdf["Avg Risk"].round(1)
            fig = px.bar(cdf, x="Category", y="Reports", color="Avg Risk",
                         color_continuous_scale="RdYlGn_r", text="Reports")
            fig.update_traces(textposition="outside")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#1e293b", margin=dict(t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            alert("No category data yet.", "info")

    with col2:
        section_header("Priority Distribution", "🎯")
        if prio_stats:
            pdf = pd.DataFrame(prio_stats).rename(columns={"_id": "Priority", "count": "Count"})
            color_map = {"High": "#e63946", "Medium": "#f4a261", "Low": "#2a9d8f"}
            fig2 = px.pie(pdf, names="Priority", values="Count",
                          color="Priority", color_discrete_map=color_map, hole=0.4)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            alert("No priority data yet.", "info")

    col3, col4 = st.columns(2)
    with col3:
        section_header("Status Breakdown", "📋")
        if stat_stats:
            sdf = pd.DataFrame(stat_stats).rename(columns={"_id": "Status", "count": "Count"})
            sc_map = {"Pending": "#94a3b8", "In Progress": "#4895ef", "Resolved": "#2a9d8f"}
            fig3 = px.bar(sdf, x="Status", y="Count", color="Status",
                          color_discrete_map=sc_map, text="Count")
            fig3.update_traces(textposition="outside")
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               showlegend=False, margin=dict(t=20, b=0))
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        section_header("Avg Risk Score by Category", "⚡")
        if cat_stats:
            cdf2 = pd.DataFrame(cat_stats).rename(
                columns={"_id": "Category", "avg_risk": "Avg Risk"}
            ).sort_values("Avg Risk", ascending=True)
            fig4 = go.Figure(go.Bar(
                x=cdf2["Avg Risk"].round(1), y=cdf2["Category"],
                orientation="h",
                marker_color=["#e63946" if v > 70 else "#f4a261" if v > 30 else "#2a9d8f"
                               for v in cdf2["Avg Risk"]],
                text=cdf2["Avg Risk"].round(1), textposition="outside",
            ))
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               xaxis_range=[0, 100], margin=dict(t=20, b=0))
            st.plotly_chart(fig4, use_container_width=True)

    if map_data:
        ai_count  = sum(1 for r in map_data if r.get("ai_powered"))
        heu_count = len(map_data) - ai_count
        section_header("AI Scoring Coverage", "🤖")
        fig5 = px.pie(
            names=["Real AI (Claude)", "Heuristic fallback"],
            values=[ai_count, heu_count],
            color_discrete_sequence=["#7b2ff7", "#94a3b8"], hole=0.5,
        )
        fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20))
        st.plotly_chart(fig5, use_container_width=True)

    section_header("Risk Heatmap — High-Risk Zones", "🔥")
    valid = [r for r in map_data if r.get("latitude") and r.get("longitude")]
    if valid:
        center_lat = sum(r["latitude"]  for r in valid) / len(valid)
        center_lon = sum(r["longitude"] for r in valid) / len(valid)
        hm = build_heatmap(valid, center_lat=center_lat, center_lon=center_lon)
        st_folium(hm, width=720, height=460)
    else:
        alert("Submit reports first to see the heatmap.", "info")

    if auto_on:
        remaining = max(0, REFRESH_INTERVAL - (time.time() - st.session_state.get("analytics_last_refresh", 0)))
        st.caption(f"⏱ Next auto-refresh in {int(remaining)}s")
        st.session_state["analytics_last_refresh"] = st.session_state.get("analytics_last_refresh", time.time())
        time.sleep(1)
        st.rerun()
