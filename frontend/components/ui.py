# # import streamlit as st

# # PRIORITY_COLORS = {"High": "#e63946", "Medium": "#f4a261", "Low": "#2a9d8f"}
# # STATUS_COLORS   = {"Pending": "#adb5bd", "In Progress": "#4895ef", "Resolved": "#2a9d8f"}


# # def priority_badge(p: str) -> str:
# #     c = PRIORITY_COLORS.get(p, "#888")
# #     return f"<span style='background:{c};color:#fff;padding:2px 12px;border-radius:12px;font-size:0.78rem;font-weight:600'>{p}</span>"


# # def status_badge(s: str) -> str:
# #     c = STATUS_COLORS.get(s, "#888")
# #     return f"<span style='background:{c};color:#fff;padding:2px 12px;border-radius:12px;font-size:0.78rem;font-weight:600'>{s}</span>"


# # def ai_badge(powered: bool) -> str:
# #     if powered:
# #         return "<span style='background:#7b2ff7;color:#fff;padding:2px 10px;border-radius:12px;font-size:0.75rem'>🤖 AI Scored</span>"
# #     return "<span style='background:#888;color:#fff;padding:2px 10px;border-radius:12px;font-size:0.75rem'>⚙️ Heuristic</span>"


# # def metric_card(label: str, value, color: str = "#0077B6", sub: str = "") -> str:
# #     return f"""
# #     <div style='background:{color};color:#fff;padding:1rem 1.2rem;
# #                 border-radius:14px;text-align:center;height:90px;
# #                 display:flex;flex-direction:column;justify-content:center'>
# #       <div style='font-size:1.7rem;font-weight:700;line-height:1'>{value}</div>
# #       <div style='font-size:0.85rem;margin-top:4px;opacity:0.9'>{label}</div>
# #       {"<div style='font-size:0.72rem;opacity:0.75'>" + sub + "</div>" if sub else ""}
# #     </div>"""


# # def section_header(title: str, icon: str = "") -> None:
# #     st.markdown(
# #         f"<h3 style='color:#0077B6;margin-top:1.5rem;margin-bottom:0.5rem'>{icon} {title}</h3>",
# #         unsafe_allow_html=True,
# #     )


# # def alert(msg: str, kind: str = "info") -> None:
# #     colors = {
# #         "info":    ("#dbeafe", "#1e40af"),
# #         "warning": ("#fef9c3", "#92400e"),
# #         "error":   ("#fee2e2", "#991b1b"),
# #         "success": ("#d1fae5", "#065f46"),
# #     }
# #     bg, fg = colors.get(kind, colors["info"])
# #     st.markdown(
# #         f"<div style='background:{bg};color:{fg};padding:10px 16px;"
# #         f"border-radius:8px;font-size:0.9rem;margin:6px 0'>{msg}</div>",
# #         unsafe_allow_html=True,
# #     )

# import streamlit as st

# # 🎨 New color system (more unique)
# PRIORITY_COLORS = {
#     "High": "#ff4d6d",
#     "Medium": "#ff9f1c",
#     "Low": "#2ec4b6"
# }

# STATUS_COLORS = {
#     "Pending": "#6c757d",
#     "In Progress": "#3a86ff",
#     "Resolved": "#06d6a0"
# }


# # 🌈 Global Style Injection (call once in main)
# def apply_theme():
#     st.markdown("""
#     <style>
#         body {
#             background: linear-gradient(135deg, #0f172a, #1e293b);
#             color: #e5e7eb;
#         }

#         .block-container {
#             padding-top: 2rem;
#         }

#         /* Buttons */
#         .stButton > button {
#             border-radius: 25px;
#             padding: 8px 18px;
#             background: linear-gradient(135deg, #7b2ff7, #00c6ff);
#             color: white;
#             border: none;
#             transition: 0.2s ease;
#         }

#         .stButton > button:hover {
#             transform: scale(1.05);
#             box-shadow: 0 4px 20px rgba(0,0,0,0.3);
#         }

