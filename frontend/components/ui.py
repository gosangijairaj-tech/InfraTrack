import streamlit as st

PRIORITY_COLORS = {"High": "#e63946", "Medium": "#f4a261", "Low": "#2a9d8f"}
STATUS_COLORS   = {"Pending": "#adb5bd", "In Progress": "#4895ef", "Resolved": "#2a9d8f"}


def priority_badge(p: str) -> str:
    c = PRIORITY_COLORS.get(p, "#888")
    return f"<span style='background:{c};color:#fff;padding:2px 12px;border-radius:12px;font-size:0.78rem;font-weight:600'>{p}</span>"


def status_badge(s: str) -> str:
    c = STATUS_COLORS.get(s, "#888")
    return f"<span style='background:{c};color:#fff;padding:2px 12px;border-radius:12px;font-size:0.78rem;font-weight:600'>{s}</span>"


def ai_badge(powered: bool) -> str:
    if powered:
        return "<span style='background:#7b2ff7;color:#fff;padding:2px 10px;border-radius:12px;font-size:0.75rem'>🤖 AI Scored</span>"
    return "<span style='background:#888;color:#fff;padding:2px 10px;border-radius:12px;font-size:0.75rem'>⚙️ Heuristic</span>"


def metric_card(label: str, value, color: str = "#0077B6", sub: str = "") -> str:
    return f"""
    <div style='background:{color};color:#fff;padding:1rem 1.2rem;
                border-radius:14px;text-align:center;height:90px;
                display:flex;flex-direction:column;justify-content:center'>
      <div style='font-size:1.7rem;font-weight:700;line-height:1'>{value}</div>
      <div style='font-size:0.85rem;margin-top:4px;opacity:0.9'>{label}</div>
      {"<div style='font-size:0.72rem;opacity:0.75'>" + sub + "</div>" if sub else ""}
    </div>"""


def section_header(title: str, icon: str = "") -> None:
    st.markdown(
        f"<h3 style='color:#0077B6;margin-top:1.5rem;margin-bottom:0.5rem'>{icon} {title}</h3>",
        unsafe_allow_html=True,
    )


def alert(msg: str, kind: str = "info") -> None:
    colors = {
        "info":    ("#dbeafe", "#1e40af"),
        "warning": ("#fef9c3", "#92400e"),
        "error":   ("#fee2e2", "#991b1b"),
        "success": ("#d1fae5", "#065f46"),
    }
    bg, fg = colors.get(kind, colors["info"])
    st.markdown(
        f"<div style='background:{bg};color:{fg};padding:10px 16px;"
        f"border-radius:8px;font-size:0.9rem;margin:6px 0'>{msg}</div>",
        unsafe_allow_html=True,
    )
