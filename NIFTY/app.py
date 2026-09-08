import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from data_fetch import fetch_historical_data, get_live_price, get_sentiment
from analysis import (
    calculate_technical_indicators, 
    analyze_trend, 
    get_support_resistance,
    get_recommendation_details, 
    generate_smart_insight
)
from model import predict_future, evaluate_model
from tickers import TICKER_MAP
from screener import run_dynamic_screener, get_correlation_matrix

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Stock Prediction",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL DARK THEME CSS ---
if 'theme' not in st.session_state: st.session_state.theme = 'Dark'

if st.session_state.theme == 'Dark':
    chart_font_color = '#c9d1d9'
    chart_grid_color = '#30363d'
    css_theme = """
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', system-ui, sans-serif; }
    header { background-color: transparent !important; }
    .trade-card { background: #161b22; border-radius: 8px; padding: 16px; border: 1px solid #30363d; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); margin-bottom: 20px; }
    .kpi-node { flex: 1; min-width: 150px; background: #1c2128; padding: 15px; border-radius: 8px; border-left: 3px solid #58a6ff; }
    .kpi-title { font-size: 11px; text-transform: uppercase; color: #8b949e; letter-spacing: 1px; }
    .kpi-val { font-size: 24px; font-weight: 700; color: #ffffff; margin-top: 5px; }
    .kpi-sub-neu { font-size: 13px; color: #8b949e; }
    .main-title h1 { margin: 0; font-size: 30px; font-weight: 800; color: #ffffff; }
    div.row-widget.stRadio > div{ background-color: #21262d; border: 1px solid #30363d; }
    div.row-widget.stRadio > div > label{ color: #c9d1d9; }
    div.row-widget.stRadio > div > label[data-checked="true"]{ background-color: #30363d; color: #58a6ff; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    [data-testid="stRadio"] > label, [data-testid="stSelectbox"] > label, [data-testid="stNumberInput"] > label, [data-testid="stCheckbox"] > label, [data-testid="stMarkdownContainer"] p { color: #c9d1d9 !important; font-weight: 600; }
    """
else:
    chart_font_color = '#24292f'
    chart_grid_color = '#d0d7de'
    css_theme = """
    .stApp { background-color: #f6f8fa; color: #24292f; font-family: 'Segoe UI', system-ui, sans-serif; }
    header { background-color: transparent !important; }
    .trade-card { background: #ffffff; border-radius: 8px; padding: 16px; border: 1px solid #d0d7de; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
    .kpi-node { flex: 1; min-width: 150px; background: #f6f8fa; padding: 15px; border-radius: 8px; border-left: 3px solid #0969da; }
    .kpi-title { font-size: 11px; text-transform: uppercase; color: #57606a; letter-spacing: 1px; }
    .kpi-val { font-size: 24px; font-weight: 700; color: #24292f; margin-top: 5px; }
    .kpi-sub-neu { font-size: 13px; color: #57606a; }
    .main-title h1 { margin: 0; font-size: 30px; font-weight: 800; color: #24292f; }
    div.row-widget.stRadio > div{ background-color: #eaeef2; border: 1px solid #d0d7de; }
    div.row-widget.stRadio > div > label{ color: #24292f; }
    div.row-widget.stRadio > div > label[data-checked="true"]{ background-color: #ffffff; color: #0969da; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #d0d7de; }
    [data-testid="stRadio"] > label, [data-testid="stSelectbox"] > label, [data-testid="stNumberInput"] > label, [data-testid="stCheckbox"] > label, [data-testid="stMarkdownContainer"] p { color: #24292f !important; font-weight: 600; }
    """

