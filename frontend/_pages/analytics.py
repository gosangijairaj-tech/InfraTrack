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
    st.markdown("""
    <style>

    .main-title{
        font-size:2.2rem;
        font-weight:800;
        background: linear-gradient(90deg,#00c6ff,#0072ff,#7b2ff7);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:0.3rem;
    }

    .glass-box{
        background: rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.08);
        border-radius:18px;
        padding:1rem;
        backdrop-filter: blur(10px);
        box-shadow:0 8px 24px rgba(0,0,0,0.25);
    }

    div[data-testid="stMetric"]{
        background: rgba(255,255,255,0.04);
        border-radius:16px;
        padding:12px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>🌍 Analytics Dashboard</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2,1,1])

    with c1:
        last_ts = st.session_state.get("analytics_last_refresh", time.time())
        st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S', time.localtime(last_ts))}")

    with c2:
        auto_on = st.toggle("Auto-refresh", value=True, key="analytics_auto")

    with c3:
        if st.button("↺ Refresh Now", use_container_width=True):
            st.session_state["analytics_last_refresh"] = time.time()
            st.rerun()
    with st.spinner("Loading analytics..."):
        ok, data = get_analytics(token)
        ok2, stats = get_admin_stats(token)

    if not ok:
        alert(data.get("error", "Cannot load analytics."), "error")
        return

    cat_stats  = data.get("category_stats", [])
    prio_stats = data.get("priority_stats", [])
    stat_stats = data.get("status_stats", [])
    map_data   = data.get("map_data", [])

    # ---------- KPI ----------
    section_header("Key Metrics", "📊")

    cols = st.columns(4)

    cards = [
        ("Total Reports", stats.get("total",0), "#00c6ff"),
        ("High Risk", stats.get("high_risk",0), "#ff4b4b"),
        ("AI Scored", stats.get("ai_scored",0), "#7b2ff7"),
        ("Resolved", stats.get("resolved",0), "#00d084"),
    ]

    for col, (label,val,color) in zip(cols, cards):
        with col:
            st.markdown(metric_card(label, val, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_header("Reports by Category", "📂")

        if cat_stats:
            cdf = pd.DataFrame(cat_stats).rename(
                columns={"_id":"Category","count":"Reports","avg_risk":"Avg Risk"}
            )

            fig = px.bar(
                cdf,
                x="Category",
                y="Reports",
                color="Avg Risk",
                text="Reports",
                color_continuous_scale=[
                    "#00d084",
                    "#f9c74f",
                    "#ff4b4b"
                ]
            )

            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
                marker_opacity=0.95
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font_color="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                margin=dict(t=20,b=0,l=0,r=0)
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Priority Distribution", "🎯")

        if prio_stats:
            pdf = pd.DataFrame(prio_stats).rename(
                columns={"_id":"Priority","count":"Count"}
            )

            fig2 = px.pie(
                pdf,
                names="Priority",
                values="Count",
                hole=0.58,
                color="Priority",
                color_discrete_map={
                    "High":"#ff4b4b",
                    "Medium":"#ffb703",
                    "Low":"#00d084"
                }
            )

            fig2.update_traces(
                textinfo="percent+label",
                pull=[0.05,0.02,0]
            )

            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                margin=dict(t=20,b=0,l=0,r=0)
            )

            st.plotly_chart(fig2, use_container_width=True)
    col3, col4 = st.columns(2)

    with col3:
        section_header("Status Breakdown", "📋")

        if stat_stats:
            sdf = pd.DataFrame(stat_stats).rename(
                columns={"_id":"Status","count":"Count"}
            )

            fig3 = px.bar(
                sdf,
                x="Status",
                y="Count",
                text="Count",
                color="Status",
                color_discrete_map={
                    "Pending":"#94a3b8",
                    "In Progress":"#00c6ff",
                    "Resolved":"#00d084"
                }
            )

            fig3.update_traces(textposition="outside")

            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font_color="white",
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                margin=dict(t=20,b=0,l=0,r=0)
            )

            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        section_header("Avg Risk Score", "⚡")

        if cat_stats:
            cdf2 = pd.DataFrame(cat_stats).rename(
                columns={"_id":"Category","avg_risk":"Risk"}
            ).sort_values("Risk")

            fig4 = go.Figure()

            fig4.add_trace(go.Bar(
                x=cdf2["Risk"],
                y=cdf2["Category"],
                orientation="h",
                text=cdf2["Risk"].round(1),
                textposition="outside",
                marker=dict(
                    color=cdf2["Risk"],
                    colorscale="Turbo",
                    line=dict(width=0)
                )
            ))

            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font_color="white",
                xaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.08)"),
                margin=dict(t=20,b=0,l=0,r=0)
            )

            st.plotly_chart(fig4, use_container_width=True)

    if map_data:
        ai_count  = sum(1 for r in map_data if r.get("ai_powered"))
        heu_count = len(map_data) - ai_count

        section_header("AI Scoring Coverage", "🤖")

        fig5 = px.pie(
            names=["Real AI", "Fallback"],
            values=[ai_count, heu_count],
            hole=0.62,
            color_discrete_sequence=["#7b2ff7","#64748b"]
        )

        fig5.update_traces(textinfo="percent+label")

        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(t=20,b=0,l=0,r=0)
        )

        st.plotly_chart(fig5, use_container_width=True)
    section_header("Risk Heatmap — High Risk Zones", "🔥")

    valid = [r for r in map_data if r.get("latitude") and r.get("longitude")]

    if valid:
        center_lat = sum(r["latitude"] for r in valid) / len(valid)
        center_lon = sum(r["longitude"] for r in valid) / len(valid)

        hm = build_heatmap(valid, center_lat=center_lat, center_lon=center_lon)

        st_folium(hm, width=None, height=520)

    else:
        alert("Submit reports first to see heatmap.", "info")

    if auto_on:
        remaining = max(
            0,
            REFRESH_INTERVAL - (
                time.time() -
                st.session_state.get("analytics_last_refresh",0)
            )
        )
        st.caption(f"⏱ Next auto-refresh in {int(remaining)}s")
        st.session_state["analytics_last_refresh"] = time.time()
        time.sleep(1)
        st.rerun()