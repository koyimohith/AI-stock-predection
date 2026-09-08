@echo off
TITLE NIFTY AI Stock Predictor - Master Launcher
echo =======================================================
echo    Launching NIFTY AI Stock Predictor Full Project
echo =======================================================
echo.
echo 1. Starting Flask API Backend...
start /b start_api.bat

echo 2. Starting Streamlit Frontend Dashboard...
start /b start.bat

echo.
echo Both services are fully launched in separate windows.
echo You can access the Dashboard at: http://localhost:8501
echo.
echo You may close this launcher window now.
pause
