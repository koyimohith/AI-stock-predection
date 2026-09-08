# NIFTY AI Stock Prediction Dashboard

A Python-based stock analysis and forecasting dashboard for NIFTY 50 and supported market symbols. The project provides two ways to use the same analysis backend:

- A Streamlit dashboard for interactive charts, indicators, screening, sentiment, and predictions.
- A Flask API with a vanilla JavaScript frontend for browser-based deployment.

> **Disclaimer:** This project is for education and research only. Predictions, signals, and recommendations are not financial advice. Market data may be delayed, unavailable, or affected by provider limits.

## Features

- Historical market-data retrieval with fallback handling for unavailable data.
- LSTM and GRU forecasting models with Keras model files included in the repository.
- Technical analysis including moving averages, RSI, volatility, trend analysis, and support/resistance levels.
- Stock screener and correlation analysis utilities.
- Sentiment analysis support through TextBlob and market-data integrations.
- Live price refresh in the Streamlit dashboard.
- JSON API endpoints for chart data and sentiment data.
- Optional Docker and Windows batch launchers.

## Requirements

- Python 3.9 or later
- Internet access for live data when using the `yfinance` integration
- TensorFlow-compatible hardware and Python environment

## Installation

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>

python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt
# .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the Project

### Streamlit dashboard

This is the recommended entry point:

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501` in a browser.

On Windows, `start.bat` runs the same dashboard. `run_project.bat` starts both the Streamlit dashboard and Flask API.

### Flask API and web frontend

Start the API and frontend together from the project directory:

```bash
python api.py
```

Open `http://localhost:5000`. The Flask server serves `index.html` and the static JavaScript/CSS assets.

On Windows, `start_api.bat` starts the Flask server.

### Docker

Build and run the Streamlit container:

```bash
docker build -t nifty-ai-dashboard .
docker run --rm -p 8501:8501 nifty-ai-dashboard
```

Then open `http://localhost:8501`.

## API Endpoints

When Flask is running on port 5000:

| Endpoint | Description |
| --- | --- |
| `GET /` | Serves the web frontend |
| `GET /api/data?ticker=^NSEI` | Historical prices, indicators, live price, trend, and recommendation |
| `GET /api/realtime?ticker=^NSEI` | Alias for `/api/data` |
| `GET /api/sentiment?ticker=^NSEI` | Returns sentiment label and score |

Example:

```text
http://localhost:5000/api/data?ticker=^NSEI
```

## Project Structure

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit dashboard |
| `api.py` | Flask API and static-file server |
| `index.html`, `script.js`, `style.css` | Browser frontend |
| `data_fetch.py` | Historical, live-price, and sentiment data access |
| `analysis.py` | Technical indicators and recommendation logic |
| `model.py` | Forecasting and model evaluation |
| `screener.py` | Dynamic screening and correlation analysis |
| `tickers.py` | Supported ticker definitions |
| `lstm_model.keras`, `gru_model.keras` | Saved Keras forecasting models |
| `config.json` | Application configuration |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Streamlit container definition |

## GitHub Publishing

After creating an empty repository on GitHub, run these commands from this folder:

```bash
git init
git add .
git commit -m "Initial project release"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repository>.git
git push -u origin main
```

Before publishing, review large model/data files and add secrets or local environment files to `.gitignore`.
