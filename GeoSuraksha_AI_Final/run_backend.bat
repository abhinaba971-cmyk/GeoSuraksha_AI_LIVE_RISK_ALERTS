@echo off
cd /d %~dp0
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python -m ml.train
uvicorn backend.main:app --host 127.0.0.1 --port 8000
