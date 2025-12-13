@echo off
echo Starting Backend Server on all interfaces (0.0.0.0:8000)...
cd /d "%~dp0"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
pause


