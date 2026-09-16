import math
import requests
from datetime import datetime, timezone

USGS_URL="https://earthquake.usgs.gov/fdsnws/event/1/query"
NER_BBOX={"minlatitude":21.5,"maxlatitude":30.5,"minlongitude":88.0,"maxlongitude":97.5}

def haversine_km(lat1,lon1,lat2,lon2):
    r=6371.0
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

def get_earthquakes(days=7,limit=50):
    params={"format":"geojson","orderby":"time","limit":limit,"starttime":f"NOW-{days}days","endtime":"NOW",**NER_BBOX}
    try:
        r=requests.get(USGS_URL,params=params,timeout=15); r.raise_for_status()
        out=[]
        for f in r.json().get("features",[]):
            c=f.get("geometry",{}).get("coordinates",[]); p=f.get("properties",{})
            if len(c)<3: continue
            out.append({"id":f.get("id"),"magnitude":p.get("mag"),"place":p.get("place"),"time":datetime.fromtimestamp(p.get("time",0)/1000,tz=timezone.utc).isoformat(),"lat":c[1],"lon":c[0],"depthKm":c[2],"url":p.get("url")})
        return out
    except Exception as e:
        return [{"error":str(e)}]

def nearest_event(lat,lon,events):
    best=None
    for e in events:
        if e.get("lat") is None: continue
        d=haversine_km(lat,lon,e["lat"],e["lon"])
        if best is None or d<best["distanceKm"]:
            best={**e,"distanceKm":round(d,1)}
    return best
