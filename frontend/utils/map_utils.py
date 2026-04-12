import folium
from folium.plugins import HeatMap


def get_pin_color(priority: str) -> str:
    return {"High": "red", "Medium": "orange", "Low": "green"}.get(priority, "blue")


def build_report_map(reports: list, center_lat: float = 17.385, center_lon: float = 78.487, zoom: int = 12):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom,
                   tiles="CartoDB positron")
    for r in reports:
        lat = r.get("latitude")
        lon = r.get("longitude")
        if lat is None or lon is None:
            continue
        color = get_pin_color(r.get("priority", "Low"))
        popup_html = f"""
        <div style='font-family:sans-serif; min-width:180px'>
          <b>{r.get('category','N/A')}</b><br>
          <span>Risk: <b>{r.get('risk_score','N/A')}</b>/100</span><br>
          <span>Priority: <b style='color:{color}'>{r.get('priority','N/A')}</b></span><br>
          <span>Status: {r.get('status','N/A')}</span><br>
          <small>{r.get('description','')[:80]}...</small>
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=220),
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)
    return m


def build_heatmap(reports: list, center_lat: float = 17.385, center_lon: float = 78.487):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11,
                   tiles="CartoDB dark_matter")
    heat_data = [
        [r["latitude"], r["longitude"], r.get("risk_score", 50) / 100]
        for r in reports
        if r.get("latitude") and r.get("longitude")
    ]
    if heat_data:
        HeatMap(heat_data, radius=18, blur=15, max_zoom=13).add_to(m)
    return m