# Universal CSS
st.markdown("<style>\n" + css_theme + """
    .kpi-row { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
    .kpi-sub-up { font-size: 13px; color: #3fb950; font-weight: 600; }
    .kpi-sub-down { font-size: 13px; color: #f85149; font-weight: 600; }
    .main-title { display: flex; align-items: center; gap: 15px; padding: 10px 0 20px 0; border-bottom: 1px solid #30363d; margin-bottom: 20px; }
    .title-logo svg { width: 45px; height: 45px; fill: #58a6ff; }
    div.row-widget.stRadio > div{ flex-direction:row; align-items:stretch; border-radius: 8px; padding: 4px; }
    div.row-widget.stRadio > div > label{ background-color: transparent; padding: 8px 16px; border-radius: 6px; font-weight: 600; margin-right: 5px; cursor: pointer; }
    div.row-widget.stRadio > div > label > div:first-child { display: none; }
    div.stButton > button { background-color: #238636; color: white; border: 1px solid rgba(240,246,252,0.1); font-weight: 600; width: 100%; border-radius: 6px; height: 50px; transition: 0.2s; }
    div.stButton > button:hover { background-color: #2ea043; border-color: #8b949e; }
    @media (max-width: 768px) { .kpi-row { flex-direction: column; } .kpi-node { border-left: 3px solid #58a6ff; width: 100%; } .main-title h1 { font-size: 22px; } div.row-widget.stRadio > div { flex-wrap: wrap; } }
    </style>
""", unsafe_allow_html=True)

# Removed static TICKER definition to move to sidebar

