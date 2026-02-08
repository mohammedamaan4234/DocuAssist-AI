@echo off
REM DocuAssist AI - Development Server Startup
echo.
echo =========================================
echo  DocuAssist AI - Starting Development
echo =========================================
echo.
echo Setting up Python environment...
cd /d "d:\AI Capstone\Task"

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
