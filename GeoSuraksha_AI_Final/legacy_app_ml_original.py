import math
import random
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import os
import joblib

# =========================================================================
# DESIGN TOKENS & PALETTE
# =========================================================================
C = {
    "bg": "#0A0E14",
    "panel": "#111823",
    "panel2": "#0D131C",
    "border": "#1E2A38",
    "borderLight": "#2A3847",
    "text": "#E6EBF1",
    "textDim": "#8C99AB",
    "textFaint": "#5B6779",
    "accent": "#2DD4BF",
    "accentDim": "#0F3D3A",
    "low": "#3FB950",
    "moderate": "#E3B341",
    "high": "#F0883E",
    "critical": "#F85149",
}

RISK_META = {
    "LOW": {"color": C["low"], "label": "Low"},
    "MODERATE": {"color": C["moderate"], "label": "Moderate"},
    "HIGH": {"color": C["high"], "label": "High"},
    "CRITICAL": {"color": C["critical"], "label": "Critical"},
}


def level_from_score(score: float) -> str:
    if score >= 76:
        return "CRITICAL"
    if score >= 51:
        return "HIGH"
    if score >= 26:
        return "MODERATE"
    return "LOW"


# =========================================================================
# DATA MODELS & INITIAL DATA
# =========================================================================
STATE_LABELS = [
    {"name": "Sikkim", "lat": 27.6, "lon": 88.5},
    {"name": "Arunachal Pradesh", "lat": 28.2, "lon": 94.7},
    {"name": "Assam", "lat": 26.3, "lon": 92.9},
    {"name": "Nagaland", "lat": 26.0, "lon": 94.5},
    {"name": "Manipur", "lat": 24.7, "lon": 93.9},
    {"name": "Meghalaya", "lat": 25.5, "lon": 91.3},
    {"name": "Mizoram", "lat": 23.3, "lon": 92.8},
    {"name": "Tripura", "lat": 23.8, "lon": 91.5},
]

RAW_HOTSPOTS = [
    {
        "id": "H01",
        "location": "NH-10 Corridor, Sikkim",
        "state": "Sikkim",
        "lat": 27.33,
        "lon": 88.62,
        "rainfall24h": 142,
        "rainfall72h": 318,
        "soilMoisture": 91,
        "slope": 42,
        "elevation": 1820,
        "ndvi": 0.31,
        "historicalDensity": 78,
        "riskScore": 87,
        "confidence": 93,
        "updatedAt": "3 min ago",
    },
    {
        "id": "H02",
        "location": "Mangan–Chungthang Road, Sikkim",
        "state": "Sikkim",
        "lat": 27.52,
        "lon": 88.53,
        "rainfall24h": 118,
        "rainfall72h": 276,
        "soilMoisture": 84,
        "slope": 39,
        "elevation": 1640,
        "ndvi": 0.35,
        "historicalDensity": 64,
        "riskScore": 74,
        "confidence": 88,
        "updatedAt": "3 min ago",
    },
    {
        "id": "H03",
        "location": "Tawang–Bomdila Highway, Arunachal Pradesh",
        "state": "Arunachal Pradesh",
        "lat": 27.59,
        "lon": 92.40,
        "rainfall24h": 96,
        "rainfall72h": 210,
        "soilMoisture": 76,
        "slope": 44,
        "elevation": 2210,
        "ndvi": 0.28,
        "historicalDensity": 71,
        "riskScore": 69,
        "confidence": 85,
        "updatedAt": "6 min ago",
    },
    {
        "id": "H04",
        "location": "Along–Pasighat Road, Arunachal Pradesh",
        "state": "Arunachal Pradesh",
        "lat": 28.16,
        "lon": 95.33,
        "rainfall24h": 54,
        "rainfall72h": 132,
        "soilMoisture": 58,
        "slope": 27,
        "elevation": 480,
        "ndvi": 0.52,
        "historicalDensity": 38,
        "riskScore": 41,
        "confidence": 79,
        "updatedAt": "9 min ago",
    },
    {
        "id": "H05",
        "location": "Cherrapunji–Sohra Escarpment, Meghalaya",
        "state": "Meghalaya",
        "lat": 25.28,
        "lon": 91.72,
        "rainfall24h": 165,
        "rainfall72h": 402,
        "soilMoisture": 89,
        "slope": 51,
        "elevation": 1290,
        "ndvi": 0.40,
        "historicalDensity": 82,
        "riskScore": 91,
        "confidence": 95,
        "updatedAt": "2 min ago",
    },
    {
        "id": "H06",
        "location": "Shillong–Dawki Road, Meghalaya",
        "state": "Meghalaya",
        "lat": 25.32,
        "lon": 91.87,
        "rainfall24h": 88,
        "rainfall72h": 190,
        "soilMoisture": 67,
        "slope": 33,
        "elevation": 990,
        "ndvi": 0.46,
        "historicalDensity": 45,
        "riskScore": 52,
        "confidence": 82,
        "updatedAt": "5 min ago",
    },
    {
        "id": "H07",
        "location": "Haflong Hill Section, Assam",
        "state": "Assam",
        "lat": 25.16,
        "lon": 93.02,
        "rainfall24h": 71,
        "rainfall72h": 158,
        "soilMoisture": 62,
        "slope": 29,
        "elevation": 680,
        "ndvi": 0.49,
        "historicalDensity": 40,
        "riskScore": 47,
        "confidence": 80,
        "updatedAt": "7 min ago",
    },
    {
        "id": "H08",
        "location": "Kohima–Dimapur NH-29, Nagaland",
        "state": "Nagaland",
        "lat": 25.78,
        "lon": 94.00,
        "rainfall24h": 63,
        "rainfall72h": 141,
        "soilMoisture": 59,
        "slope": 31,
        "elevation": 1150,
        "ndvi": 0.44,
        "historicalDensity": 35,
        "riskScore": 39,
        "confidence": 77,
        "updatedAt": "11 min ago",
    },
    {
        "id": "H09",
        "location": "Imphal–Jiribam Corridor, Manipur",
        "state": "Manipur",
        "lat": 24.55,
        "lon": 93.70,
        "rainfall24h": 47,
        "rainfall72h": 105,
        "soilMoisture": 51,
        "slope": 24,
        "elevation": 520,
        "ndvi": 0.55,
        "historicalDensity": 27,
        "riskScore": 29,
        "confidence": 74,
        "updatedAt": "12 min ago",
    },
    {
        "id": "H10",
        "location": "Aizawl–Lunglei Highway, Mizoram",
        "state": "Mizoram",
        "lat": 23.44,
        "lon": 92.72,
        "rainfall24h": 102,
        "rainfall72h": 224,
        "soilMoisture": 73,
        "slope": 37,
        "elevation": 1100,
        "ndvi": 0.38,
        "historicalDensity": 58,
        "riskScore": 63,
        "confidence": 84,
        "updatedAt": "4 min ago",
    },
    {
        "id": "H11",
        "location": "Atharamura Range, Tripura",
        "state": "Tripura",
        "lat": 23.90,
        "lon": 91.60,
        "rainfall24h": 38,
        "rainfall72h": 84,
        "soilMoisture": 44,
        "slope": 19,
        "elevation": 310,
        "ndvi": 0.58,
        "historicalDensity": 18,
        "riskScore": 19,
        "confidence": 71,
        "updatedAt": "14 min ago",
    },
    {
        "id": "H12",
        "location": "Barapani Catchment, Meghalaya",
        "state": "Meghalaya",
        "lat": 25.68,
        "lon": 91.90,
        "rainfall24h": 55,
        "rainfall72h": 119,
        "soilMoisture": 53,
        "slope": 22,
        "elevation": 850,
        "ndvi": 0.50,
        "historicalDensity": 22,
        "riskScore": 24,
        "confidence": 76,
        "updatedAt": "10 min ago",
    },
]