#         /* Inputs */
#         .stTextInput input {
#             border-radius: 12px !important;
#             padding: 10px !important;
#         }
#     </style>
#     """, unsafe_allow_html=True)


# # 🏷️ Badges (more modern)
# def priority_badge(p: str) -> str:
#     c = PRIORITY_COLORS.get(p, "#888")
#     return f"""
#     <span style='
#         background: {c};
#         color: white;
#         padding: 4px 14px;
#         border-radius: 999px;
#         font-size: 0.75rem;
#         font-weight: 600;
#         letter-spacing: 0.3px;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.2);
#     '>{p}</span>
#     """


# def status_badge(s: str) -> str:
#     c = STATUS_COLORS.get(s, "#888")
#     return f"""
#     <span style='
#         background: {c};
#         color: white;
#         padding: 4px 14px;
#         border-radius: 999px;
#         font-size: 0.75rem;
#         font-weight: 600;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.2);
#     '>{s}</span>
#     """


# def ai_badge(powered: bool) -> str:
#     if powered:
#         return """
#         <span style='
#             background: linear-gradient(135deg, #7b2ff7, #f107a3);
#             color: white;
#             padding: 4px 12px;
#             border-radius: 999px;
#             font-size: 0.72rem;
#             box-shadow: 0 2px 10px rgba(123,47,247,0.5);
#         '>🤖 AI Powered</span>
#         """
#     return """
#     <span style='
#         background: #6c757d;
#         color: white;
#         padding: 4px 12px;
#         border-radius: 999px;
#         font-size: 0.72rem;
#     '>⚙️ Manual</span>
#     """


# # 📊 Metric cards (glass style)
# def metric_card(label: str, value, color: str = "#3a86ff", sub: str = "") -> str:
#     return f"""
#     <div style='
#         backdrop-filter: blur(12px);
#         background: rgba(255,255,255,0.05);
#         border: 1px solid rgba(255,255,255,0.08);
#         border-radius: 16px;
#         padding: 16px;
#         text-align: center;
#         height: 100px;
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         box-shadow: 0 8px 30px rgba(0,0,0,0.3);
#     '>
#         <div style='font-size: 1.8rem; font-weight: 700; color:{color}'>{value}</div>
#         <div style='font-size: 0.85rem; opacity: 0.85'>{label}</div>
#         {"<div style='font-size:0.7rem;opacity:0.6'>" + sub + "</div>" if sub else ""}
#     </div>
#     """


# # 🧭 Section header (clean + modern)
# def section_header(title: str, icon: str = "") -> None:
#     st.markdown(
#         f"""
#         <div style='
#             display:flex;
#             align-items:center;
#             gap:10px;
#             margin-top:1.8rem;
#             margin-bottom:0.6rem;
#         '>
#             <h3 style='margin:0;font-weight:600;color:#e5e7eb'>
#                 {icon} {title}
#             </h3>
#             <div style='flex:1;height:1px;background:rgba(255,255,255,0.1)'></div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


# # 🚨 Alerts (cleaner UI)
# def alert(msg: str, kind: str = "info") -> None:
#     colors = {
#         "info":    ("rgba(59,130,246,0.15)", "#60a5fa"),
#         "warning": ("rgba(251,191,36,0.15)", "#fbbf24"),
#         "error":   ("rgba(239,68,68,0.15)", "#f87171"),
#         "success": ("rgba(16,185,129,0.15)", "#34d399"),
#     }

#     bg, fg = colors.get(kind, colors["info"])

#     st.markdown(
#         f"""
#         <div style='
#             background:{bg};
#             color:{fg};
#             padding:12px 16px;
#             border-radius:12px;
#             font-size:0.9rem;
#             margin:8px 0;
#             border:1px solid rgba(255,255,255,0.08);
#         '>
#             {msg}
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


import streamlit as st

# =========================
# 🎨 DESIGN TOKENS (SYSTEM)
# =========================
PRIORITY_COLORS = {
    "High": "#ff4d6d",
    "Medium": "#ff9f1c",
    "Low": "#2ec4b6"
}