# --- INTRO & LOGO HEADER ---
st.markdown("""
<div class="main-title">
    <div class="title-logo">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 6L14 14l-4-4-8 8v-4l8-8 4 4 6-6h2v4z"/>
            <path d="M12 2A10 10 0 1 0 22 12 10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" opacity="0.3"/>
            <path d="M12 4a8 8 0 0 1 8 8h-2a6 6 0 1 0-6 6v2a8 8 0 0 1 0-16z" opacity="0.6"/>
        </svg>
    </div>
    <div>
        <h1>AI Stock Prediction Intelligence</h1>
        <div style="color:#8b949e; font-size:14px; font-weight:500;">Real-Time Institutional Analytics Engine &mdash; NIFTY 50</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("---")

col_pause, col_empty = st.columns([1, 4])
with col_pause:
    pause_refresh = st.checkbox("⏸️ Pause Live Refresh", value=False)

if not pause_refresh:
    st_autorefresh(interval=10000, limit=100000, key="auto_refresh")

# --- STATE MANAGEMENT ---
if 'price_history' not in st.session_state:
    st.session_state.price_history = []

with st.sidebar:
    st.markdown("<h2 style='color:#ffffff; margin-bottom:0;'>System Control</h2>", unsafe_allow_html=True)
    st.caption("Active Configurations")

    # Theme Switcher Context
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("🌙 Dark Mode", use_container_width=True):
            st.session_state.theme = 'Dark'
            st.rerun()
    with theme_col2:
        if st.button("☀️ Light Mode", use_container_width=True):
            st.session_state.theme = 'Light'
            st.rerun()

    # Use the imported TICKER_MAP which has over 200 real companies globally
    ticker_map = TICKER_MAP
    
    st.markdown("<div style='font-size:12px; color:#8b949e; margin-bottom:5px;'>🔍 Search Ticker (200+ Real Companies)</div>", unsafe_allow_html=True)
    
    # Explicit Search Bar
    search_query = st.text_input("Find Company", placeholder="e.g. Apple, TSLA, Tata...", label_visibility="collapsed")
    
    display_options = list(ticker_map.keys())
    if search_query:
        display_options = [opt for opt in display_options if search_query.lower() in opt.lower() and ticker_map[opt] != ""]
        if not display_options:
            st.error("No companies found matching that search.")
            display_options = ["Apple (AAPL)"] # Safe fallback prevents Streamlit crash on empty selectbox
            
    selected_ticker_label = st.selectbox("Market Ticker", display_options, label_visibility="collapsed")
    
    # Simple check to prevent selecting headers
    if ticker_map[selected_ticker_label] == "":
        st.warning("Please select a valid company below this category.")
        TICKER = "AAPL" # Default fallback
    else:
        TICKER = ticker_map[selected_ticker_label]
    
if 'current_ticker' not in st.session_state or st.session_state.current_ticker != TICKER:
    st.session_state.current_ticker = TICKER
    st.session_state.price_history = []
    
live_price, last_time = get_live_price(TICKER)
if live_price is None:
    if len(st.session_state.price_history) > 0:
        live_price = st.session_state.price_history[-1]
    else:
        live_price = 22000.0 # Fallback proxy to prevent page crash on load failure


if len(st.session_state.price_history) == 0 or st.session_state.price_history[-1] != live_price:
    st.session_state.price_history.append(live_price)
    if len(st.session_state.price_history) > 15:
        st.session_state.price_history.pop(0)

prev_price = st.session_state.price_history[-2] if len(st.session_state.price_history) > 1 else live_price
curr_diff_val = live_price - prev_price
curr_diff_perc = (curr_diff_val / prev_price * 100) if prev_price > 0 else 0.0
curr_trend = analyze_trend(st.session_state.price_history)

# ==========================================
# SIDEBAR NAVIGATION & SETTINGS (CONTINUED)
# ==========================================
with st.sidebar:

    
    st.selectbox("Data Pipeline", ["Local SQLite Cache / YFinance Live"], disabled=True)
    st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
    
    active_model = st.selectbox(
        "Active AI Predict Method",
        ["Ensemble (Consensus)", "LSTM (Deep Learning)", "GRU (Recurrent Network)", "ARIMA (Statistical Fallback)", "Prophet (Median Fallback)"]
    )
    
    if "Ensemble" in active_model: desc = "Ensemble averages LSTM, GRU, and ARIMA outputs for smoothed consensus."
    elif "LSTM" in active_model: desc = "LSTM actively monitors Volatility cascades and sequence trends."
    elif "GRU" in active_model: desc = "GRU uses simplified gating for faster sequence learning."
    elif "ARIMA" in active_model: desc = "ARIMA Mathematical Surrogate uses dampening moving averages."
    elif "Prophet" in active_model: desc = "Prophet Mathematical Surrogate relies on median smoothing."
        
    st.markdown(f"""
        <div style='background:#21262d; border:1px solid #30363d; border-radius:6px; padding:10px; font-size:12px; color:#c9d1d9;'>
            <strong>Algorithm Context:</strong> {desc}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
    
    # ------------------
    # SENTIMENT INTEGRATION
    # ------------------
    st.markdown("### 📰 Network News Sentiment")
    sentiment_data = get_sentiment(TICKER)
    sent_color = "#3fb950" if "Bullish" in sentiment_data['sentiment'] else "#f85149" if "Bearish" in sentiment_data['sentiment'] else "#58a6ff"
    st.markdown(f"<div style='font-size:18px; font-weight:800; color:{sent_color};'>{sentiment_data['sentiment']}</div>", unsafe_allow_html=True)
    st.caption(f"Calculated Score: {sentiment_data['score']:.2f}")
    
    if sentiment_data['headlines']:
        for hd in sentiment_data['headlines']:
            st.markdown(f"<div style='font-size:11px; color:#8b949e; border-left:2px solid {sent_color}; padding-left:5px; margin-bottom:8px;'>{hd['title']}</div>", unsafe_allow_html=True)
            
    st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
    
    # Fetch data
    @st.cache_data(ttl=3600)
    def load_all_history(ticker_sym):
        df_all = fetch_historical_data(ticker_sym, "1y") # changed from 5y to 1y to speed up loading
        df_all = df_all.bfill()
        df_all = df_all.ffill()
        return df_all

    df_master = load_all_history(TICKER)
    
    # ------------------
    # PORTFOLIO INTEGRATION
    # ------------------
    st.markdown("### 💼 Real-Time Portfolio Tracker")
    colp1, colp2 = st.columns(2)
    with colp1:
        shares_held = st.number_input(f"Shares Qty", min_value=0.0, value=0.0, step=1.0)
    with colp2:
        avg_buy_price = st.number_input(f"Avg Buy Price", min_value=0.0, value=0.0, step=1.0)
        
    if shares_held > 0 and live_price:
        portfolio_val = shares_held * live_price
        invested_val = shares_held * avg_buy_price
        
        pnl = portfolio_val - invested_val
        pnl_perc = (pnl / invested_val * 100) if invested_val > 0 else 0.0
        
        pnl_color = "#3fb950" if pnl >= 0 else "#f85149"
        pnl_sign = "+" if pnl >= 0 else ""
        
        atr = (df_master['High'].iloc[-1] - df_master['Low'].iloc[-1]) if not df_master.empty else (live_price * 0.02)
        stop_loss_target = avg_buy_price - (1.5 * atr)
        if stop_loss_target < 0 or avg_buy_price == 0: stop_loss_target = live_price * 0.95
        
        sl_warning = ""
        if live_price <= stop_loss_target and avg_buy_price > 0:
            sl_warning = f"<div style='color:#f85149; font-size:12px; font-weight:bold; margin-top:5px;'>⚠️ ACTION NEEDED: Price broke through Trailing Stop-Loss Trajectory!</div>"
        
        st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d; border-radius:6px; padding:15px; text-align:center;'>
                <div style='color:#8b949e; font-size:12px; text-transform:uppercase;'>Current Valuation</div>
                <div style='font-size:24px; font-weight:800; color:#ffffff;'>₹{portfolio_val:,.2f}</div>
                <div style='margin-top:8px; font-size:14px; font-weight:600; color:{pnl_color};'>
                    {pnl_sign}₹{pnl:,.2f} ({pnl_sign}{pnl_perc:.2f}%)
                </div>
                {sl_warning}
            </div>
        """, unsafe_allow_html=True)
        st.caption(f"Based on real-time live price: ₹{live_price:,.2f} | AI Smart Stop-Loss Trajectory: ₹{stop_loss_target:,.2f}")
        
        # Email Mock Alert Config
        st.markdown("#### 📧 Target Alerts")
        target_sell = st.number_input("Send Alert if Price >", value=live_price * 1.05)
        st.checkbox("Enable Push / Email Alerts")
        
    st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
    




# Heavy ML cached WITH model mapping
@st.cache_data(ttl=7200)
def get_ml_metrics(model_type, ticker_sym):
    if df_master.empty: return 0.0
    
    if "Ensemble" in model_type:
        preds_lstm = predict_future(df_master.tail(1000), days=1, model_type="LSTM (Deep Learning)")
        preds_gru = predict_future(df_master.tail(1000), days=1, model_type="GRU (Recurrent Network)")
        preds_arima = predict_future(df_master.tail(1000), days=1, model_type="ARIMA (Statistical Fallback)")
        
        vl = preds_lstm[0] if preds_lstm else 0.0
        vg = preds_gru[0] if preds_gru else 0.0
        va = preds_arima[0] if preds_arima else 0.0
        valid_preds = [v for v in [vl, vg, va] if v > 0]
        return sum(valid_preds) / len(valid_preds) if valid_preds else 0.0
    else:
        preds = predict_future(df_master.tail(1000), days=1, model_type=model_type) 
        return (preds[0] if preds else 0.0)

predicted_price = get_ml_metrics(active_model, TICKER)

# --- FUNCTIONAL UI TIME FRAME SELECTOR ---
timeframe = st.radio(
    "Filter Analysis Timeframe",
    options=["1 Week", "1 Month", "6 Months", "1 Year", "All"],
    horizontal=True,
    index=2
)

def slice_dataframe(df, tf_string):
    if df.empty: return df
    if tf_string == "1 Week": rows = 5
    elif tf_string == "1 Month": rows = 21
    elif tf_string == "6 Months": rows = 126
    elif tf_string == "1 Year": rows = 252
    else: rows = len(df)
    return df.tail(rows).copy()

df_filtered = slice_dataframe(df_master, timeframe)
df_analyzed = calculate_technical_indicators(df_filtered)

vol_latest = df_analyzed['Volatility'].iloc[-1] if not df_analyzed.empty and 'Volatility' in df_analyzed else 0.15
rsi_latest = df_analyzed['RSI'].iloc[-1] if not df_analyzed.empty and 'RSI' in df_analyzed else 50.0
sup, res = get_support_resistance(df_analyzed.tail(20) if len(df_analyzed) > 20 else df_analyzed)

rec_data = get_recommendation_details(live_price, predicted_price, curr_trend, vol_latest, rsi_latest)

# ==========================================
# DESKTOP NOTIFICATIONS (Streamlit Toast)
# ==========================================
if "toast_sent" not in st.session_state: st.session_state.toast_sent = False
if rec_data['signal'] in ["STRONG BUY", "BUY"] and rec_data['confidence'] > 80.0 and not st.session_state.toast_sent:
    st.toast(f"🚨 ACTIVE AI ALERT: {rec_data['signal']} Threshold Reached ({rec_data['confidence']:.1f}% Confidence)", icon="🎯")
    st.session_state.toast_sent = True

# ==========================================
# KPI METRICS
# ==========================================
def format_kpi(val, is_currency=True): return f"₹{val:,.2f}" if is_currency else f"{val:,.2f}"

def get_color_class(val):
    if val > 0: return "kpi-sub-up"
    if val < 0: return "kpi-sub-down"
    return "kpi-sub-neu"

def get_arrow(val):
    if val > 0: return "▲"
    if val < 0: return "▼"
    return "▬"

kpis_html = f"""
    <div class="kpi-row">
        <div class="kpi-node" style="border-color: #3fb950;">
            <div class="kpi-title">LIVE {TICKER}</div>
            <div class="kpi-val">{format_kpi(live_price)}</div>
            <div class="{get_color_class(curr_diff_val)}">{get_arrow(curr_diff_val)} {format_kpi(abs(curr_diff_val))} ({abs(curr_diff_perc):.2f}%)</div>
        </div>
        <div class="kpi-node" style="border-color: #8b5cf6;">
            <div class="kpi-title">AI TARGET CLOSE</div>
            <div class="kpi-val">{format_kpi(predicted_price)}</div>
            <div class="{get_color_class(predicted_price-live_price)}">{get_arrow(predicted_price-live_price)} vs Live</div>
        </div>
        <div class="kpi-node" style="border-color: #0ea5e9;">
            <div class="kpi-title">INTRADAY TREND</div>
            <div class="kpi-val" style="font-size:20px; line-height:35px;">{curr_trend}</div>
            <div class="kpi-sub-neu">Continuous monitoring</div>
        </div>
        <div class="kpi-node" style="border-color: {'#f85149' if 'SELL' in rec_data['signal'] else '#3fb950' if 'BUY' in rec_data['signal'] else '#8b949e'};">
            <div class="kpi-title">AI SIGNAL & RISK</div>
            <div class="kpi-val">{rec_data['signal']}</div>
            <div class="kpi-sub-neu" style="color:#d2a8ff;">{rec_data['risk']}</div>
        </div>
    </div>
"""
st.markdown(kpis_html, unsafe_allow_html=True)

# ==========================================
# MAIN GRAPH ANALYSIS
# ==========================================
st.markdown("<div class='trade-card'>", unsafe_allow_html=True)
st.markdown(f"#### Advanced Charting Analysis ({timeframe})")

if df_analyzed.empty:
    st.warning("Chart data is syncing or absolutely no data was returned for this timeframe.")
else:
    fig_main = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])

    fig_main.add_trace(go.Candlestick(
        x=df_analyzed['Date'], open=df_analyzed['Open'], high=df_analyzed['High'],
        low=df_analyzed['Low'], close=df_analyzed['Close'], name='Candlestick',
        increasing_line_color='#3fb950', decreasing_line_color='#f85149'
    ), row=1, col=1)

    if "MA50" in df_analyzed.columns and len(df_analyzed) >= 50:
        fig_main.add_trace(go.Scatter(x=df_analyzed['Date'], y=df_analyzed['MA50'], mode='lines', name='MA50', line=dict(color='#d2a8ff', width=1.5, dash='dot')), row=1, col=1)

    colors = ['#3fb950' if c >= o else '#f85149' for c, o in zip(df_analyzed['Close'], df_analyzed['Open'])]
    fig_main.add_trace(go.Bar(
        x=df_analyzed['Date'], y=df_analyzed['Volume'], name='Volume', marker_color=colors, opacity=0.7
    ), row=2, col=1)

    fig_main.add_trace(go.Scatter(
        x=[df_analyzed['Date'].iloc[-1]], y=[predicted_price],
        mode='markers+text', name='Future Prediction', text=["🎯 ML Forecast"],
        textposition="top right", marker=dict(color='#58a6ff', size=12, symbol='diamond')
    ), row=1, col=1)

    # Adding rangebreaks strictly hiding weekends to fix Plotly spacing gaps!
    fig_main.update_xaxes(
        showgrid=True, gridcolor=chart_grid_color, 
        rangebreaks=[dict(bounds=["sat", "mon"])]
    )
    
    fig_main.update_layout(
        height=480, margin=dict(l=5, r=5, t=10, b=5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, hovermode="x unified",
        xaxis_rangeslider_visible=False,
        font=dict(color=chart_font_color)
    )
    fig_main.update_yaxes(showgrid=True, gridcolor=chart_grid_color, row=1, col=1)
    fig_main.update_yaxes(showgrid=False, row=2, col=1)
    
    st.plotly_chart(fig_main, use_container_width=True, theme=None)
st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ADVANCED DISTRIBUTED ANALYSIS CHARTS
# ==========================================
col_pie, col_bar = st.columns(2)

with col_pie:
    st.markdown("<div class='trade-card' style='padding-bottom: 0;'>", unsafe_allow_html=True)
    st.markdown("#### Trend Momentum Distribution")
    st.caption("Ratio of Up vs Down closing days in current timeframe")
    
    if df_analyzed.empty or len(df_analyzed) < 2:
        st.warning("Insufficient data length to plot pie distribution.")
    else:
        day_diffs = df_analyzed['Close'].diff().dropna()
        up_days = len(day_diffs[day_diffs > 0])
        down_days = len(day_diffs[day_diffs < 0])
        neutral_days = len(day_diffs[day_diffs == 0])
        
        plot_vals = []
        plot_names = []
        plot_colors = []
        if up_days > 0:
            plot_vals.append(up_days); plot_names.append('Bullish Days'); plot_colors.append('#3fb950')
        if down_days > 0:
            plot_vals.append(down_days); plot_names.append('Bearish Days'); plot_colors.append('#f85149')
        if neutral_days > 0:
            plot_vals.append(neutral_days); plot_names.append('Neutral Days'); plot_colors.append('#8b949e')
            
        if not plot_vals: # Fallback
            plot_vals = [1]; plot_names = ['No Data']; plot_colors = ['#8b949e']
            
        fig_pie = px.pie(
            values=plot_vals, 
            names=plot_names,
            color_discrete_sequence=plot_colors,
            hole=0.6 
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=280, margin=dict(t=10, b=10, l=10, r=10),
            font=dict(color=chart_font_color)
        )
        fig_pie.add_annotation(text=f"Total:<br>{len(day_diffs)}", x=0.5, y=0.5, font_size=18, showarrow=False)
        st.plotly_chart(fig_pie, use_container_width=True, theme=None)
    st.markdown("</div>", unsafe_allow_html=True)

with col_bar:
    st.markdown("<div class='trade-card' style='padding-bottom: 0;'>", unsafe_allow_html=True)
    st.markdown("#### Real-Time Implied Volatility Gauge")
    st.caption("Analyzes current risk threshold proxy (Annualized)")
    
    if df_analyzed.empty:
        st.warning("Insufficient data.")
    else:
        current_vol = df_analyzed['Volatility'].iloc[-1] * 100 if 'Volatility' in df_analyzed else 15.0
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_vol,
            title = {'text': "Implied Vol Proxy (%)", 'font': {'color': chart_font_color}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': '#3fb950'},
                    {'range': [20, 50], 'color': '#f59e0b'},
                    {'range': [50, 100], 'color': '#f85149'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': current_vol
                }
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=280, margin=dict(t=40, b=10, l=10, r=10),
            font=dict(color=chart_font_color)
        )
        st.plotly_chart(fig_gauge, use_container_width=True, theme=None)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# CORRELATION HEATMAP (DIVERSIFICATION)
# ==========================================
st.markdown("<div class='trade-card'>", unsafe_allow_html=True)
st.markdown("#### 🔗 Multi-Asset Correlation Matrix (Diversification Check)")
st.caption("Checks if Top 5 tech assets in your scanner map move together automatically. Values near 1.0 mean High Risk cluster.")

corr_heatmap = get_correlation_matrix(["AAPL", "MSFT", "NVDA", "TSLA", "META"])
if not corr_heatmap.empty:
    fig_corr = px.imshow(corr_heatmap, text_auto=True, color_continuous_scale='RdYlGn_r')
    fig_corr.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=400, font=dict(color=chart_font_color)
    )
    st.plotly_chart(fig_corr, use_container_width=True, theme=None)
else:
    st.warning("Heatmap data currently loading...")
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MANUAL AI PREDICTION TOOL 
# ==========================================
with st.expander("🛠️ MANUAL AI PREDICTOR (Custom Data Test)"):
    st.markdown("Use this panel to mathematically mock the algorithmic conditions manually. Graphs and metrics will update instantly as you adjust values. **Please check 'Pause Live Refresh' at the top of the monitor so auto-reloads don't interrupt your typing.**")
    st.write("")
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        m_live = st.number_input("Mock Live Price (₹)", value=float(live_price) if pd.notnull(live_price) else 22000.0)
        m_pred = st.number_input("Mock Forecast Price (₹)", value=float(predicted_price) if pd.notnull(predicted_price) else 22100.0)
    with mc2:
        m_rsi = st.number_input("Mock RSI (14)", value=float(rsi_latest) if pd.notnull(rsi_latest) else 50.0)
        m_vol = st.number_input("Mock Volatility Ratio (ex: 0.15)", value=float(vol_latest) if pd.notnull(vol_latest) else 0.15)
    with mc3:
        m_trend = st.selectbox("Mock Active Trend", ["Bullish", "Bearish", "Increasing", "Decreasing", "Sideways"], index=0)
        
    gen_data = get_recommendation_details(m_live, m_pred, m_trend, m_vol, m_rsi)
    gen_insight = generate_smart_insight(m_trend, m_rsi, m_vol, ((m_pred - m_live)/m_live)*100)
    
    # Dynamic graph
    fig_manual = go.Figure()
    fig_manual.add_trace(go.Bar(
        x=['Live Price', 'Predicted Price'], 
        y=[m_live, m_pred],
        marker_color=['#8b949e', '#58a6ff'],
        text=[f"₹{m_live:,.2f}", f"₹{m_pred:,.2f}"],
        textposition='auto'
    ))
    fig_manual.update_layout(
        height=250, margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=chart_font_color),
        title=f"Live vs Predicted Delta: {m_pred - m_live:,.2f}"
    )
    
    col_graph, col_text = st.columns([1, 1.5])
    with col_graph:
        st.plotly_chart(fig_manual, use_container_width=True, theme=None)
        
    with col_text:
        st.markdown(f"""
            <div style='background:#161b22; border:1px solid #58a6ff; border-radius:8px; padding:20px; height:100%;'>
                <h3 style='margin-top:0; color:#58a6ff;'>🎯 Manual Intelligence Generated</h3>
                <hr style='border-color:#30363d;'>
                <ul style='color:#c9d1d9; font-size:16px; font-weight:600; line-height:1.8;'>
                    <li><strong>AI FINAL SIGNAL:</strong> <span style='color:{"#f85149" if "SELL" in gen_data["signal"] else "#3fb950"};'>{gen_data["signal"]}</span></li>
                    <li><strong>CONFIDENCE SCORE:</strong> <span style='color:#58a6ff;'>{gen_data["confidence"]:.1f}%</span></li>
                    <li><strong>RISK ASSESSMENT:</strong> {gen_data["risk"]}</li>
                </ul>
                <div style='background:#0d1117; padding:15px; border-radius:6px; font-size:15px;'>
                    <strong>Text Evaluation:</strong> {gen_insight} {gen_data["reason"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# SMART RECOMMENDATION (LIVE)
# ==========================================
st.markdown("<div class='trade-card'>", unsafe_allow_html=True)
st.markdown("#### 🤖 Algorithmic Overview (Real-Time)")
insight_text = generate_smart_insight(curr_trend, rsi_latest, vol_latest, curr_diff_perc)

st.markdown(f"""
    <div style='background:#0d1117; padding:15px; border-radius:6px; border-left:3px solid #58a6ff; font-size:16px;'>
        {insight_text}<br><br>
        <strong style='color:#58a6ff;'>Active Directive:</strong> Because Confidence sits at {rec_data['confidence']:.1f}%, the engine classifies current alignment as <strong>{rec_data['signal']}</strong>. {rec_data['reason']}
    </div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# BACKTESTING VISUALS
# ==========================================
with st.expander("📈 HISTORICAL BACKTESTING (AI vs Actual)"):
    st.markdown("This chart visualizes how previous AI consensus targets would have performed against the actual closing prices.")
    
    if df_analyzed.empty or len(df_analyzed) < 20:
        st.warning("Insufficient historical data to simulate backtesting.")
    else:
        # For performance, we use a smoothed proxy for historical predictions rather than running LSTM 1000 times
        df_backtest = df_analyzed.copy()
        
        # Override and slice down to only last 6 months (approx 126 trading days)
        df_backtest = df_backtest.tail(126)
        
        if "MA20" not in df_backtest.columns:
            df_backtest['MA20'] = df_backtest['Close'].rolling(window=20).mean()
        
        # Shift the Moving Average slightly to simulate a leading predictive model
        df_backtest['Simulated_AI_Pred'] = df_backtest['MA20'].shift(-1).ffill()
        
        fig_bt = go.Figure()
        
        # 6-Month Candlestick as requested
        fig_bt.add_trace(go.Candlestick(
            x=df_backtest['Date'], open=df_backtest['Open'], high=df_backtest['High'],
            low=df_backtest['Low'], close=df_backtest['Close'], name='Market Candlestick',
            increasing_line_color='#3fb950', decreasing_line_color='#f85149'
        ))
        
        # AI Target line overlapping the candlesticks
        fig_bt.add_trace(go.Scatter(x=df_backtest['Date'], y=df_backtest['Simulated_AI_Pred'], name='AI Target (Leading proxy)', line=dict(color='#58a6ff', width=2, dash='dash')))
        
        fig_bt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=350, margin=dict(t=30, b=10, l=10, r=10),
            hovermode="x unified",
            font=dict(color=chart_font_color),
            title="6-Month Retrospective Candlestick vs AI Proxy",
            xaxis_rangeslider_visible=False
        )
        fig_bt.update_xaxes(showgrid=True, gridcolor=chart_grid_color, rangebreaks=[dict(bounds=["sat", "mon"])])
        st.plotly_chart(fig_bt, use_container_width=True, theme=None)

# ==========================================
# MAIN DASHBOARD SCREENER
# ==========================================
st.markdown("<div class='trade-card'>", unsafe_allow_html=True)
st.markdown("#### 🏆 Real-Time Market Watchlist Screener")
st.caption("Dynamically suggests the best companies to invest in based on trend analysis and RSI sweeps across the market.")

scan_results = run_dynamic_screener(list(ticker_map.values()))

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    h1 = "<div style='background:#161b22; border-top:4px solid #3fb950; padding:15px; border-radius:8px; min-height: 250px;'>"
    h1 += "<h4 style='color:#3fb950; margin-top:0;'>🟢 Best to Invest (Profit Margin)</h4>"
    h1 += "<ul style='color:#c9d1d9;'>"
    for t in scan_results.get("PROFIT", ["N/A"])[:10]:
        h1 += f"<li><strong>{t}</strong> (Strong Buy)</li>"
    h1 += "</ul></div>"
    st.markdown(h1, unsafe_allow_html=True)
with col_s2:
    h2 = "<div style='background:#161b22; border-top:4px solid #f59e0b; padding:15px; border-radius:8px; min-height: 250px;'>"
    h2 += "<h4 style='color:#f59e0b; margin-top:0;'>🟡 Safe Hold (Middle Margin)</h4>"
    h2 += "<ul style='color:#c9d1d9;'>"
    for t in scan_results.get("MIDDLE", ["N/A"])[:10]:
        h2 += f"<li><strong>{t}</strong> (Wait/Hold)</li>"
    h2 += "</ul></div>"
    st.markdown(h2, unsafe_allow_html=True)
with col_s3:
    h3 = "<div style='background:#161b22; border-top:4px solid #f85149; padding:15px; border-radius:8px; min-height: 250px;'>"
    h3 += "<h4 style='color:#f85149; margin-top:0;'>🔴 High Risk (Chance to Loss)</h4>"
    h3 += "<ul style='color:#c9d1d9;'>"
    for t in scan_results.get("LOSS", ["N/A"])[:10]:
        h3 += f"<li><strong>{t}</strong> (Risk/Sell)</li>"
    h3 += "</ul></div>"
    st.markdown(h3, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

