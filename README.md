# 📈 NIFTY AI Stock Prediction Dashboard

> **AI-powered stock market analysis and forecasting platform for NIFTY 50 and supported market symbols.**

NIFTY AI is a Python-based financial analytics platform that combines **machine learning, technical analysis, market data, and sentiment analysis** into a unified dashboard.

The project provides two interfaces using the same analysis backend:

* 🖥️ **Streamlit Dashboard** — Interactive charts, indicators, screening, sentiment, and predictions.
* 🌐 **Flask REST API + Web Frontend** — Browser-based interface built with Flask, HTML, CSS, and JavaScript.

> ⚠️ **Disclaimer:** This project is intended for educational and research purposes only. Predictions, signals, and recommendations are not financial advice. Market data may be delayed, unavailable, or affected by third-party provider limitations.

---

## 🚀 Features

* 📊 Historical and live market-data retrieval using `yfinance`
* 🤖 LSTM and GRU deep-learning forecasting models
* 📈 Moving averages, RSI, volatility, trend analysis, and support/resistance
* 🔎 Dynamic stock screening and correlation analysis
* 📰 Sentiment analysis using TextBlob
* 📉 Interactive price and forecasting visualizations
* 🔄 Live price refresh in the Streamlit dashboard
* 🌐 JSON REST API for market and sentiment data
* 🐳 Docker support
* 🪟 Windows batch launchers

---

## 🧠 System Architecture

```text
                    Market Data
                         │
                         ▼
                Data Processing Layer
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
   Technical Analysis          Sentiment Analysis
            │                         │
            └────────────┬────────────┘
                         ▼
                  ML Forecasting
                   ┌─────┴─────┐
                   ▼           ▼
                 LSTM         GRU
                   └─────┬─────┘
                         ▼
                Analysis & Signals
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         Streamlit              Flask API
          Dashboard           + Web Frontend
```

---

## 🛠️ Technology Stack

| Category         | Technology            |
| ---------------- | --------------------- |
| Language         | Python 3.9+           |
| Dashboard        | Streamlit             |
| Backend          | Flask                 |
| Frontend         | HTML, CSS, JavaScript |
| Machine Learning | TensorFlow / Keras    |
| Models           | LSTM, GRU             |
| Market Data      | yfinance              |
| Data Processing  | Pandas, NumPy         |
| Sentiment        | TextBlob              |
| Deployment       | Docker                |

---

## 📁 Project Structure

```text
NIFTY-AI-Stock-Prediction/
│
├── app.py                  # Streamlit dashboard
├── api.py                  # Flask API & web server
├── index.html              # Web frontend
├── script.js               # Frontend JavaScript
├── style.css               # Frontend styling
│
├── data_fetch.py           # Market & sentiment data
├── analysis.py             # Technical analysis
├── model.py                # Forecasting & evaluation
├── screener.py             # Screening & correlation
├── tickers.py              # Supported symbols
│
├── lstm_model.keras        # LSTM model
├── gru_model.keras         # GRU model
├── config.json             # Configuration
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker configuration
│
├── start.bat               # Streamlit launcher
├── start_api.bat           # Flask launcher
└── run_project.bat         # Full project launcher
```

---

## ⚙️ Requirements

* Python **3.9 or later**
* Internet connection for live `yfinance` data
* TensorFlow-compatible environment
* Git
* Docker *(optional)*

---

## 📥 Installation

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>

python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Run the Dashboard

### Streamlit

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

### Flask Web Application

```bash
python api.py
```

Open:

```text
http://localhost:5000
```

---

## 🔌 API Endpoints

| Endpoint                          | Description                                     |
| --------------------------------- | ----------------------------------------------- |
| `GET /`                           | Web frontend                                    |
| `GET /api/data?ticker=^NSEI`      | Market data, indicators, trend & recommendation |
| `GET /api/realtime?ticker=^NSEI`  | Realtime data                                   |
| `GET /api/sentiment?ticker=^NSEI` | Sentiment label & score                         |

Example:

```text
http://localhost:5000/api/data?ticker=^NSEI
```

---

## 🐳 Docker

Build the image:

```bash
docker build -t nifty-ai-dashboard .
```

Run:

```bash
docker run --rm -p 8501:8501 nifty-ai-dashboard
```

Then open:

```text
http://localhost:8501
```

---

## 🔬 Future Enhancements

* Transformer-based forecasting
* FinBERT financial sentiment analysis
* Explainable AI with SHAP
* Advanced backtesting
* Portfolio optimization
* Automated model retraining
* Risk analysis and volatility forecasting
* Multi-market support
* Cloud deployment

---

## 🔐 Security

Before publishing:

* Add `.env` and credentials to `.gitignore`
* Do not commit API keys or secrets
* Review large model and dataset files
* Exclude temporary files and caches
* Validate public API inputs

---

## 📤 GitHub Publishing

```bash
git init
git add .
git commit -m "Initial project release"
git branch -M main

git remote add origin https://github.com/<your-username>/<your-repository>.git

git push -u origin main
```

---

## 👨‍💻 Author

**Mohith**
Computer Science | AI & Machine Learning | Software Development

---

## ⚠️ Disclaimer

This application is **not a financial advisory system**. All predictions, technical signals, sentiment scores, and recommendations are experimental outputs intended for **educational and research purposes only**.

Financial markets are inherently unpredictable. Past performance and machine-learning predictions do not guarantee future results.

**Always conduct independent research before making financial decisions.**