STATUS_COLORS = {
    "Pending": "#6c757d",
    "In Progress": "#3a86ff",
    "Resolved": "#06d6a0"
}


# =========================
# 🌈 GLOBAL THEME
# =========================
def apply_theme():
    st.markdown("""
    <style>
        /* 🌌 App background */
        .stApp {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #e5e7eb;
        }

        /* 📦 Main container spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* 🔘 Buttons */
        .stButton > button {
            border-radius: 14px;
            padding: 8px 16px;
            background: linear-gradient(135deg, #7b2ff7, #00c6ff);
            color: white;
            border: none;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        }

        /* ✍️ Inputs */
        .stTextInput input,
        .stTextArea textarea {
            border-radius: 10px !important;
            padding: 10px !important;
        }

        /* 📍 Hide ugly Streamlit bits */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# =========================
# 🏷️ BADGES
# =========================
def priority_badge(p: str) -> str:
    c = PRIORITY_COLORS.get(p, "#888")
    return f"""
    <span style="
        background:{c};
        color:white;
        padding:4px 12px;
        border-radius:999px;
        font-size:0.75rem;
        font-weight:600;
        box-shadow:0 2px 8px rgba(0,0,0,0.2);
    ">{p}</span>
    """


def status_badge(s: str) -> str:
    c = STATUS_COLORS.get(s, "#888")
    return f"""
    <span style="
        background:{c};
        color:white;
        padding:4px 12px;
        border-radius:999px;
        font-size:0.75rem;
        font-weight:600;
        box-shadow:0 2px 8px rgba(0,0,0,0.2);
    ">{s}</span>
    """


def ai_badge(powered: bool) -> str:
    if powered:
        return """
        <span style="
            background: linear-gradient(135deg, #7b2ff7, #f107a3);
            color: white;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            box-shadow: 0 2px 10px rgba(123,47,247,0.4);
        ">🤖 AI Powered</span>
        """
    return """
    <span style="
        background: #6c757d;
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
    ">⚙️ Manual</span>
    """


# =========================
# 📊 METRIC CARD
# =========================
def metric_card(label: str, value, color: str = "#3a86ff", sub: str = "") -> str:
    return f"""
    <div style="
        backdrop-filter: blur(14px);
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        height: 105px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    ">
        <div style="font-size:1.8rem;font-weight:700;color:{color}">
            {value}
        </div>
        <div style="font-size:0.85rem;opacity:0.85">
            {label}
        </div>
        {"<div style='font-size:0.7rem;opacity:0.6'>" + sub + "</div>" if sub else ""}
    </div>
    """


# =========================
# 🧭 SECTION HEADER
# =========================
def section_header(title: str, icon: str = "") -> None:
    st.markdown(f"""
    <div style="
        display:flex;
        align-items:center;
        gap:10px;
        margin-top:1.6rem;
        margin-bottom:0.8rem;
    ">
        <h3 style="margin:0;color:#e5e7eb;font-weight:600">
            {icon} {title}
        </h3>
        <div style="flex:1;height:1px;background:rgba(255,255,255,0.08)"></div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🚨 ALERT SYSTEM
# =========================
def alert(msg: str, kind: str = "info") -> None:
    colors = {
        "info":    ("rgba(59,130,246,0.15)", "#60a5fa"),
        "warning": ("rgba(251,191,36,0.15)", "#fbbf24"),
        "error":   ("rgba(239,68,68,0.15)", "#f87171"),
        "success": ("rgba(16,185,129,0.15)", "#34d399"),
    }

    bg, fg = colors.get(kind, colors["info"])

    st.markdown(f"""
    <div style="
        background:{bg};
        color:{fg};
        padding:12px 14px;
        border-radius:12px;
        font-size:0.9rem;
        margin:8px 0;
        border:1px solid rgba(255,255,255,0.08);
    ">
        {msg}
    </div>
    """, unsafe_allow_html=True)