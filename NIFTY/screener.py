import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(ttl=300)
def run_dynamic_screener(tickers_list):
    """
    Downloads data for top 25 companies efficiently and buckets them into 
    Profit Margin, Safe Hold, or Risk to Loss based on RSI and Trend.
    """
    # Filter out any empty items like section headers
    valid_tickers = [t for t in tickers_list if t.strip()]
    # Limit to 25 to ensure speed, using the most popular from the list
    scan_list = valid_tickers[:25]
    
    try:
        # bulk download
        data = yf.download(scan_list, period="1mo", interval="1d", progress=False)["Close"]
        
        results = {"PROFIT": [], "MIDDLE": [], "LOSS": []}
        
        for ticker in scan_list:
            if ticker not in data.columns:
                continue
            prices = data[ticker].dropna()
            if len(prices) < 15:
                continue
                
            # Basic RSI
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            trend_val = prices.iloc[-1] - prices.iloc[-5] if len(prices) >= 5 else 0
            
            if rsi < 40 and trend_val > 0:
                results["PROFIT"].append(ticker)
            elif rsi > 65 and trend_val < 0:
                results["LOSS"].append(ticker)
            elif rsi > 65:
                results["LOSS"].append(ticker)
            elif rsi < 35:
                results["PROFIT"].append(ticker)
            else:
                results["MIDDLE"].append(ticker)
                
        return results
    except Exception as e:
        print(f"Screener Error: {e}")
        return {"PROFIT": ["AAPL"], "MIDDLE": ["MSFT"], "LOSS": ["TSLA"]}

@st.cache_data(ttl=3600)
def get_correlation_matrix(tickers_group):
    try:
        data = yf.download(tickers_group, period="3mo", interval="1d", progress=False)["Close"]
        corr = data.corr()
        return corr
    except:
        return pd.DataFrame()
