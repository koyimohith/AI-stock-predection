import pandas as pd
import numpy as np

def calculate_technical_indicators(df):
    """Calculates MA, RSI, MACD, and Volatility"""
    if df.empty or len(df) < 50:
        return df
        
    try:
        close_col = 'Close'
        if close_col not in df.columns:
            cols = [c for c in df.columns if 'close' in str(c).lower()]
            if cols:
                close_col = cols[0]
            else:
                return df

        df[close_col] = pd.to_numeric(df[close_col], errors='coerce')

        # Moving Averages
        df['MA10'] = df[close_col].rolling(window=10).mean()
        df['MA50'] = df[close_col].rolling(window=50).mean()
        df['MA200'] = df[close_col].rolling(window=200).mean()
        
        # RSI (14 days)
        delta = df[close_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df[close_col].ewm(span=12, adjust=False).mean()
        ema_26 = df[close_col].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Volatility
        df['Daily_Return'] = df[close_col].pct_change()
        # Ensure sufficient data for std, fill with 0 if necessary
        df['Volatility'] = df['Daily_Return'].rolling(window=20, min_periods=1).std() * np.sqrt(252)
        df['Volatility'] = df['Volatility'].fillna(0.15) # Default baseline
        
        # Spike/Drop Alerts
        df['Price_Spike'] = np.where(df['Daily_Return'] > 0.02, 1, 0) # 2% up
        df['Price_Drop'] = np.where(df['Daily_Return'] < -0.02, 1, 0) # 2% down

        df = df.bfill()
        df = df.ffill()
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        
    return df

def analyze_trend(price_history):
    """
    Analyzes list of recent live prices to determine continuous tracking trend
    Strong Uptrend -> consistent increase
    Strong Downtrend -> consistent decrease
    """
    if len(price_history) < 2:
        return "Stable"
    
    increases = 0
    decreases = 0
    for i in range(1, len(price_history)):
        if price_history[i] > price_history[i-1]:
            increases += 1
        elif price_history[i] < price_history[i-1]:
            decreases += 1
            
    recent_diff = price_history[-1] - price_history[-2]
    
    if increases >= len(price_history) - 2 and recent_diff > 0:
        return "Bullish"
    elif decreases >= len(price_history) - 2 and recent_diff < 0:
        return "Bearish"
    elif recent_diff > 0:
        return "Increasing"
    elif recent_diff < 0:
        return "Decreasing"
    else:
        return "Sideways"

def get_support_resistance(df):
    """Derives basic short-term support and resistance from recent highs/lows"""
    if df.empty or 'High' not in df.columns or 'Low' not in df.columns:
        return 0.0, 0.0
    
    recent_data = df.tail(20) # Look at last 20 periods
    resistance = recent_data['High'].max()
    support = recent_data['Low'].min()
    return support, resistance

def get_recommendation_details(live_price, predicted_price, trend, volatility, rsi):
    """
    Returns a dictionary with comprehensive recommendation logic for the dashboard card.
    """
    diff_perc = ((predicted_price - live_price) / live_price) * 100 if live_price > 0 else 0
    
    # Base signal logic
    signal = "HOLD"
    if diff_perc > 0.1 and trend in ["Bullish", "Increasing"]:
        signal = "BUY"
    elif diff_perc < -0.1 and trend in ["Bearish", "Decreasing"]:
        signal = "SELL"
    elif diff_perc > 0.25:
        signal = "BUY" # Breakout prediction prediction overrides short-term trend
    elif diff_perc < -0.25:
        signal = "SELL"
        
    # Calculate simulated confidence score out of 100
    base_conf = 50
    conf_add = abs(diff_perc) * 50 # if diff is 0.5%, adds 25
    
    # Modifiers
    if signal == "BUY" and trend == "Bullish": conf_add += 15
    if signal == "SELL" and trend == "Bearish": conf_add += 15
    if rsi is not None:
        if signal == "BUY" and rsi < 40: conf_add += 10 # Good entry
        if signal == "SELL" and rsi > 60: conf_add += 10 # Good exit
        
    # Penalty for extreme high volatility uncertainty
    vol_adjusted = volatility if volatility is not None else 0.15
    if vol_adjusted > 0.25:
        conf_add -= 10
        risk = "High Risk"
    elif vol_adjusted < 0.12:
        risk = "Low Risk"
    else:
        risk = "Moderate Risk"
        
    confidence_score = min(max(base_conf + conf_add, 50), 98) # cap between 50 and 98
    
    # Reason generator
    reason = "Market shows stable oscillation near current levels."
    if signal == "BUY":
        reason = "AI predicts impending upward momentum combined with positive technical structures."
        if rsi and rsi < 30: reason += " Deep oversold territory suggests a bounce."
    elif signal == "SELL":
        reason = "AI forecasts downward pressure, exacerbated by weak live trend movement."
        if rsi and rsi > 70: reason += " Overbought warnings support shorting."
        
    return {
        "signal": signal,
        "confidence": confidence_score,
        "reason": reason,
        "risk": risk
    }

def generate_smart_insight(trend, rsi, volatility, diff_perc):
    """Generates dynamic market insight string based on multiple factors"""
    message = []
    
    if trend == "Bullish":
        message.append("Market momentum is accelerating upward.")
    elif trend == "Increasing":
        message.append("Momentum is improving but confirmation is pending.")
    elif trend == "Bearish":
        message.append("Strong downward pressure is evident.")
    elif trend == "Decreasing":
        message.append("Slight bearish sentiment observed in the short term.")
    else:
        message.append("Market is moving sideways with low momentum.")

    if volatility and not pd.isna(volatility) and volatility > 0.2:
        message.append("Volatility is increasing near resistance.")
        
    if rsi and not pd.isna(rsi):
        if rsi > 70:
            message.append("Technicals indicate overbought territory.")
        elif rsi < 30:
            message.append("Potential bounce detected near support.")

    return " ".join(message)
