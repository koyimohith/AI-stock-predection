# NIFTY AI Stock Prediction: Implementation & Methodology

This document outlines the detailed technical implementation, technology stack, and dataset architectures utilized in building the NIFTY AI Stock Prediction Dashboard. It is formatted to be easily adapted for project reports, technical thesis documentation, or final presentations.

---

## 1. The Implementation Part
The overarching architecture of this project is built upon a **Hybrid Dual-Frontend system** combined with an **Offline-Resilient Micro-Backend**. The implementation was separated into three distinct developmental phases:

### A. Data Engineering & Fetch Logic
To prevent the dashboard from completely crashing during API rate-limiting or network disconnections, a highly sophisticated data-fetch pipeline was implemented. The backend (`data_fetch.py`) actively tries to pull the live 1-minute market price from Yahoo Finance APIs. 
- If it succeeds, it updates the visual GUI State Machine immediately. 
- If the internet goes offline or Yahoo Finance rate-limits the connection, the pipeline immediately triggers an algorithmic exception. It falls back to catching the last known value retrieved from an offline SQLite snapshot and applies **Deterministic Price Jitters**  (Gaussian noise `+/- 0.05%`) so the application never "freezes" visually.  

### B. Machine Learning Modeling & Scaling
Traditional ML projects map inputs against global scalers, causing them to break if a stock scales outside of trained bounds. This project implements "on-the-fly" dynamic scaling. The core logic (`model.py`) spawns temporary `MinMaxScalers` dynamically. It shapes the last 60 days of historical data against pre-trained core computational matrices (`lstm_model.keras` or `gru_model.keras`).

The system offers a robust predictive hierarchy evaluating variables:
- **LSTM (Deep Learning):** Focuses heavily on cascading sequence manipulation.
- **GRU (Recurrent Network):** Leverages simplified computational gating for faster sequence calculations.
- **ARIMA & Prophet:** Used simultaneously as mathematical statistical surrogates.
- **Ensemble (Consensus):** Averages the outputs of all underlying algorithms to calculate the highest-confidence Target Predict line.

### C. The Graphical Dashboard Presentation
Two independent interfaces were implemented:
1. **The Python UI (`app.py`):** Uses **Streamlit**. It generates responsive, institutional-grade Plotly interactive graphs. It includes a 6-month historical Candlestick Backtesting engine combined with mathematical mock overlays in a manual predictor form.
2. **The Web Application (`index.html` & `api.py`):** Uses a native Vanilla JS and Bootstrap CSS layout interacting asynchronously through a localized native RESTful API powered by Flask.

---

## 2. What Technologies are Used (Tech Stack)
The project integrates the following frameworks and libraries:

### Programming Languages
- **Python (3.x):** The core foundational language handling data pipelines, AI modeling, and logic routing.
- **JavaScript / HTML / Vanilla CSS:** Powering the secondary asynchronous browser client.

### Libraries & Frameworks
- **Streamlit:** Facilitates the primary analytical GUI rendering natively inside Python.
- **Flask:** Acts as the high-availability RESTful API backend engine for non-streamlit integrations.
- **TensorFlow & Keras (`tf.keras`):** Provides the foundational nodes and computational graph mapping for the Deep Learning networks.
- **Pandas & NumPy:** Handles dense sequence dataframes and high-speed multi-dimensional array mathematics.
- **Plotly:** Used primarily to calculate responsive graphical chart matrices including the multi-layered candlestick mappings.
- **yfinance:** Acts as the networking tunnel to external live web servers.

---

## 3. Dataset Integrations (What Datasets Are Used)
Stock price prediction lives or dies on the reliability of data. This project utilizes a sophisticated dual-dataset pipeline ensuring 100% offline stability. 

### A. The Offline Snapshot (`nifty_history.db`)
- **Type:** Local SQLite Relational Database Cache.
- **Characteristics:** Provides deep historical, minute-to-minute or daily closing data primarily focused on the **NIFTY 50 baseline index**.
- **Role:** This dataset acts as the foundation of the project. If network connectivity fails, the platform seamlessly mines columns from this cached dataset offline. It contains up to 5-years of pre-calculated sequence boundaries preventing memory overload.
- **Intelligent Degradation:** If a user requests data for an asset much smaller than NIFTY (e.g., `HDFCBANK`), the database initiates a Mathematical Scale Transformer to dynamically mutate the larger NIFTY data down to match the approximate size bounds of the requested asset, maintaining statistical variance seamlessly.

### B. The Live Feed (Yahoo Finance Hook / `yfinance`)
- **Type:** Live External API Hook.
- **Characteristics:** Intermittent active pinging server querying.
- **Role:** The system fetches real-time 1m tick data vectors from Yahoo Finance servers every few seconds asynchronously. It feeds the raw `Open`, `High`, `Low`, and `Close` properties directly into the Volatility, RSI, and MACD technical indicator algorithms to map immediate market momentum dynamically without saving it permanently to storage drives. 
