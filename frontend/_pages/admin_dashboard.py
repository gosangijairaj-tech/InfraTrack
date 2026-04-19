import time
import base64
import streamlit as st
import pandas as pd
from frontend.utils.api import (
    get_all_reports, update_report_status, get_admin_stats,
    get_admin_config, update_thresholds, update_category_config,
)
from frontend.utils.map_utils import build_report_map
from frontend.components.ui import (
    priority_badge, status_badge, ai_badge,
    metric_card, section_header, alert,
)
from streamlit_folium import st_folium
REFRESH_INTERVAL = 20


def show():
    token = st.session_state.get("token")
    if not token or st.session_state.get("role") != "admin":
        alert("Admin access required. Change your role to 'admin' in MongoDB Atlas.", "error")
        return

    st.markdown("<h2 style='color:#0077B6'>🛠️ Admin Dashboard</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        last_ts = st.session_state.get("admin_last_refresh", time.time())
        st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S', time.localtime(last_ts))}")
    with col2:
        auto_on = st.toggle("Auto-refresh", value=True, key="admin_auto_refresh")
    with col3:
        if st.button("↺ Refresh Now", use_container_width=True):
            st.session_state["admin_last_refresh"] = time.time()
            st.session_state["admin_prev_count"] = st.session_state.get("admin_report_count", 0)
            st.rerun()

    ok, stats = get_admin_stats(token)
    if not ok:
        alert(stats.get("error", "Could not load stats."), "error")
        return

    curr_count = stats.get("total", 0)
    prev_count = st.session_state.get("admin_prev_count", curr_count)
    new_count  = curr_count - prev_count
    if new_count > 0:
        st.markdown(
            f"<div style='background:#e63946;color:#fff;padding:8px 16px;"
            f"border-radius:8px;font-weight:700;text-align:center'>"
            f"🔔 {new_count} new report{'s' if new_count > 1 else ''} since last refresh!</div>",
            unsafe_allow_html=True,
        )
    st.session_state["admin_report_count"] = curr_count

    cols = st.columns(5)
    cards = [
        ("Total",       stats.get("total",       0), "#0077B6"),
        ("Pending",     stats.get("pending",      0), "#94a3b8"),
        ("In Progress", stats.get("in_progress",  0), "#4895ef"),
        ("Resolved",    stats.get("resolved",     0), "#2a9d8f"),
        ("High Risk",   stats.get("high_risk",    0), "#e63946"),
    ]
    for col, (lbl, val, clr) in zip(cols, cards):
        with col:
            st.markdown(metric_card(lbl, val, clr), unsafe_allow_html=True)

    ai_pct = round(stats.get("ai_scored", 0) / max(curr_count, 1) * 100)
    st.caption(f"🤖 {stats.get('ai_scored', 0)} of {curr_count} reports scored by real AI ({ai_pct}%)")

    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Manage Reports", "⚙️ System Config"])

    with tab1:
        ok2, rdata = get_all_reports(token)
        if not ok2:
            alert(rdata.get("error", "Cannot load reports."), "error")
            return

        reports = rdata.get("reports", [])
        if not reports:
            alert("No reports submitted yet.", "info")
            return

        df = pd.DataFrame(reports)

        section_header("Filter Reports", "🔍")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
            sel_cat = st.selectbox("Category", cats)
        with fc2:
            sel_prio = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
        with fc3:
            sel_status = st.selectbox("Status", ["All", "Pending", "In Progress", "Resolved"])

        filtered = df.copy()
        if sel_cat    != "All": filtered = filtered[filtered["category"] == sel_cat]
        if sel_prio   != "All": filtered = filtered[filtered["priority"] == sel_prio]
        if sel_status != "All": filtered = filtered[filtered["status"]   == sel_status]

        section_header(f"Map ({len(filtered)} reports)", "🗺️")
        valid = [r for r in filtered.to_dict("records") if r.get("latitude") and r.get("longitude")]
        if valid:
            m = build_report_map(valid)
            st_folium(m, width=700, height=420)
        else:
            alert("No geolocated reports match the filter.", "info")

        section_header("Report List", "📋")
        for _, row in filtered.sort_values("risk_score", ascending=False).iterrows():
            r = row.to_dict()
            label = (
                f"[{r.get('category','?')}]  "
                f"{r.get('username','?')}  —  "
                f"Risk {r.get('risk_score','?')}/100  |  "
                f"{str(r.get('created_at',''))[:10]}"
            )
            with st.expander(label):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**User:** {r.get('username','')}")
                    st.write(f"**Description:** {r.get('description','')}")
                    loc = r.get("location_label") or "{}, {}".format(
                        r.get("latitude", "?"), r.get("longitude", "?")
                    )
                    st.write(f"**Location:** {loc}")
                    src_map = {"gps": "📡 GPS", "manual": "✏️ Manual", "map_click": "🗺️ Map click"}
                    st.write(f"**Location source:** {src_map.get(r.get('location_source',''), 'Unknown')}")
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
                            st.caption("Image error")
                    new_s = st.selectbox(
                        "Update status",
                        ["Pending", "In Progress", "Resolved"],
                        index=["Pending", "In Progress", "Resolved"].index(r.get("status", "Pending")),
                        key=f"sel_{r['_id']}",
                    )
                    if st.button("Update", key=f"upd_{r['_id']}", use_container_width=True):
                        ok3, res = update_report_status(token, r["_id"], new_s)
                        if ok3:
                            st.success("✅ Updated!")
                            st.rerun()
                        else:
                            alert(res.get("error", "Update failed."), "error")

    with tab2:
        st.markdown("### ⚙️ Live System Configuration")
        ok_cfg, cfg = get_admin_config(token)
        if not ok_cfg:
            alert(cfg.get("error", "Cannot load config."), "error")
            return

        section_header("Priority Thresholds", "🎯")
        thresh = cfg.get("thresholds", {})
        tc1, tc2 = st.columns(2)
        with tc1:
            new_low = st.number_input(
                "Low → Medium boundary",
                min_value=1, max_value=69,
                value=int(thresh.get("low_max", 30)),
            )
        with tc2:
            new_med = st.number_input(
                "Medium → High boundary",
                min_value=2, max_value=99,
                value=int(thresh.get("medium_max", 70)),
            )
        if st.button("💾 Save Thresholds", type="primary"):
            if new_low >= new_med:
                alert("Low boundary must be less than Medium boundary.", "error")
            else:
                ok_t, td = update_thresholds(token, new_low, new_med)
                if ok_t:
                    alert("✅ Thresholds updated.", "success")
                    st.rerun()
                else:
                    alert(td.get("error", "Update failed."), "error")

        section_header("Category Base Scores", "📂")
        for cat in cfg.get("categories", []):
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            with cc1:
                st.write(f"{cat.get('icon','')} **{cat['name']}**")
            with cc2:
                new_bs = st.slider(
                    "Base score", 0, 100,
                    value=int(cat.get("base_score", 35)),
                    key=f"bs_{cat['name']}",
                    label_visibility="collapsed",
                )
            with cc3:
                if st.button("Save", key=f"save_{cat['name']}"):
                    ok_c, cd = update_category_config(token, cat["name"], new_bs, cat.get("active", True))
                    if ok_c:
                        alert(f"✅ {cat['name']} updated.", "success")
                    else:
                        alert(cd.get("error", "Failed."), "error")

    if auto_on:
        remaining = max(0, REFRESH_INTERVAL - (time.time() - st.session_state.get("admin_last_refresh", 0)))
        st.caption(f"⏱ Next auto-refresh in {int(remaining)}s")
        st.session_state["admin_last_refresh"] = st.session_state.get("admin_last_refresh", time.time())
        time.sleep(1)
        st.rerun()
