# import folium
# from folium.plugins import HeatMap


# def get_pin_color(priority: str) -> str:
#     return {"High": "red", "Medium": "orange", "Low": "green"}.get(priority, "blue")


# def build_report_map(reports: list, center_lat: float = 17.385, center_lon: float = 78.487, zoom: int = 12):
#     m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom,
#                    tiles="CartoDB positron")
#     for r in reports:
#         lat = r.get("latitude")
#         lon = r.get("longitude")
#         if lat is None or lon is None:
#             continue
#         color = get_pin_color(r.get("priority", "Low"))
#         popup_html = f"""
#         <div style='font-family:sans-serif; min-width:180px'>
#           <b>{r.get('category','N/A')}</b><br>
#           <span>Risk: <b>{r.get('risk_score','N/A')}</b>/100</span><br>
#           <span>Priority: <b style='color:{color}'>{r.get('priority','N/A')}</b></span><br>
#           <span>Status: {r.get('status','N/A')}</span><br>
#           <small>{r.get('description','')[:80]}...</small>
#         </div>
#         """
#         folium.Marker(
#             location=[lat, lon],
#             popup=folium.Popup(popup_html, max_width=220),
#             icon=folium.Icon(color=color, icon="info-sign"),
#         ).add_to(m)
#     return m


# def build_heatmap(reports: list, center_lat: float = 17.385, center_lon: float = 78.487):
#     m = folium.Map(location=[center_lat, center_lon], zoom_start=11,
#                    tiles="CartoDB dark_matter")
#     heat_data = [
#         [r["latitude"], r["longitude"], r.get("risk_score", 50) / 100]
#         for r in reports
#         if r.get("latitude") and r.get("longitude")
#     ]
#     if heat_data:
#         HeatMap(heat_data, radius=18, blur=15, max_zoom=13).add_to(m)
#     return m



import folium
from folium.plugins import HeatMap


# 🎨 Modern color palette
PRIORITY_COLORS = {
    "High": "#ff4d6d",
    "Medium": "#ff9f1c",
    "Low": "#2ec4b6"
}


def get_pin_color(priority: str) -> str:
    return PRIORITY_COLORS.get(priority, "#3a86ff")


# 🗺️ Main report map (upgraded UI)
def build_report_map(
    reports: list,
    center_lat: float = 17.385,
    center_lon: float = 78.487,
    zoom: int = 12
):
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB Voyager"  # 🔥 more modern than positron
    )

    for r in reports:
        lat = r.get("latitude")
        lon = r.get("longitude")

        if lat is None or lon is None:
            continue

        color = get_pin_color(r.get("priority", "Low"))

        # 🧾 Modern popup card
        popup_html = f"""
        <div style="
            font-family: 'Segoe UI', sans-serif;
            min-width:200px;
            padding:10px;
        ">
            <div style="font-weight:600;font-size:14px;margin-bottom:4px">
                {r.get('category','N/A')}
            </div>

            <div style="font-size:12px;color:#555;margin-bottom:6px">
                Risk Score:
                <b style="color:#111">{r.get('risk_score','N/A')}/100</b>
            </div>

            <div style="margin-bottom:6px">
                <span style="
                    background:{color};
                    color:white;
                    padding:2px 10px;
                    border-radius:999px;
                    font-size:11px;
                    font-weight:600;
                ">
                    {r.get('priority','N/A')}
                </span>
            </div>

            <div style="font-size:12px;margin-bottom:6px">
                Status: <b>{r.get('status','N/A')}</b>
            </div>

            <div style="font-size:11px;color:#666">
                {r.get('description','')[:100]}...
            </div>
        </div>
        """

        # 🔵 Custom circle marker (much cleaner than default pin)
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=260),
        ).add_to(m)

    return m


# 🔥 Heatmap (enhanced)
def build_heatmap(
    reports: list,
    center_lat: float = 17.385,
    center_lon: float = 78.487
):
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="CartoDB dark_matter"
    )

    heat_data = [
        [r["latitude"], r["longitude"], r.get("risk_score", 50) / 100]
        for r in reports
        if r.get("latitude") and r.get("longitude")
    ]

    if heat_data:
        HeatMap(
            heat_data,
            radius=20,
            blur=18,
            max_zoom=13,
            gradient={
                0.2: "#2ec4b6",
                0.4: "#90dbf4",
                0.6: "#ff9f1c",
                0.9: "#ff4d6d"
            }
        ).add_to(m)

    return m
