from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

# Import our backend analysis tools
from data_fetch import fetch_historical_data, get_sentiment, get_live_price
from analysis import calculate_technical_indicators, analyze_trend, get_recommendation_details
from model import predict_future, evaluate_model

app = Flask(__name__, static_folder='.', static_url_path='')
# Enable CORS so the local frontend running (even just file://) can hit localhost:5000
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def safe_list(l):
    """Safely converts NaN values to None for compliant JSON serialization"""
    return [None if pd.isna(x) else float(x) if isinstance(x, (int, float, np.number)) else str(x) for x in l]

# Simple memory cache to prevent Keras from hanging on every polling request
_prediction_cache = {}

@app.route('/api/data')
@app.route('/api/realtime')
def api_data():
    ticker = request.args.get('ticker', '^NSEI')
    # Use standard 5y historical fetch from SQLite caching / yf.
    df = fetch_historical_data(ticker, period="5y")
    
    if df.empty:
        return jsonify({"error": "No data found for symbol"}), 404
        
    df = calculate_technical_indicators(df)
    
    dates = df['Date'].tolist()
    close_vals = df['Close'].tolist()
    open_vals = df['Open'].tolist() if 'Open' in df.columns else []
    high_vals = df['High'].tolist() if 'High' in df.columns else []
    low_vals = df['Low'].tolist() if 'Low' in df.columns else []
    
    ma50 = df['MA50'].tolist() if 'MA50' in df.columns else []
    ma200 = df['MA200'].tolist() if 'MA200' in df.columns else []
    rsi = df['RSI'].tolist() if 'RSI' in df.columns else []
    
    # In some models, calculating realtime fast updates is better. We'll use the latest close.
    live_price, _ = get_live_price(ticker)
    current_price = float(live_price) if live_price else float(close_vals[-1])
    highest_price = float(max(high_vals)) if high_vals else current_price
    
    trend = analyze_trend(close_vals[-15:] if len(close_vals) >= 15 else close_vals)
    
    vol_latest = float(df['Volatility'].iloc[-1]) if 'Volatility' in df.columns else 0.15
    rsi_latest = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else 50.0
    
    # Fallback to current price if model needs more data.
    global _prediction_cache
    if ticker not in _prediction_cache:
        preds = predict_future(df.tail(1000), days=1, model_type="LSTM")
        _prediction_cache[ticker] = preds
    else:
        preds = _prediction_cache[ticker]
        
    predicted_price = float(preds[0]) if preds else current_price
    
    rec_data = get_recommendation_details(current_price, predicted_price, trend, vol_latest, rsi_latest)
    
    # Safely compute daily growth
    prev_close = float(close_vals[-2]) if len(close_vals) >= 2 else current_price
    daily_growth = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0.0
    
    return jsonify({
        "dates": dates,
        "close": safe_list(close_vals),
        "open": safe_list(open_vals),
        "high": safe_list(high_vals),
        "low": safe_list(low_vals),
        "ma50": safe_list(ma50),
        "ma200": safe_list(ma200),
        "rsi": safe_list(rsi),
        "current_price": current_price,
        "highest_price": highest_price,
        "trend": trend,
        "recommendation": rec_data['signal'],
        "volatility": vol_latest,
        "daily_growth": daily_growth
    })

@app.route('/api/sentiment')
def api_sentiment():
    ticker = request.args.get('ticker', '^NSEI')
    sentiment_data = get_sentiment(ticker)
    return jsonify({
        "sentiment": sentiment_data['sentiment'],
        "score": sentiment_data['score']
    })

@app.route('/api/predict')
def api_predict():
    days = request.args.get('days', default=30, type=int)
    ticker = request.args.get('ticker', '^NSEI')
    
    df = fetch_historical_data(ticker, period="3y")
    if df.empty:
        return jsonify({"error": "No data available for prediction"}), 404
        
    preds = predict_future(df, days=days, model_type="LSTM")
    rmse, mae = evaluate_model(df) # Simulated fast response values
    
    return jsonify({
        "predictions": [float(p) for p in preds],
        "rmse": rmse,
        "mae": mae
    })

@app.route('/api/market_overview')
def api_market_overview():
    try:
        from tickers import TICKER_MAP
        import yfinance as yf
        
        # Get up to 100 valid tickers to avoid huge timeouts on local instances
        valid_tickers = [k for k, v in TICKER_MAP.items() if v.strip()]
        scan_list = [TICKER_MAP[k] for k in valid_tickers[:100]]
        
        # Bulk download
        data = yf.download(scan_list, period="5d", interval="1d", progress=False)
        
        results = []
        for i, ticker_key in enumerate(valid_tickers[:100]):
            ticker = TICKER_MAP[ticker_key]
            if "Open" not in data or ticker not in data["Open"]:
                continue
                
            open_prices = data["Open"][ticker].dropna()
            close_prices = data["Close"][ticker].dropna()
            
            if len(open_prices) == 0 or len(close_prices) < 2:
                continue
                
            current_open = float(open_prices.iloc[-1])
            last_close = float(close_prices.iloc[-2]) if len(close_prices) > 1 else current_open
            current_close = float(close_prices.iloc[-1])
            
            # Simple fast proxy for ML prediction: ARIMA-like surrogate
            # (base + dampened trend)
            trend = current_close - last_close
            predicted_close = current_close + (trend * 0.1)
            
            # Additional safety fallback: if it drops below open by too much in proxy
            if predicted_close <= 0:
                predicted_close = current_open * 1.01
                
            growth_perc = ((predicted_close - current_open) / current_open) * 100 if current_open > 0 else 0
            
            results.append({
                "ticker": ticker_key,
                "symbol": ticker,
                "open": current_open,
                "predicted_close": predicted_close,
                "estimated_growth": growth_perc
            })
            
        return jsonify({"data": results})
    except Exception as e:
        print(f"Market Overview error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
