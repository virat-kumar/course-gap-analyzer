@echo off
echo ==========================================
echo Killing existing frontend/streamlit processes...
echo ==========================================

REM Kill processes using port 8501
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    echo Killing process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Wait for processes to terminate
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo Starting Frontend Server on ALL interfaces
echo Host: 0.0.0.0:8501
echo Access: http://localhost:8501
echo Network: http://192.168.10.150:8501
echo ==========================================
echo.

cd /d "%~dp0"
call conda activate course-gap-analyzer
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

