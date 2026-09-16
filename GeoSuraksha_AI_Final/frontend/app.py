import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

from data.sample_data import HOTSPOTS, INFRASTRUCTURE, STATE_LABELS
from utils.risk import predict, load_model

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

C = {
    "bg": "#0A0E14",
    "panel": "#111823",
    "panel2": "#0D131C",
    "border": "#1E2A38",
    "text": "#E6EBF1",
    "dim": "#8C99AB",
    "accent": "#2DD4BF",
    "low": "#3FB950",
    "moderate": "#E3B341",
    "high": "#F0883E",
    "critical": "#F85149"
}

RISK_META = {
    "LOW": C["low"],
    "MODERATE": C["moderate"],
    "HIGH": C["high"],
    "CRITICAL": C["critical"]
}

st.set_page_config(
    page_title="GeoSuraksha AI",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
<style>
    body {{ background: {C['bg']}; }}
    .block-container {{ padding-top: 1.2rem; }}
    .panel {{
        background: {C['panel']};
        border: 1px solid {C['border']};
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }}
    h1, h2, h3, h4 {{ color: {C['text']}; }}
    .muted {{ color: {C['dim']}; }}
</style>
""", unsafe_allow_html=True)


def api_get(path, params=None):
    try:
        r = requests.get(API + path, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def api_post(path, payload):
    try:
        r = requests.post(API + path, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def prep_df(data):
    df = pd.DataFrame(data)
    if "riskScore" in df.columns and "riskLevel" not in df.columns:
        df["riskLevel"] = df["riskScore"].apply(
            lambda x: "CRITICAL" if x >= 76 else "HIGH" if x >= 51 else "MODERATE" if x >= 26 else "LOW"
        )
    if "weatherSource" not in df.columns:
        df["weatherSource"] = "Live / Cached API"
    return df


st.title("⛰️ GeoSuraksha AI")
st.caption("AI-Based Early Warning & Landslide Risk Monitoring System — Northeast Region")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Risk Map", "AI Prediction", "Earthquakes", "Field Reports", "Infrastructure", "Analytics", "System Status"]
)

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if page == "Dashboard":
    with st.spinner("Fetching live weather, earthquake and AI risk data..."):
        live = api_get("/api/hotspots", {"refresh": True}) or HOTSPOTS
    df = prep_df(live)

    st.subheader("NER Situation Dashboard")
    cols = st.columns(4)
    cols[0].metric("Monitored Hotspots", len(df))
    cols[1].metric("Critical", int((df.riskScore >= 76).sum()))
    cols[2].metric("High", int(((df.riskScore >= 51) & (df.riskScore < 76)).sum()))
    cols[3].metric("Max Risk", f"{df.riskScore.max():.0f}/100")

    st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"})[["latitude", "longitude"]], zoom=6)

    cols_to_show = ["id", "location", "state", "riskScore", "riskLevel", "rainfall24h", "rainfall72h", "soilMoisture", "slope", "weatherSource"]
    available_cols = [c for c in cols_to_show if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True)

    st.subheader("Automatic Alerts")
    alerts = api_get("/api/alerts") or []
    if alerts:
        for a in alerts[:8]:
            msg = f"**{a['level']}** — {a['title']} · {a['status']}"
            (st.error if a['level'] == "CRITICAL" else st.warning)(msg)
            if a.get("reasons"):
                st.caption("Contributors: " + ", ".join(a["reasons"]))
            if a.get("status") == "NEW" and st.button(f"Acknowledge alert #{a['id']}", key=f"ack_{a['id']}"):
                api_post(f"/api/alerts/{a['id']}/acknowledge", {})
                st.rerun()
    else:
        st.success("No active high/critical alerts.")

# ----------------------------------------------------
# 2. RISK MAP
# ----------------------------------------------------
elif page == "Risk Map":
    st.subheader("GIS Risk Map")
    with st.spinner("Refreshing live risk map..."):
        live = api_get("/api/hotspots", {"refresh": True}) or HOTSPOTS
    df = prep_df(live)

    try:
        hover_cols = [c for c in ["state", "riskScore", "rainfall24h", "soilMoisture", "slope"] if c in df.columns]
        fig = px.scatter_map(
            df,
            lat="lat",
            lon="lon",
            size="riskScore",
            color="riskLevel",
            hover_name="location",
            hover_data=hover_cols,
            zoom=5.8,
            center={"lat": 26.0, "lon": 92.5},
            height=650,
            color_discrete_map=RISK_META,
            map_style="open-street-map"
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        # Fallback to standard streamlit map if map tiles fail
        st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"})[["latitude", "longitude"]], zoom=6)

# ----------------------------------------------------
# 3. AI PREDICTION
# ----------------------------------------------------
elif page == "AI Prediction":
    st.subheader("AI Landslide Risk Prediction")
    with st.form("risk"):
        a, b, c = st.columns(3)
        r24 = a.number_input("Rainfall — 24h (mm)", 0.0, 500.0, 120.0)
        r72 = b.number_input("Rainfall — 72h (mm)", 0.0, 1000.0, 280.0)
        soil = c.slider("Soil Moisture (%)", 0, 100, 75)

        d, e, f = st.columns(3)
        slope = d.slider("Slope (°)", 0, 70, 35)
        elev = e.number_input("Elevation (m)", 0.0, 5000.0, 1200.0)
        ndvi = f.slider("NDVI", 0.0, 1.0, 0.40)

        g, h, i = st.columns(3)
        hist = g.slider("Historical susceptibility", 0, 100, 50)
        eqm = h.number_input("Nearest earthquake magnitude", 0.0, 10.0, 0.0)
        eqd = i.number_input("Earthquake distance (km)", 0.0, 1000.0, 999.0)
        submitted = st.form_submit_button("Run AI Risk Assessment", use_container_width=True)

    if submitted:
        payload = {
            "rainfall24h": r24,
            "rainfall72h": r72,
            "soilMoisture": soil,
            "slope": slope,
            "elevation": elev,
            "ndvi": ndvi,
            "historicalDensity": hist,
            "earthquakeMagnitude": eqm,
            "earthquakeDistanceKm": eqd,
            "earthquakeDepthKm": 0
        }
        result = api_post("/api/risk", payload) or predict(payload)
        st.metric("Risk Score", f"{result['riskScore']}/100")
        color = "red" if result["riskLevel"] in ["CRITICAL", "HIGH"] else "orange" if result["riskLevel"] == "MODERATE" else "green"
        st.markdown(f"### :{color}[{result['riskLevel']}]")
        st.write(f"Model: **{result.get('model', 'Ensemble')}** · Estimated probability: **{result.get('probability', 0.0)*100:.1f}%**")
        
        for x in result.get("contributingFactors", []):
            st.progress(min(1.0, float(x["pct"]) / 100.0), text=f"{x['label']} — {x['pct']}%")
        st.warning("This model is an MVP/demo and must be validated with authoritative NER historical/event data before operational warning decisions.")

# ----------------------------------------------------
# 4. EARTHQUAKES
# ----------------------------------------------------
elif page == "Earthquakes":
    st.subheader("Recent Earthquake Activity — NER")
    days = st.slider("Lookback (days)", 1, 30, 7)
    events = api_get("/api/earthquakes", {"days": days})
    if events and not (len(events) == 1 and "error" in events[0]):
        df = pd.DataFrame(events)
        st.metric("Events returned", len(df))
        cols = [c for c in ["time", "magnitude", "depthKm", "place", "lat", "lon"] if c in df.columns]
        st.dataframe(df[cols], hide_index=True, use_container_width=True)
        if not df.empty and "lat" in df.columns and "lon" in df.columns:
            st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"})[["latitude", "longitude"]], zoom=5)
    else:
        st.error("Earthquake feed unavailable. Check internet/API connectivity.")

# ----------------------------------------------------
# 5. FIELD REPORTS
# ----------------------------------------------------
elif page == "Field Reports":
    st.subheader("Field Incident Reporting")
    with st.form("report"):
        loc = st.text_input("Location")
        state = st.selectbox("State", [x["name"] for x in STATE_LABELS])
        typ = st.selectbox("Type", ["Slope crack", "Rockfall", "Landslide", "Road blockage", "Soil movement", "Water seepage", "Other"])
        sev = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        desc = st.text_area("Observation")
        lat = st.number_input("Latitude", -90.0, 90.0, 25.5)
        lon = st.number_input("Longitude", -180.0, 180.0, 91.3)
        offline = st.checkbox("Save as pending/offline report")
        ok = st.form_submit_button("Submit Field Report", use_container_width=True)

    if ok and loc.strip():
        item = api_post("/api/reports", {
            "location": loc, "state": state, "lat": lat, "lon": lon,
            "type": typ, "severity": sev, "description": desc, "synced": not offline
        })
        if item:
            st.success("Report stored in backend database.")
        else:
            st.error("Backend unavailable. Keep the report locally and retry when connected.")

    rows = api_get("/api/reports") or []
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

# ----------------------------------------------------
# 6. INFRASTRUCTURE
# ----------------------------------------------------
elif page == "Infrastructure":
    st.subheader("Critical Infrastructure Vulnerability Registry")
    st.dataframe(pd.DataFrame(api_get("/api/infrastructure") or INFRASTRUCTURE), hide_index=True, use_container_width=True)

# ----------------------------------------------------
# 7. ANALYTICS
# ----------------------------------------------------
elif page == "Analytics":
    st.subheader("Risk Analytics")
    live = api_get("/api/hotspots", {"refresh": True}) or HOTSPOTS
    df = prep_df(live)

    st.plotly_chart(
        px.bar(df.sort_values("riskScore"), x="location", y="riskScore", color="state", title="Current Risk by Hotspot"),
        use_container_width=True
    )
    st.plotly_chart(
        px.scatter(df, x="rainfall24h", y="riskScore", size="slope", color="state", hover_name="location", title="Rainfall vs Risk"),
        use_container_width=True
    )

# ----------------------------------------------------
# 8. SYSTEM STATUS
# ----------------------------------------------------
elif page == "System Status":
    st.subheader("System Status")
    health = api_get("/health")
    st.success("Backend ONLINE") if health else st.error("Backend OFFLINE — frontend can still show demo data")
    st.write("ML model:", "LOADED" if load_model() else "NOT TRAINED")
    st.write("Backend URL:", API)
    st.info("Operational deployment requires validated NER training data, calibrated thresholds, monitoring, authentication, and an approved alerting procedure.")