INITIAL_ALERTS = [
    {
        "id": "A-2201",
        "hotspotId": "H05",
        "title": "High landslide risk detected near Cherrapunji–Sohra Escarpment, Meghalaya.",
        "level": "CRITICAL",
        "status": "NEW",
        "reasons": [
            "Heavy rainfall (165mm/24h)",
            "Soil moisture above threshold (89%)",
            "Steep slope (51°)",
            "Historical landslide hotspot",
        ],
        "time": "2 min ago",
    },
    {
        "id": "A-2200",
        "hotspotId": "H01",
        "title": "High landslide risk detected near NH-10, Sikkim.",
        "level": "CRITICAL",
        "status": "ACKNOWLEDGED",
        "reasons": [
            "Heavy rainfall accumulation",
            "Soil moisture above threshold",
            "Steep terrain",
            "Historical landslide hotspot",
        ],
        "time": "18 min ago",
    },
    {
        "id": "A-2196",
        "hotspotId": "H03",
        "title": "Elevated risk on Tawang–Bomdila Highway, Arunachal Pradesh.",
        "level": "HIGH",
        "status": "ESCALATED",
        "reasons": ["Rising 72h rainfall", "Steep slope gradient"],
        "time": "1 hr ago",
    },
    {
        "id": "A-2189",
        "hotspotId": "H10",
        "title": "Moderate-to-high risk on Aizawl–Lunglei Highway, Mizoram.",
        "level": "HIGH",
        "status": "RESOLVED",
        "reasons": ["Sustained rainfall", "Elevated soil moisture"],
        "time": "5 hr ago",
    },
]

INITIAL_REPORTS = [
    {
        "id": "FR-3391",
        "location": "Near NH-10, 4km from Mangan",
        "state": "Sikkim",
        "lat": 27.35,
        "lon": 88.60,
        "type": "Slope crack",
        "severity": "High",
        "description": "Fresh tension crack observed along the cut slope above the highway, approx. 15m long.",
        "timestamp": "12 min ago",
        "aiStatus": "Possible slope crack detected — 82% confidence",
        "synced": True,
    },
    {
        "id": "FR-3388",
        "location": "Sohra–Dawki Road, 2km marker",
        "state": "Meghalaya",
        "lat": 25.29,
        "lon": 91.75,
        "type": "Water seepage",
        "severity": "Medium",
        "description": "Persistent water seepage on the uphill embankment after continuous rain.",
        "timestamp": "47 min ago",
        "aiStatus": "Seepage pattern consistent with saturation — 76% confidence",
        "synced": True,
    },
    {
        "id": "FR-3379",
        "location": "Haflong Bypass",
        "state": "Assam",
        "lat": 25.17,
        "lon": 93.00,
        "type": "Rockfall",
        "severity": "Medium",
        "description": "Small rockfall blocked one lane overnight, cleared by morning.",
        "timestamp": "3 hr ago",
        "aiStatus": "Image consistent with minor rockfall debris — 68% confidence",
        "synced": True,
    },
]

INFRA = [
    {
        "name": "NH-10 Corridor",
        "type": "Road",
        "state": "Sikkim",
        "risk": "CRITICAL",
        "nearestHotspot": "H01 · NH-10 Corridor, Sikkim",
        "priority": 94,
        "action": "Restrict heavy vehicle movement; deploy slope monitoring sensors.",
    },
    {
        "name": "Sohra–Dawki Bridge",
        "type": "Bridge",
        "state": "Meghalaya",
        "risk": "CRITICAL",
        "nearestHotspot": "H05 · Cherrapunji–Sohra Escarpment",
        "priority": 91,
        "action": "Structural inspection within 24 hours; prepare alternate route.",
    },
    {
        "name": "Chungthang Village",
        "type": "Village",
        "state": "Sikkim",
        "risk": "HIGH",
        "nearestHotspot": "H02 · Mangan–Chungthang Road",
        "priority": 82,
        "action": "Issue advisory to residents; identify evacuation staging point.",
    },
    {
        "name": "Tawang Government School",
        "type": "School",
        "state": "Arunachal Pradesh",
        "risk": "HIGH",
        "nearestHotspot": "H03 · Tawang–Bomdila Highway",
        "priority": 76,
        "action": "Coordinate with district education office on contingency plan.",
    },
    {
        "name": "Haflong Hill Railway Section",
        "type": "Railway",
        "state": "Assam",
        "risk": "MODERATE",
        "nearestHotspot": "H07 · Haflong Hill Section",
        "priority": 58,
        "action": "Increase track-walking frequency during rainfall events.",
    },
    {
        "name": "Community Health Centre, Aizawl",
        "type": "Hospital",
        "state": "Mizoram",
        "risk": "MODERATE",
        "nearestHotspot": "H10 · Aizawl–Lunglei Highway",
        "priority": 55,
        "action": "Verify backup access route for ambulance movement.",
    },
    {
        "name": "Dawki Border Road",
        "type": "Road",
        "state": "Meghalaya",
        "risk": "MODERATE",
        "nearestHotspot": "H06 · Shillong–Dawki Road",
        "priority": 49,
        "action": "Monitor drainage; clear culverts before peak monsoon.",
    },
    {
        "name": "Kohima–Dimapur NH-29",
        "type": "Road",
        "state": "Nagaland",
        "risk": "LOW",
        "nearestHotspot": "H08 · Kohima–Dimapur NH-29",
        "priority": 33,
        "action": "Routine inspection; no immediate action required.",
    },
]

