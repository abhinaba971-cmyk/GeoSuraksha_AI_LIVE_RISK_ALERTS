# GeoSuraksha AI — Complete MVP

AI-Based Early Warning & Landslide Risk Monitoring System for the Northeast Region (NER), built from the original `app_ml(3).py` prototype.

## Architecture

Streamlit frontend → FastAPI backend → risk/earthquake/weather services → SQLite persistence → ML model.

## Run on Windows

1. Open terminal in this folder.
2. `python -m venv .venv`
3. `.venv\\Scripts\\activate`
4. `pip install -r requirements.txt`
5. `python -m ml.train`
6. Terminal A: `uvicorn backend.main:app --reload --port 8000`
7. Terminal B: `streamlit run frontend/app.py`

Or use `run_backend.bat` and `run_frontend.bat` in two terminals.

## Data sources

- Earthquakes: USGS Earthquake Hazards Program public FDSN event service.
- Weather/rainfall/soil moisture: Open-Meteo public forecast API.
- Terrain, satellite/NDVI and historical landslide inventory are currently represented by prototype fields and must be connected to authoritative datasets before operational deployment.

## ML warning

`ml/train.py` intentionally generates synthetic training data so the project runs end-to-end. This is NOT a validated operational landslide model. Replace the training dataset with georeferenced historical landslide/non-landslide observations from NER and perform spatial/temporal holdout validation, calibration, lead-time evaluation, and false-alarm analysis.

## Production upgrades

1. PostgreSQL/PostGIS instead of SQLite.
2. Authentication/RBAC.
3. Persistent sensor ingestion and data-quality checks.
4. Satellite/DEM processing pipeline.
5. Real field GPS/photo uploads and offline PWA synchronization.
6. SMS/push integration with human verification/escalation.
7. Docker/cloud deployment and monitoring.
