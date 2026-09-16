from pathlib import Path
import math
import joblib

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "landslide_model.joblib"
FEATURES = ["rainfall24h","rainfall72h","soilMoisture","slope","elevation","ndvi","historicalDensity","earthquakeMagnitude","earthquakeDistanceKm","earthquakeDepthKm"]

def level_from_score(score: float) -> str:
    if score >= 76: return "CRITICAL"
    if score >= 51: return "HIGH"
    if score >= 26: return "MODERATE"
    return "LOW"

def load_model():
    if MODEL_PATH.exists():
        try: return joblib.load(MODEL_PATH)
        except Exception: return None
    return None

def _norm(v, lo, hi):
    return max(0.0, min(1.0, (float(v)-lo)/(hi-lo)))

def heuristic_score(d):
    rain = 0.35*_norm(d.get("rainfall24h",0),0,180) + 0.20*_norm(d.get("rainfall72h",0),0,450)
    soil = 0.18*_norm(d.get("soilMoisture",0),20,100)
    slope = 0.12*_norm(d.get("slope",0),10,60)
    hist = 0.08*_norm(d.get("historicalDensity",0),0,100)
    veg = 0.04*(1-_norm(d.get("ndvi",0.5),0.2,0.8))
    eq_mag = float(d.get("earthquakeMagnitude",0) or 0)
    eq_dist = float(d.get("earthquakeDistanceKm",999) or 999)
    eq = 0 if eq_mag <= 0 else 0.08*_norm(eq_mag,2.5,7.5)*(1-_norm(eq_dist,0,300))
    score = 100*(rain+soil+slope+hist+veg+eq)
    return max(0,min(100,score))

def predict(features):
    model_bundle = load_model()
    x = [[float(features.get(f,0) or 0) for f in FEATURES]]
    if model_bundle:
        model = model_bundle["model"]
        try:
            p = float(model.predict_proba(x)[0][1])
            score = p*100
            method = "Random Forest"
        except Exception:
            score = heuristic_score(features); p=score/100; method="Hybrid fallback"
    else:
        score = heuristic_score(features); p=score/100; method="Physics-inspired fallback"
    level = level_from_score(score)
    contrib = []
    checks = [
      ("Heavy recent rainfall", min(100, 100*_norm(features.get("rainfall24h",0),40,180))),
      ("High soil moisture", min(100, 100*_norm(features.get("soilMoisture",0),45,100))),
      ("Steep slope", min(100, 100*_norm(features.get("slope",0),20,60))),
      ("Historical susceptibility", float(features.get("historicalDensity",0))),
      ("Low vegetation index", 100*(1-_norm(features.get("ndvi",0.5),0.2,0.8))),
    ]
    if float(features.get("earthquakeMagnitude",0) or 0)>0:
        checks.append(("Recent nearby earthquake", min(100, 100*_norm(features.get("earthquakeMagnitude",0),2.5,7.5)*(1-_norm(features.get("earthquakeDistanceKm",999),0,300)))))
    total=sum(max(0,x[1]) for x in checks) or 1
    for label,val in checks:
        contrib.append({"label":label,"pct":round(100*val/total,1)})
    return {"riskScore":round(score,1),"riskLevel":level,"probability":round(p,4),"confidence":round(100*(0.55+0.45*max(0,min(1,abs(p-0.5)*2))),1),"model":method,"contributingFactors":contrib}