T = {
    "en": {
        "dashboard": "Dashboard",
        "riskMap": "Live Risk Map",
        "predictions": "Predictions",
        "fieldReports": "Field Reports",
        "alerts": "Alerts",
        "infrastructure": "Infrastructure",
        "analytics": "Analytics",
        "settings": "Settings",
        "subtitle": "AI-Based Early Warning & Landslide Risk Monitoring System",
    },
    "hi": {
        "dashboard": "डैशबोर्ड",
        "riskMap": "लाइव जोखिम मानचित्र",
        "predictions": "पूर्वानुमान",
        "fieldReports": "फील्ड रिपोर्ट",
        "alerts": "चेतावनी",
        "infrastructure": "अवसंरचना",
        "analytics": "विश्लेषण",
        "settings": "सेटिंग्स",
        "subtitle": "एआई-आधारित पूर्व चेतावनी एवं भूस्खलन जोखिम निगरानी प्रणाली",
    },
    "as": {
        "dashboard": "ডেশ্ববৰ্ড",
        "riskMap": "লাইভ বিপদ মানচিত্ৰ",
        "predictions": "পূৰ্বানুমান",
        "fieldReports": "ক্ষেত্ৰ প্ৰতিবেদন",
        "alerts": "সতৰ্কবাণী",
        "infrastructure": "আন্তঃগাঁথনি",
        "analytics": "বিশ্লেষণ",
        "settings": "ছেটিংছ",
        "subtitle": "এআই-ভিত্তিক পূৰ্ব সতৰ্কবাণী আৰু ভূমিস্খলন বিপদ নিৰীক্ষণ প্ৰণালী",
    },
    "bn": {
        "dashboard": "ড্যাশবোর্ড",
        "riskMap": "লাইভ ঝুঁকি মানচিত্র",
        "predictions": "পূর্বাভাস",
        "fieldReports": "ফিল্ড রিপোর্ট",
        "alerts": "সতর্কতা",
        "infrastructure": "অবকাঠামো",
        "analytics": "বিশ্লেষণ",
        "settings": "সেটিংস",
        "subtitle": "এআই-ভিত্তিক পূর্ব সতর্কতা ও ভূমিধস ঝুঁকি পর্যবেক্ষণ ব্যবস্থা",
    },
}

