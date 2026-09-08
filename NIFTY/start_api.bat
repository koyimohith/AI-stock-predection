@echo off
TITLE AI Stock REST API (Flask)
echo *******************************************************
echo Starting AI Stock REST API Server...
echo *******************************************************
echo.
echo Make sure you have installed requirements:
echo pip install -r requirements.txt
echo.
echo The backend will start on http://localhost:5000
echo You can safely open index.html in your browser.
echo.
echo Press Ctrl+C to stop the server at any time.
echo.

if exist ".\.venv\Scripts\activate.bat" call ".\.venv\Scripts\activate.bat"
python api.py
pause
