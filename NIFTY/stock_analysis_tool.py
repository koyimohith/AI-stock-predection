import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Stock Analysis Tool", layout="wide")

st.title("Stock Analysis & Forecasting Tool")

# Part 1: UI
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Stock Ticker", value="AAPL")
with col2:
    shares = st.number_input("Number of Shares", min_value=1.0, value=10.0, step=1.0)
with col3:
    duration_months = st.number_input("Investment Duration (months)", min_value=1, value=6, step=1)

btn1 = st.button("Run Historical Backtest")
btn2 = st.button("Predict Future Profit/Loss")

@st.cache_data(ttl=3600)
def load_data(ticker_symbol, period="5y"):
    data = yf.Ticker(ticker_symbol).history(period=period)
    # Ensure timezone-naive dates for plotly / consistent manipulation if needed
    if data.index.tz is not None:
        data.index = data.index.tz_convert(None)
    return data

def simulate_ai_prediction_historical(data):
    # Simulate an AI prediction made 6 months ago.
    # Take data up to 6 months ago.
    six_months_ago_date = data.index[-1] - relativedelta(months=6)
    
    hist_data = data[data.index <= six_months_ago_date]
    if hist_data.empty or len(hist_data) < 50:
        st.error("Not enough data to run backtest.")
        return None, None
        
    actual_recent = data[data.index > six_months_ago_date]
    if actual_recent.empty:
        st.warning("No recent data for backtest comparison.")
        return None, None
        
    last_price = hist_data['Close'].iloc[-1]
    
    # Simple stylistic "LSTM-style" mocked trajectory 
    # Calculate daily return mean and std over the last 1 year
    one_year_ago = six_months_ago_date - relativedelta(years=1)
    train_data = hist_data[hist_data.index >= one_year_ago]
    
    if len(train_data) > 0:
        returns = train_data['Close'].pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std()
    else:
        mu = 0.0
        sigma = 0.02
        
    # Introduce some momentum factor (like RSI implies)
    trend = 1.0 if train_data['Close'].iloc[-1] > train_data['Close'].iloc[0] else -1.0
    drift_adjustment = trend * abs(mu) * 0.5
    
    # Generate predicted path over the actual_recent index
    pred_path = [last_price]
    for _ in range(1, len(actual_recent)):
        step = pred_path[-1] * (1 + mu + drift_adjustment + np.random.normal(0, sigma * 0.4))
        pred_path.append(step)
        
    ai_predicted = pd.Series(pred_path, index=actual_recent.index)
    
    return actual_recent['Close'], ai_predicted

def forecast_future(data, months):
    days = int(months * 30.44)
    if days <= 0: return None
    
    last_price = data['Close'].iloc[-1]
    last_date = data.index[-1]
    
    # Use last 2 years for trend
    train_data = data[data.index >= last_date - relativedelta(years=2)]
    returns = train_data['Close'].pct_change().dropna()
    
    mu = returns.mean() 
    sigma = returns.std()
    
    # Adding business days to index
    future_dates = pd.bdate_range(start=last_date + relativedelta(days=1), periods=days)
    
    pred_path = []
    current_price = last_price
    for _ in range(days):
        current_price = current_price * (1 + mu + np.random.normal(0, sigma * 0.7))
        pred_path.append(current_price)
        
    future_series = pd.Series(pred_path, index=future_dates[:days])
    return future_series

if btn1:
    st.subheader(f"Historical Backtest (AI vs. Actual) for {ticker.upper()}")
    with st.spinner("Fetching data and running backtest..."):
        try:
            data = load_data(ticker)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            data = pd.DataFrame()
            
        if not data.empty:
            actual, ai_predicted = simulate_ai_prediction_historical(data)
            if actual is not None:
                fig = go.Figure()
                
                # Show full last year for context
                start_plot_date = data.index[-1] - relativedelta(years=1)
                plot_data = data[data.index >= start_plot_date]
                # Plot historically up to 6mo ago in grey just for reference:
                history_only = plot_data[plot_data.index <= data.index[-1] - relativedelta(months=6)]
                fig.add_trace(go.Scatter(x=history_only.index, y=history_only['Close'], mode='lines', name='Past History', line=dict(color='gray')))
                
                # Plot Actual vs AI Predicted overlay
                fig.add_trace(go.Scatter(x=actual.index, y=actual, mode='lines', name='Actual Price', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=ai_predicted.index, y=ai_predicted, mode='lines', name='AI Predicted Price', line=dict(color='red', dash='dash')))
                
                fig.update_layout(title=f"{ticker.upper()}: AI Prediction 6 Months Ago vs Actual", xaxis_title="Date", yaxis_title="Price (USD)", hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found or an error occurred.")

if btn2:
    st.subheader(f"Future Profit/Loss Projection for {ticker.upper()} ({duration_months} Months)")
    with st.spinner("Calculating projection..."):
        try:
            data = load_data(ticker)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            data = pd.DataFrame()
            
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            future_series = forecast_future(data, duration_months)
            
            if future_series is not None:
                predicted_future_price = future_series.iloc[-1]
                
                total_investment = current_price * shares
                projected_value = predicted_future_price * shares
                profit_loss = projected_value - total_investment
                roi = (profit_loss / total_investment) * 100
                
                st.markdown("### Summary Table")
                
                # Format results
                verdict = "PROFIT" if profit_loss > 0 else "LOSS"
                verdict_color = "green" if profit_loss > 0 else "red"
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Current Price", f"${current_price:,.2f}")
                col_b.metric(f"Predicted Price (after {duration_months}m)", f"${predicted_future_price:,.2f}")
                col_c.metric(f"Total Cost for {shares} Shares", f"${total_investment:,.2f}")
                
                st.markdown("### Final Verdict")
                st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.1);'>"
                            f"<strong>Verdict:</strong> <span style='color:{verdict_color}; font-size:24px; font-weight:bold;'>{verdict}</span><br/>"
                            f"<strong>Estimated Profit/Loss Amount:</strong> <span style='color:{verdict_color}; font-weight:bold;'>${profit_loss:+,.2f}</span><br/>"
                            f"<strong>Estimated ROI:</strong> <span style='color:{verdict_color}; font-weight:bold;'>{roi:+.2f}%</span>"
                            f"</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Growth Chart
                fig2 = go.Figure()
                # Past 6 months history
                past_data = data[data.index >= data.index[-1] - relativedelta(months=6)]
                fig2.add_trace(go.Scatter(x=past_data.index, y=past_data['Close'], mode='lines', name='Past Actual Price', line=dict(color='blue')))
                fig2.add_trace(go.Scatter(x=future_series.index, y=future_series, mode='lines', name='Forecasted Growth', line=dict(color='green' if profit_loss > 0 else 'red', dash='dot')))
                
                fig2.update_layout(title=f"{ticker.upper()} Projection over {duration_months} Months", xaxis_title="Date", yaxis_title="Price (USD)", hovermode="x unified")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Invalid duration.")
        else:
            st.warning("No data found or an error occurred.")
