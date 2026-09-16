from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import json
import sqlite3
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data.sample_data import HOTSPOTS, INFRASTRUCTURE
from utils.risk import predict
from utils.earthquake import get_earthquakes, nearest_event
from utils.weather import get_weather

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "storage" / "geosuraksha.db"


def db():
    (ROOT / "storage").mkdir(exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            state TEXT,
            lat REAL,
            lon REAL,
            type TEXT,
            severity TEXT,
            description TEXT,
            created_at TEXT,
            synced INTEGER
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotspot_id TEXT,
            level TEXT,
            title TEXT,
            reasons TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )
    c.commit()
    return c


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables exist
    conn = db()
    conn.close()
    yield
    # Shutdown logic (if any) goes here


app = FastAPI(
    title="GeoSuraksha AI API",
    version="1.1.0",
    description="AI-based landslide risk monitoring MVP for NER",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def model_to_dict(model_obj):
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump()
    return model_obj.dict()


class Report(BaseModel):
    location: str
    state: str = "Unspecified"
    lat: float = 0.0
    lon: float = 0.0
    type: str = "Other"
    severity: str = "Medium"
    description: str = ""
    synced: bool = True


class RiskRequest(BaseModel):
    rainfall24h: float = 0.0
    rainfall72h: float = 0.0
    soilMoisture: float = 50.0
    slope: float = 20.0
    elevation: float = 500.0
    ndvi: float = 0.5
    historicalDensity: float = 20.0
    earthquakeMagnitude: float = 0.0
    earthquakeDistanceKm: float = 999.0
    earthquakeDepthKm: float = 0.0


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def build_live_hotspots():
    events = []
    try:
        events = get_earthquakes(7, 100)
    except Exception:
        events = []

    result = []
    for h in HOTSPOTS:
        d = dict(h)
        try:
            weather = get_weather(h["lat"], h["lon"])
            if weather and not weather.get("error"):
                d["rainfall24h"] = weather.get("rainfall24h", d.get("rainfall24h", 0))
                d["rainfall72h"] = weather.get("rainfall72h", d.get("rainfall72h", 0))
                if weather.get("soilMoisture") is not None:
                    d["soilMoisture"] = weather["soilMoisture"]
                d["weatherSource"] = weather.get("source", "Open-Meteo")
            else:
                d["weatherSource"] = "Demo fallback"
        except Exception:
            d["weatherSource"] = "Demo fallback"

        try:
            eq = nearest_event(h["lat"], h["lon"], events) if events and not events[0].get("error") else None
            d["earthquakeMagnitude"] = (eq.get("magnitude") or 0) if eq else 0
            d["earthquakeDistanceKm"] = (eq.get("distanceKm") or 999) if eq else 999
            d["earthquakeDepthKm"] = (eq.get("depthKm") or 0) if eq else 0
        except Exception:
            d["earthquakeMagnitude"] = 0
            d["earthquakeDistanceKm"] = 999
            d["earthquakeDepthKm"] = 0

        try:
            prediction = predict(d)
            d.update({
                "riskScore": prediction.get("riskScore", d.get("riskScore", 50)),
                "riskLevel": prediction.get("riskLevel", "MODERATE"),
                "probability": prediction.get("probability", 0.5),
                "confidence": prediction.get("confidence", 0.5),
                "contributingFactors": prediction.get("contributingFactors", [])
            })
        except Exception:
            d.setdefault("riskScore", 50)
            d.setdefault("riskLevel", "MODERATE")

        result.append(d)
    return result


def maybe_create_alert(h):
    if h.get("riskLevel") not in ("HIGH", "CRITICAL"):
        return None
    c = db()
    existing = c.execute(
        "SELECT * FROM alerts WHERE hotspot_id=? AND status IN ('NEW','ACKNOWLEDGED') ORDER BY id DESC LIMIT 1",
        (h["id"],)
    ).fetchone()
    if existing:
        c.close()
        return dict(existing)

    factors = h.get("contributingFactors", [])
    reasons = [x["label"] for x in sorted(factors, key=lambda x: x.get("pct", 0), reverse=True)[:3]] if factors else ["High risk indicator"]
    title = f"{h.get('riskLevel')} landslide risk at {h.get('location')}"

    cur = c.execute(
        "INSERT INTO alerts(hotspot_id,level,title,reasons,status,created_at) VALUES(?,?,?,?,?,?)",
        (h["id"], h.get("riskLevel"), title, json.dumps(reasons), "NEW", now_iso())
    )
    c.commit()
    row = c.execute("SELECT * FROM alerts WHERE id=?", (cur.lastrowid,)).fetchone()
    c.close()
    return dict(row) if row else None


@app.get("/health")
def health():
    return {"status": "ok", "service": "GeoSuraksha AI", "time": now_iso()}


@app.get("/api/hotspots")
def hotspots(refresh: bool = False):
    if refresh:
        live = build_live_hotspots()
        for h in live:
            maybe_create_alert(h)
        return live
    return [dict(h) for h in HOTSPOTS]


@app.get("/api/hotspots/{hotspot_id}")
def hotspot(hotspot_id: str):
    for h in HOTSPOTS:
        if h["id"] == hotspot_id:
            return h
    raise HTTPException(404, "Hotspot not found")


@app.post("/api/risk")
def risk(req: RiskRequest):
    return predict(model_to_dict(req))


@app.get("/api/live-risk/{hotspot_id}")
def live_risk(hotspot_id: str):
    for h in HOTSPOTS:
        if h["id"] == hotspot_id:
            live = build_live_hotspots()
            for item in live:
                if item["id"] == hotspot_id:
                    maybe_create_alert(item)
                    return item
    raise HTTPException(404, "Hotspot not found")


@app.get("/api/earthquakes")
def earthquakes(days: int = 7):
    return get_earthquakes(max(1, min(days, 30)), 100)


@app.get("/api/weather")
def weather(lat: float, lon: float):
    return get_weather(lat, lon)


@app.get("/api/infrastructure")
def infrastructure():
    return INFRASTRUCTURE


@app.get("/api/alerts")
def alerts(status: str | None = None):
    c = db()
    if status:
        rows = c.execute("SELECT * FROM alerts WHERE status=? ORDER BY id DESC", (status.upper(),)).fetchall()
    else:
        rows = c.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    out = []
    for row in rows:
        item = dict(row)
        try:
            item["reasons"] = json.loads(item["reasons"])
        except Exception:
            pass
        out.append(item)
    c.close()
    return out


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    c = db()
    row = c.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
    if not row:
        c.close()
        raise HTTPException(404, "Alert not found")
    c.execute("UPDATE alerts SET status='ACKNOWLEDGED' WHERE id=?", (alert_id,))
    c.commit()
    updated = c.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
    c.close()
    return dict(updated)


@app.get("/api/reports")
def reports():
    c = db()
    rows = [dict(x) for x in c.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()]
    c.close()
    return rows


@app.post("/api/reports")
def create_report(report: Report):
    c = db()
    now = now_iso()
    cur = c.execute(
        "INSERT INTO reports(location,state,lat,lon,type,severity,description,created_at,synced) VALUES(?,?,?,?,?,?,?,?,?)",
        (
            report.location,
            report.state,
            report.lat,
            report.lon,
            report.type,
            report.severity,
            report.description,
            now,
            int(report.synced)
        )
    )
    c.commit()
    item = {"id": cur.lastrowid, **model_to_dict(report), "created_at": now}
    c.close()
    return item