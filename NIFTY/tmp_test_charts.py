import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_fetch import fetch_historical_data
from analysis import calculate_technical_indicators

def test_charts():
    df_master = fetch_historical_data("^NSEI", "5y")
    df_filtered = df_master.tail(126).copy()
    df_analyzed = calculate_technical_indicators(df_filtered)
    
    print("Columns:", df_analyzed.columns)
    
    # Test pie
    try:
        day_diffs = df_analyzed['Close'].diff()
        # Ensure we convert series elements properly
        up_days = len(day_diffs[day_diffs > 0])
        down_days = len(day_diffs[day_diffs < 0])
        print("up:", up_days, "down:", down_days)
        fig_pie = px.pie(
            values=[up_days, down_days] if up_days or down_days else [1,1], 
            names=['Bullish Days', 'Bearish Days'],
            color_discrete_sequence=['#3fb950', '#f85149'],
            hole=0.6 
        )
        print("Pie chart created successfully")
    except Exception as e:
        print("Pie err:", e)
        
    # Test bar
    try:
        returns = df_analyzed['Close'].pct_change() * 100
        
        # Test the list comprehension explicitly
        colors = ['#3fb950' if pd.notnull(r) and r >= 0 else '#f85149' for r in returns]
        
        fig_bar = go.Figure(go.Bar(
            x=df_analyzed['Date'],
            y=returns,
            marker_color=colors,
            opacity=0.8
        ))
        print("Bar chart created successfully")
    except Exception as e:
        print("Bar err:", e)

if __name__ == "__main__":
    test_charts()