# =========================================================================
# STATE INITIALIZATION
# =========================================================================
st.set_page_config(
    page_title="GeoSuraksha AI",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "hotspots" not in st.session_state:
    for h in RAW_HOTSPOTS:
        h["riskLevel"] = level_from_score(h["riskScore"])
    st.session_state.hotspots = RAW_HOTSPOTS

if "alerts" not in st.session_state:
    st.session_state.alerts = INITIAL_ALERTS

if "reports" not in st.session_state:
    st.session_state.reports = INITIAL_REPORTS

if "lang" not in st.session_state:
    st.session_state.lang = "en"

if "role" not in st.session_state:
    st.session_state.role = "AUTHORITY"

if "offline" not in st.session_state:
    st.session_state.offline = False

if "pending_offline_reports" not in st.session_state:
    st.session_state.pending_offline_reports = 0

# =========================================================================
# THEME INJECTION
# =========================================================================
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {C["bg"]};
            color: {C["text"]};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        [data-testid="stSidebar"] {{
            background-color: {C["panel2"]} !important;
            border-right: 1px solid {C["border"]};
        }}
        .metric-card {{
            background-color: {C["panel"]};
            border: 1px solid {C["border"]};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }}
        .metric-title {{
            color: {C["textDim"]};
            font-size: 13px;
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: {C["text"]};
        }}
        .risk-pill {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .panel-box {{
            background-color: {C["panel"]};
            border: 1px solid {C["border"]};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }}
    </style>
""",
    unsafe_allow_html=True,
)


def risk_pill_html(level: str) -> str:
    meta = RISK_META.get(level, RISK_META["LOW"])
    return f'<span class="risk-pill" style="background:{meta["color"]}22; color:{meta["color"]}; border:1px solid {meta["color"]}55;">● {meta["label"]}</span>'


@st.cache_resource
def load_landslide_model():
    """Load the trained Random Forest demo model."""
    model_file = os.path.join(os.path.dirname(__file__), "landslide_model_demo.joblib")
    if not os.path.exists(model_file):
        return None
    return joblib.load(model_file)


def _ml_score_from_inputs(rain24, rain72, soil, slope, elevation, ndvi, hist):
    bundle = load_landslide_model()
    if bundle is None:
        return None

    features = bundle["features"]
    model = bundle["model"]
    row = pd.DataFrame([{
        "rainfall_24h": float(rain24),
        "rainfall_72h": float(rain72),
        "soil_moisture": float(soil),
        "slope": float(slope),
        "elevation": float(elevation),
        "ndvi": float(ndvi),
        "historical_density": float(hist),
    }])[features]

    probability = float(model.predict_proba(row)[0, 1])
    score = int(round(probability * 100))
    return score, probability, model.feature_importances_, bundle


def compute_risk(rain24, rain72, soil, slope, elevation, ndvi, hist):
    """Actual ML inference using the trained Random Forest model."""
    result = _ml_score_from_inputs(rain24, rain72, soil, slope, elevation, ndvi, hist)

    if result is None:
        # Safe fallback if the model file is missing.
        rain_score = min(100.0, (rain24 / 200.0) * 60.0 + (rain72 / 450.0) * 40.0)
        soil_score = float(soil)
        slope_score = min(100.0, (slope / 60.0) * 100.0)
        hist_score = float(hist)
        veg_score = (1.0 - ndvi) * 100.0
        score = round(
            min(
                100.0,
                rain_score * 0.32
                + soil_score * 0.24
                + slope_score * 0.21
                + hist_score * 0.14
                + veg_score * 0.09,
            )
        )
        contributions = [
            {"label": "Rainfall", "pct": 32, "color": "#3B82F6"},
            {"label": "Soil Moisture", "pct": 24, "color": "#0EA5E9"},
            {"label": "Slope", "pct": 21, "color": C["high"]},
            {"label": "Historical Susceptibility", "pct": 14, "color": "#A855F7"},
            {"label": "Vegetation", "pct": 9, "color": C["low"]},
        ]
        return score, contributions, None, None, None

    score, probability, importances, bundle = result
    labels = {
        "rainfall_24h": "24h Rainfall",
        "rainfall_72h": "72h Rainfall",
        "soil_moisture": "Soil Moisture",
        "slope": "Slope",
        "elevation": "Elevation",
        "ndvi": "Vegetation (NDVI)",
        "historical_density": "Historical Susceptibility",
    }
    contributions = [
        {
            "label": labels.get(feature, feature),
            "pct": int(round(importance * 100)),
            "color": C["accent"],
        }
        for feature, importance in sorted(
            zip(bundle["features"], importances),
            key=lambda x: x[1],
            reverse=True,
        )
    ]
    return score, contributions, probability, importances, bundle


# =========================================================================
# SIDEBAR
# =========================================================================
with st.sidebar:
    st.markdown("### ⛰️ GeoSuraksha AI")
    st.caption("Early Warning & Hazard Intelligence System")
    st.divider()

    selected_page = st.radio(
        "Navigation",
        options=[
            "Dashboard",
            "Live Risk Map",
            "Predictions",
            "Field Reports",
            "Alerts",
            "Infrastructure",
            "Analytics",
            "Settings",
        ],
        index=0,
    )

    st.divider()
    active_alerts_count = len(
        [a for a in st.session_state.alerts if a["status"] != "RESOLVED"]
    )
    st.markdown(
        f"**Active Alerts:** <span style='color:{C['critical']}; font-weight:bold;'>{active_alerts_count}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:{C['panel']}; border:1px solid {C['border']}; padding:8px; border-radius:6px; font-size:11px; color:{C['textFaint']}'>🛡️ Decision-support system only.</div>",
        unsafe_allow_html=True,
    )

# =========================================================================
# TOP HEADER BAR
# =========================================================================
top_c1, top_c2, top_c3, top_c4 = st.columns([3, 1.5, 1, 1])
with top_c1:
    st.markdown(
        f"<div style='font-size:12px; color:{C['textDim']}'>📍 Region: <b>All NER States</b> | 🌧️ <b>Monsoon active</b> · 24h rainfall trending up</div>",
        unsafe_allow_html=True,
    )
with top_c2:
    if st.button("🔄 Sync Feed (Updated now)"):
        st.toast("Data refreshed successfully.", icon="✅")
with top_c3:
    lang_choice = st.selectbox(
        "Language",
        options=["en", "hi", "as", "bn"],
        index=["en", "hi", "as", "bn"].index(st.session_state.lang),
        label_visibility="collapsed",
    )
    st.session_state.lang = lang_choice
with top_c4:
    st.markdown(
        f"<div style='text-align:right; font-size:12px; color:{C['accent']};'><b>{st.session_state.role}</b></div>",
        unsafe_allow_html=True,
    )

st.write("")

# =========================================================================
# PAGE 1: DASHBOARD
# =========================================================================
if selected_page == "Dashboard":
    col_head, col_sim = st.columns([4, 1.2])
    with col_head:
        st.subheader("Operations Overview")
        st.caption(T[st.session_state.lang]["subtitle"])
    with col_sim:
        if st.button("⚡ Run Demo Simulation", use_container_width=True):
            # Simulate a sensor update and run the trained ML model.
            for h in st.session_state.hotspots:
                if h["id"] == "H01":
                    h["rainfall24h"] = 142
                    h["rainfall72h"] = 365
                    h["soilMoisture"] = 91
                    ml_result = _ml_score_from_inputs(
                        h["rainfall24h"],
                        h["rainfall72h"],
                        h["soilMoisture"],
                        h["slope"],
                        h["elevation"],
                        h["ndvi"],
                        h["historicalDensity"],
                    )
                    if ml_result:
                        ml_score = ml_result[0]
                        h["riskScore"] = ml_score
                        h["riskLevel"] = level_from_score(ml_score)
                        h["confidence"] = int(round(ml_result[1] * 100))
                    h["updatedAt"] = "just now"
            st.session_state.alerts.insert(
                0,
                {
                    "id": f"A-{random.randint(3100, 3999)}",
                    "hotspotId": "H01",
                    "title": "High landslide risk detected near NH-10 Corridor, Sikkim.",
                    "level": "CRITICAL",
                    "status": "NEW",
                    "reasons": [
                        "Heavy rainfall",
                        "Soil moisture above threshold",
                        "Steep slope",
                        "Historical hotspot",
                    ],
                    "time": "just now",
                },
            )
            st.toast("Simulation executed: NH-10 escalated to CRITICAL", icon="⚠️")
            st.rerun()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    crit_count = len(
        [h for h in st.session_state.hotspots if h["riskLevel"] == "CRITICAL"]
    )
    act_alerts = len(
        [a for a in st.session_state.alerts if a["status"] != "RESOLVED"]
    )

    c1.markdown(
        f"<div class='metric-card'><div class='metric-title'>Active Risk Zones</div><div class='metric-value'>{len(st.session_state.hotspots)}</div></div>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"<div class='metric-card'><div class='metric-title'>Critical Zones</div><div class='metric-value' style='color:{C['critical']}'>{crit_count}</div></div>",
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"<div class='metric-card'><div class='metric-title'>Active Alerts</div><div class='metric-value' style='color:{C['high']}'>{act_alerts}</div></div>",
        unsafe_allow_html=True,
    )
    c4.markdown(
        f"<div class='metric-card'><div class='metric-title'>Corridors</div><div class='metric-value'>148</div></div>",
        unsafe_allow_html=True,
    )
    c5.markdown(
        f"<div class='metric-card'><div class='metric-title'>Reports (30d)</div><div class='metric-value'>{len(st.session_state.reports)+323}</div></div>",
        unsafe_allow_html=True,
    )
    c6.markdown(
        f"<div class='metric-card'><div class='metric-title'>ML Model</div><div class='metric-value' style='color:{C['low']}'>RF</div></div>",
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns([2, 1])
    with g1:
        st.markdown("##### Highest-risk zones right now")
        top_hotspots = sorted(
            st.session_state.hotspots,
            key=lambda x: x["riskScore"],
            reverse=True,
        )[:5]
        for h in top_hotspots:
            hl = RISK_META[h["riskLevel"]]
            st.markdown(
                f"""
            <div style='background:{C["panel2"]}; border:1px solid {C["border"]}; border-radius:6px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span style='font-size:13px; font-weight:600; color:{C["text"]}'>{h["location"]}</span>
                    <div style='font-size:11px; color:{C["textFaint"]}'>{h["state"]} · updated {h["updatedAt"]}</div>
                </div>
                <div style='text-align:right;'>
                    <span style='font-size:18px; font-weight:700; color:{hl["color"]}; margin-right:12px;'>{h["riskScore"]}</span>
                    {risk_pill_html(h["riskLevel"])}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with g2:
        st.markdown("##### Latest alerts")
        for a in st.session_state.alerts[:4]:
            st.markdown(
                f"""
            <div style='border-bottom:1px solid {C["border"]}; padding:8px 0;'>
                <div style='display:flex; justify-content:space-between;'>
                    {risk_pill_html(a["level"])}
                    <span style='font-size:11px; color:{C["textFaint"]}'>{a["time"]}</span>
                </div>
                <div style='font-size:12px; font-weight:500; margin-top:4px; color:{C["text"]}'>{a["title"]}</div>
                <span style='font-size:10px; color:{C["textDim"]}; background:{C["panel2"]}; border:1px solid {C["border"]}; border-radius:3px; padding:2px 6px;'>{a["status"]}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

# =========================================================================
# PAGE 2: LIVE RISK MAP
# =========================================================================
elif selected_page == "Live Risk Map":
    st.subheader("Live Geospatial Risk Map")

    filter_cols = st.columns([3, 1, 1])
    with filter_cols[0]:
        level_sel = st.radio(
            "Filter Risk Level",
            options=["ALL", "LOW", "MODERATE", "HIGH", "CRITICAL"],
            horizontal=True,
        )
    with filter_cols[1]:
        time_range = st.selectbox("Forecast Window", ["24h", "48h", "7d"])
    with filter_cols[2]:
        hotspot_picker = st.selectbox(
            "Inspect Hotspot",
            options=[h["id"] + " - " + h["location"] for h in st.session_state.hotspots],
        )

    filtered_hotspots = [
        h
        for h in st.session_state.hotspots
        if level_sel == "ALL" or h["riskLevel"] == level_sel
    ]
    df_map = pd.DataFrame(filtered_hotspots)

    map_c1, map_c2 = st.columns([2.2, 1])
    with map_c1:
        color_map = {
            "LOW": C["low"],
            "MODERATE": C["moderate"],
            "HIGH": C["high"],
            "CRITICAL": C["critical"],
        }
        fig_map = px.scatter(
            df_map,
            x="lon",
            y="lat",
            size="riskScore",
            color="riskLevel",
            hover_name="location",
            hover_data={
                "state": True,
                "riskScore": True,
                "rainfall24h": True,
                "soilMoisture": True,
                "slope": True,
                "lon": False,
                "lat": False,
            },
            color_discrete_map=color_map,
            size_max=22,
        )
        # Add labels for Northeast states
        for s in STATE_LABELS:
            fig_map.add_annotation(
                x=s["lon"],
                y=s["lat"],
                text=s["name"].upper(),
                showarrow=False,
                font=dict(size=9, color=C["textFaint"]),
            )

        fig_map.update_layout(
            paper_bgcolor=C["panel"],
            plot_bgcolor=C["bg"],
            xaxis=dict(
                title="Longitude",
                showgrid=True,
                gridcolor=C["border"],
                zeroline=False,
            ),
            yaxis=dict(
                title="Latitude",
                showgrid=True,
                gridcolor=C["border"],
                zeroline=False,
            ),
            font=dict(color=C["textDim"]),
            height=540,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with map_c2:
        selected_id = hotspot_picker.split(" - ")[0]
        h_selected = next(
            (h for h in st.session_state.hotspots if h["id"] == selected_id),
            None,
        )
        if h_selected:
            st.markdown(
                f"""
            <div class='panel-box'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <h4>{h_selected["location"]}</h4>
                    {risk_pill_html(h_selected["riskLevel"])}
                </div>
                <div style='color:{C["textFaint"]}; font-size:11px; margin-bottom:12px;'>{h_selected["state"]} · updated {h_selected["updatedAt"]}</div>
                
                <div style='background:{C["panel2"]}; padding:12px; border-radius:6px; margin-bottom:14px; text-align:center;'>
                    <div style='font-size:11px; color:{C["textFaint"]}'>Risk Score</div>
                    <div style='font-size:36px; font-weight:800; color:{RISK_META[h_selected["riskLevel"]]["color"]}'>{h_selected["riskScore"]}<span style='font-size:14px; color:{C["textFaint"]}'>/100</span></div>
                </div>
                
                <table style='width:100%; font-size:12px; color:{C["text"]}; line-height:2;'>
                    <tr><td style='color:{C["textFaint"]}'>Latitude / Longitude</td><td><b>{h_selected["lat"]:.2f}°N, {h_selected["lon"]:.2f}°E</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>24h Rainfall</td><td><b>{h_selected["rainfall24h"]} mm</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>72h Rainfall</td><td><b>{h_selected["rainfall72h"]} mm</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>Soil Moisture</td><td><b>{h_selected["soilMoisture"]}%</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>Slope</td><td><b>{h_selected["slope"]}°</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>Elevation</td><td><b>{h_selected["elevation"]} m</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>Vegetation Index (NDVI)</td><td><b>{h_selected["ndvi"]}</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>Historical Density</td><td><b>{h_selected["historicalDensity"]}/100</b></td></tr>
                    <tr><td style='color:{C["textFaint"]}'>Model Confidence</td><td><b>{h_selected["confidence"]}%</b></td></tr>
                </table>
            </div>
            """,
                unsafe_allow_html=True,
            )

# =========================================================================
# PAGE 3: PREDICTIONS
# =========================================================================
elif selected_page == "Predictions":
    st.subheader("AI Risk Prediction Sandbox")
    st.caption("Adjust real-time sensor parameters to evaluate hazard risk.")

    p_col1, p_col2 = st.columns([1.1, 2])
    with p_col1:
        st.markdown("##### Input Parameters")
        r24 = st.slider("24h Rainfall (mm)", 0, 250, 85)
        r72 = st.slider("72h Rainfall (mm)", 0, 500, 210)
        soil = st.slider("Soil Moisture (%)", 0, 100, 72)
        slope = st.slider("Slope Angle (°)", 0, 70, 34)
        elevation = st.slider("Elevation (m)", 0, 3000, 1200)
        ndvi = st.slider("NDVI (Vegetation)", 0.1, 0.8, 0.4, step=0.01)
        hist = st.slider("Historical Landslide Susceptibility", 0, 100, 55)

        run_calc = st.button(
            "⚡ RUN AI PREDICTION", use_container_width=True, type="primary"
        )

    score, contributions, probability, importances, model_bundle = compute_risk(r24, r72, soil, slope, elevation, ndvi, hist)
    pred_level = level_from_score(score)

    with p_col2:
        res1, res2 = st.columns([1, 2])
        with res1:
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {
                            "range": [0, 100],
                            "tickcolor": C["textFaint"],
                        },
                        "bar": {"color": RISK_META[pred_level]["color"]},
                        "steps": [
                            {"range": [0, 25], "color": C["panel2"]},
                            {"range": [25, 50], "color": C["panel2"]},
                            {"range": [50, 75], "color": C["panel2"]},
                            {"range": [75, 100], "color": C["panel2"]},
                        ],
                    },
                )
            )
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=C["text"]),
                height=220,
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        with res2:
            st.markdown(
                f"""
            <div style='padding-top:20px;'>
                {risk_pill_html(pred_level)}
                <p style='font-size:13px; color:{C["textDim"]}; margin-top:10px;'>
                    The Random Forest model combines rainfall, soil moisture, slope, elevation, vegetation and historical susceptibility to estimate landslide probability.
                </p>
                <div style='font-size:12px; color:{C["accent"]}; margin-top:8px;'><b>ML probability: {("N/A" if probability is None else f"{probability*100:.1f}%")}</b></div>
                <div style='font-size:11px; color:{C["textFaint"]}; margin-top:6px;'>ℹ️ DEMO MODEL: trained on synthetic data for prototype validation. Replace with validated NER historical/sensor/satellite data before operational use.</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        if model_bundle is not None:
            st.success("✅ Random Forest ML model loaded and used for this prediction.")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Landslide Probability", f"{probability*100:.1f}%")
            with m2:
                st.metric("ML Risk Score", f"{score}/100")
            with m3:
                st.metric("Model", "Random Forest")
        else:
            st.warning("ML model file not found — using the prototype fallback scoring engine.")

        st.markdown("##### Contributing Factors")
        for c in contributions:
            st.markdown(
                f"""
            <div style='font-size:12px; color:{C["textDim"]}; display:flex; justify-content:space-between;'>
                <span>{c["label"]}</span><span>{c["pct"]}%</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.progress(c["pct"] / 100)

        st.markdown("##### Landslide Risk — Next 72 Hours Trajectory")
        f_df = pd.DataFrame(
            [
                {"t": "Now", "risk": 48, "rain": 14},
                {"t": "+12h", "risk": 61, "rain": 22},
                {"t": "+24h", "risk": 73, "rain": 31},
                {"t": "+36h", "risk": 81, "rain": 38},
                {"t": "+48h", "risk": 87, "rain": 44},
                {"t": "+60h", "risk": 79, "rain": 27},
                {"t": "+72h", "risk": 68, "rain": 16},
            ]
        )

        fig_pred_line = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pred_line.add_trace(
            go.Scatter(
                x=f_df["t"],
                y=f_df["risk"],
                name="Risk Trajectory",
                line=dict(color=C["accent"], width=3),
            ),
            secondary_y=False,
        )
        fig_pred_line.add_trace(
            go.Bar(
                x=f_df["t"],
                y=f_df["rain"],
                name="Rainfall Forecast (mm)",
                marker_color="#3B82F6",
                opacity=0.4,
            ),
            secondary_y=True,
        )

        fig_pred_line.update_layout(
            paper_bgcolor=C["panel"],
            plot_bgcolor=C["panel2"],
            font=dict(color=C["textFaint"], size=10),
            height=240,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig_pred_line, use_container_width=True)

# =========================================================================
# PAGE 4: FIELD REPORTS
# =========================================================================
elif selected_page == "Field Reports":
    st.subheader("Field Incident Submissions & Synchronization")

    c_rep1, c_rep2 = st.columns([1.2, 2])
    with c_rep1:
        st.markdown("##### Submit Field Incident")

        off_toggle = st.toggle("Offline Mode", value=st.session_state.offline)
        if off_toggle != st.session_state.offline:
            st.session_state.offline = off_toggle
            if (
                not off_toggle
                and st.session_state.pending_offline_reports > 0
            ):
                st.success(
                    f"{st.session_state.pending_offline_reports} offline reports successfully synced!"
                )
                for r in st.session_state.reports:
                    r["synced"] = True
                st.session_state.pending_offline_reports = 0

        with st.form("incident_form", clear_on_submit=True):
            loc = st.text_input(
                "Location", placeholder="e.g., 3km south of Mangan, NH-10"
            )
            r_type = st.selectbox(
                "Type",
                [
                    "Slope crack",
                    "Rockfall",
                    "Landslide",
                    "Road blockage",
                    "Soil movement",
                    "Water seepage",
                    "Other",
                ],
            )
            sev = st.selectbox(
                "Severity", ["Low", "Medium", "High", "Critical"]
            )
            desc = st.text_area("Observations", placeholder="Describe observed slope conditions")
            submitted = st.form_submit_button(
                "Submit Report", use_container_width=True
            )

            if submitted and loc.strip():
                ai_conf = random.randint(72, 94)
                new_rep = {
                    "id": f"FR-{random.randint(3410, 3990)}",
                    "location": loc,
                    "state": "Unspecified",
                    "lat": 0.0,
                    "lon": 0.0,
                    "type": r_type,
                    "severity": sev,
                    "description": desc or "No additional description provided.",
                    "timestamp": "Just now",
                    "aiStatus": f"Possible {r_type.lower()} detected — {ai_conf}% confidence (simulated)",
                    "synced": not st.session_state.offline,
                }
                st.session_state.reports.insert(0, new_rep)
                if st.session_state.offline:
                    st.session_state.pending_offline_reports += 1
                    st.warning("Saved locally in offline queue.")
                else:
                    st.success("Report successfully submitted and analyzed.")
                st.rerun()

    with c_rep2:
        st.markdown(f"##### Recent Field Reports ({len(st.session_state.reports)})")
        for r in st.session_state.reports:
            sync_tag = (
                "<span style='color:#3FB950; font-size:10px;'>● Synced</span>"
                if r["synced"]
                else "<span style='color:#F0883E; font-size:10px;'>▲ Pending sync</span>"
            )
            st.markdown(
                f"""
            <div style='background:{C["panel"]}; border:1px solid {C["border"]}; border-radius:6px; padding:12px; margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between;'>
                    <b>{r["type"]}</b>
                    <div>{sync_tag} <span style='font-size:11px; color:{C["textFaint"]}; margin-left:6px;'>{r["timestamp"]}</span></div>
                </div>
                <div style='font-size:12px; color:{C["textDim"]}; margin-top:3px;'>📍 {r["location"]}</div>
                <div style='font-size:12px; color:{C["text"]}; margin-top:6px;'>{r["description"]}</div>
                <div style='background:{C["accentDim"]}; color:{C["accent"]}; font-size:11px; padding:4px 8px; border-radius:4px; margin-top:8px;'>
                    🤖 {r["aiStatus"]}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# =========================================================================
# PAGE 5: ALERTS
# =========================================================================
elif selected_page == "Alerts":
    st.subheader("Early Warning Alert Stream")

    for a in st.session_state.alerts:
        st.markdown(
            f"""
        <div class='panel-box'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                    <div>{risk_pill_html(a["level"])} <span style='font-size:11px; color:{C["textFaint"]}; margin-left:8px;'>{a["time"]} · {a["id"]}</span></div>
                    <h4 style='margin-top:6px; color:{C["text"]}'>"{a["title"]}"</h4>
                    <div style='margin-top:8px;'>
                        {" ".join([f"<span style='background:{C['panel2']}; color:{C['textDim']}; font-size:10px; padding:3px 6px; border-radius:4px; margin-right:4px;'>{r}</span>" for r in a["reasons"]])}
                    </div>
                </div>
                <div>
                    <span style='background:{C["border"]}; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:600;'>{a["status"]}</span>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        b_c1, b_c2, b_c3 = st.columns([1, 1, 3])
        with b_c1:
            if st.button(f"Acknowledge", key=f"ack_{a['id']}"):
                a["status"] = "ACKNOWLEDGED"
                st.rerun()
        with b_c2:
            if st.button(f"Escalate", key=f"esc_{a['id']}"):
                a["status"] = "ESCALATED"
                st.toast(f"Alert {a['id']} escalated to authorities.")
                st.rerun()
        with b_c3:
            if st.button(f"Mark Resolved", key=f"res_{a['id']}"):
                a["status"] = "RESOLVED"
                st.rerun()

# =========================================================================
# PAGE 6: INFRASTRUCTURE
# =========================================================================
elif selected_page == "Infrastructure":
    st.subheader("Critical Infrastructure Vulnerability Registry")
    st.caption("Ranked by calculated landslide risk exposure priority.")

    df_infra = pd.DataFrame(INFRA).sort_values("priority", ascending=False)
    st.dataframe(
        df_infra[
            [
                "name",
                "type",
                "state",
                "risk",
                "priority",
                "nearestHotspot",
                "action",
            ]
        ],
        column_config={
            "name": "Asset Name",
            "type": "Type",
            "state": "State",
            "risk": "Risk Level",
            "priority": st.column_config.ProgressColumn(
                "Priority", min_value=0, max_value=100, format="%d"
            ),
            "nearestHotspot": "Nearest Corridor",
            "action": "Recommended Engineering Mitigation",
        },
        use_container_width=True,
        hide_index=True,
    )

# =========================================================================
# PAGE 7: ANALYTICS
# =========================================================================
elif selected_page == "Analytics":
    st.subheader("Historical & Model Performance Analytics")

    a1, a2 = st.columns(2)
    with a1:
        # Chart 1: Monthly landslides
        df_ml = pd.DataFrame(
            [
                {"month": "Jan", "events": 2},
                {"month": "Feb", "events": 3},
                {"month": "Mar", "events": 5},
                {"month": "Apr", "events": 9},
                {"month": "May", "events": 14},
                {"month": "Jun", "events": 27},
                {"month": "Jul", "events": 41},
                {"month": "Aug", "events": 38},
                {"month": "Sep", "events": 22},
            ]
        )
        fig_m = px.bar(
            df_ml,
            x="month",
            y="events",
            title="Landslides by Month",
            color_discrete_sequence=[C["accent"]],
        )
        fig_m.update_layout(
            paper_bgcolor=C["panel"],
            plot_bgcolor=C["panel2"],
            font=dict(color=C["textDim"]),
            height=260,
            margin=dict(l=20, r=20, t=35, b=20),
        )
        st.plotly_chart(fig_m, use_container_width=True)

        # Chart 2: Risk distribution pie
        df_dist = pd.DataFrame(
            [
                {"name": "Low", "value": 62, "color": C["low"]},
                {"name": "Moderate", "value": 41, "color": C["moderate"]},
                {"name": "High", "value": 28, "color": C["high"]},
                {"name": "Critical", "value": 17, "color": C["critical"]},
            ]
        )
        fig_pie = px.pie(
            df_dist,
            values="value",
            names="name",
            title="Risk Distribution Across Monitored Zones",
            color="name",
            color_discrete_map={
                "Low": C["low"],
                "Moderate": C["moderate"],
                "High": C["high"],
                "Critical": C["critical"],
            },
            hole=0.55,
        )
        fig_pie.update_layout(
            paper_bgcolor=C["panel"],
            font=dict(color=C["textDim"]),
            height=260,
            margin=dict(l=20, r=20, t=35, b=20),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with a2:
        # Chart 3: Rainfall vs Landslides
        df_rvs = pd.DataFrame(
            [
                {"month": "Jan", "rainfall": 40, "events": 2},
                {"month": "Feb", "rainfall": 55, "events": 3},
                {"month": "Mar", "rainfall": 90, "events": 5},
                {"month": "Apr", "rainfall": 160, "events": 9},
                {"month": "May", "rainfall": 260, "events": 14},
                {"month": "Jun", "rainfall": 410, "events": 27},
                {"month": "Jul", "rainfall": 520, "events": 41},
                {"month": "Aug", "rainfall": 470, "events": 38},
                {"month": "Sep", "rainfall": 300, "events": 22},
            ]
        )
        fig_rvs = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rvs.add_trace(
            go.Scatter(
                x=df_rvs["month"],
                y=df_rvs["rainfall"],
                name="Rainfall (mm)",
                line=dict(color="#3B82F6", width=2),
            ),
            secondary_y=False,
        )
        fig_rvs.add_trace(
            go.Scatter(
                x=df_rvs["month"],
                y=df_rvs["events"],
                name="Events",
                line=dict(color=C["critical"], width=2),
            ),
            secondary_y=True,
        )
        fig_rvs.update_layout(
            title_text="Rainfall vs Landslide Events",
            paper_bgcolor=C["panel"],
            plot_bgcolor=C["panel2"],
            font=dict(color=C["textDim"]),
            height=260,
            margin=dict(l=20, r=20, t=35, b=20),
        )
        st.plotly_chart(fig_rvs, use_container_width=True)

        # Chart 4: Alerts vs False alarms
        df_alerts = pd.DataFrame(
            [
                {"month": "Apr", "alerts": 6, "falseAlarms": 1},
                {"month": "May", "alerts": 11, "falseAlarms": 2},
                {"month": "Jun", "alerts": 24, "falseAlarms": 3},
                {"month": "Jul", "alerts": 33, "falseAlarms": 4},
                {"month": "Aug", "alerts": 29, "falseAlarms": 2},
                {"month": "Sep", "alerts": 12, "falseAlarms": 1},
            ]
        )
        fig_alt = go.Figure(
            data=[
                go.Bar(
                    name="Alerts",
                    x=df_alerts["month"],
                    y=df_alerts["alerts"],
                    marker_color=C["high"],
                ),
                go.Bar(
                    name="False Alarms",
                    x=df_alerts["month"],
                    y=df_alerts["falseAlarms"],
                    marker_color=C["textFaint"],
                ),
            ]
        )
        fig_alt.update_layout(
            barmode="group",
            title_text="Alerts Generated vs False Alarms",
            paper_bgcolor=C["panel"],
            plot_bgcolor=C["panel2"],
            font=dict(color=C["textDim"]),
            height=260,
            margin=dict(l=20, r=20, t=35, b=20),
        )
        st.plotly_chart(fig_alt, use_container_width=True)

# =========================================================================
# PAGE 8: SETTINGS
# =========================================================================
    st.subheader("Model Status")
    _bundle = load_landslide_model()
    if _bundle is not None:
        st.success("Random Forest model: LOADED")
        _m = _bundle.get("metrics", {})
        st.caption("Training source: synthetic DEMO dataset — not for operational deployment.")
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Accuracy", f"{_m.get('accuracy', 0)*100:.1f}%")
        sm2.metric("Precision", f"{_m.get('precision', 0)*100:.1f}%")
        sm3.metric("Recall", f"{_m.get('recall', 0)*100:.1f}%")
        sm4.metric("ROC-AUC", f"{_m.get('roc_auc', 0):.3f}")
    else:
        st.error("Random Forest model file not found.")
    st.divider()

elif selected_page == "Settings":
    st.subheader("System Configuration & Architecture")

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("##### Operating Role")
        role_sel = st.selectbox(
            "Select Session Role",
            ["AUTHORITY", "ADMIN", "FIELD OFFICER", "CITIZEN"],
            index=["AUTHORITY", "ADMIN", "FIELD OFFICER", "CITIZEN"].index(
                st.session_state.role
            ),
        )
        st.session_state.role = role_sel
        st.caption("Controls operational simulation authority (demonstration mode).")

    with s2:
        st.markdown("##### Ingestion Feeds Status")
        data_sources = [
            {"name": "Rainfall", "status": "LIVE", "c": C["low"]},
            {"name": "Weather Forecast", "status": "LIVE", "c": C["low"]},
            {
                "name": "Soil Moisture",
                "status": "SIMULATED",
                "c": C["moderate"],
            },
            {
                "name": "Satellite Data",
                "status": "SIMULATED",
                "c": C["moderate"],
            },
            {"name": "DEM / Terrain", "status": "AVAILABLE", "c": C["accent"]},
            {
                "name": "Historical Landslides",
                "status": "DEMO DATA",
                "c": C["textFaint"],
            },
            {
                "name": "Citizen Reports",
                "status": "LIVE SIMULATION",
                "c": C["high"],
            },
        ]
        for ds in data_sources:
            st.markdown(
                f"""
            <div style='display:flex; justify-content:space-between; background:{C["panel2"]}; padding:6px 12px; border-radius:4px; margin-bottom:4px; font-size:12px;'>
                <span>{ds["name"]}</span>
                <span style='color:{ds["c"]}; font-weight:bold;'>● {ds["status"]}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("##### Pipeline Architecture")
    steps = [
        "1. Data Sources",
        "2. Data Ingestion",
        "3. Data Cleaning & Validation",
        "4. Geospatial Feature Engineering",
        "5. AI/ML Risk Engine",
        "6. Risk Score Generation",
        "7. GIS Visualization",
        "8. Alert Engine",
        "9. Emergency Response & Action",
    ]
    st.markdown(" ➔ ".join([f"`{s}`" for s in steps]))