import requests
from datetime import datetime, timezone

OPEN_METEO="https://api.open-meteo.com/v1/forecast"

def get_weather(lat,lon):
    params={"latitude":lat,"longitude":lon,"hourly":"precipitation,soil_moisture_0_to_7cm","forecast_days":3,"past_days":3,"timezone":"UTC"}
    try:
        r=requests.get(OPEN_METEO,params=params,timeout=15); r.raise_for_status(); data=r.json(); h=data["hourly"]
        times=[datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in h["time"]]
        now=datetime.now(timezone.utc)
        past=[i for i,t in enumerate(times) if t<=now]
        last24=past[-24:] if len(past)>=24 else past
        last72=past[-72:] if len(past)>=72 else past
        precip=h.get("precipitation",[])
        soil=h.get("soil_moisture_0_to_7cm",[])
        r24=round(sum((precip[i] or 0) for i in last24),1)
        r72=round(sum((precip[i] or 0) for i in last72),1)
        sm=[soil[i] for i in last24 if soil[i] is not None]
        soil_pct=round(100*sum(sm)/len(sm),1) if sm else None
        forecast=[]
        for i,t in enumerate(times):
            if t>now and len(forecast)<72:
                forecast.append({"time":t.isoformat(),"precipitation":precip[i] or 0})
        return {"rainfall24h":r24,"rainfall72h":r72,"soilMoisture":soil_pct,"forecast":forecast,"source":"Open-Meteo"}
    except Exception as e:
        return {"error":str(e),"source":"Open-Meteo"}
