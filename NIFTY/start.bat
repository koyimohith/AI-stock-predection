@echo off
TITLE AI Stock Predictor Server (Streamlit)
echo *******************************************************
echo Starting AI Stock Predictor Web Application...
echo *******************************************************
echo.
echo If this is your first time running, make sure you ran:
echo pip install -r requirements.txt
echo.
echo The dashboard will be launched automatically in your browser.
echo.
echo Press Ctrl+C to stop the server at any time.
echo.

if exist ".\.venv\Scripts\activate.bat" call ".\.venv\Scripts\activate.bat"
streamlit run app.py
pause
