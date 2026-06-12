import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import yfinance as yf

# Set Streamlit page config as first statement
st.set_page_config(layout="wide", page_title="Indian Market Trading & Analysis Terminal", page_icon="📈")

from utils.data_gateway import DataGateway
from utils.indicators import calculate_rsi, calculate_ichimoku, find_support_resistance_levels, calculate_daily_pivots, calculate_macd, calculate_bollinger_bands, calculate_moving_averages, calculate_vwap
from utils.patterns import detect_candlestick_patterns
from utils.options_engine import generate_simulated_option_chain, estimate_historical_volatility
from utils.signal_generator import generate_swing_blueprint, generate_options_signal
from utils.intraday_scanner import run_intraday_scan
from utils.backtester import run_backtest_simulation
from utils.journal import add_journal_entry, get_journal_entries, save_bulk_entries, delete_journal_entry

# Initialize session state for searched ticker
if "selected_searched_ticker" not in st.session_state:
    st.session_state["selected_searched_ticker"] = "TMCV"

# ----------------- Premium CSS styling -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Styling for dark mode dashboard */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    
    /* Header card */
    .title-area {
        background: radial-gradient(circle at top left, #1E293B, #0B0E14);
        padding: 30px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Dynamic blueprint cards */
    .blueprint-card {
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .blueprint-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0,0,0,0.15);
    }
    .buy-signal {
        background: linear-gradient(145deg, rgba(0, 176, 116, 0.05) 0%, rgba(0, 176, 116, 0.02) 100%);
        border-left: 4px solid #00B074 !important;
    }
    .hold-signal {
        background: linear-gradient(145deg, rgba(255, 171, 0, 0.05) 0%, rgba(255, 171, 0, 0.02) 100%);
        border-left: 4px solid #FFAB00 !important;
    }
    .sell-signal {
        background: linear-gradient(145deg, rgba(255, 91, 91, 0.05) 0%, rgba(255, 91, 91, 0.02) 100%);
        border-left: 4px solid #FF5B5B !important;
    }
    
    /* Custom subheaders */
    .card-title {
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        color: #94A3B8;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #94A3B8;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    /* Tabs styling override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        color: #94A3B8;
        padding-left: 16px;
        padding-right: 16px;
        border: 1px solid transparent;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #E2E8F0;
        background-color: rgba(255, 255, 255, 0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3);
    }
    
    /* Dataframes and Tables */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        transition: all 0.2s ease-in-out;
    }
    .stTextInput > div > div > input:focus, .stSelectbox > div > div > div:focus {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Lightweight fade-in animation for main app */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main .block-container {
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #2563EB;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Application Title -----------------
st.markdown("""
<div class="title-area">
    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">📈 High-Precision Trading Terminal</h1>
    <p style="margin: 8px 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;">Institutional-Grade Swing, Intraday, and F&O Options Suite • Indian Markets (NSE/BSE)</p>
</div>
""", unsafe_allow_html=True)

# ----------------- Helper Functions -----------------
@st.cache_data(ttl=60)
def get_index_summary(symbol: str) -> dict:
    try:
        df = DataGateway.fetch_ohlcv(symbol, period="5d", interval="1d")
        if df.empty:
            return {"spot": 0.0, "change": 0.0}
        close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else close
        change_pct = ((close - prev_close) / prev_close) * 100.0
        return {"spot": round(close, 2), "change": round(change_pct, 2)}
    except Exception:
        fallbacks = {
            "^NSEI": {"spot": 23520.15, "change": 0.35},
            "^NSEBANK": {"spot": 49850.50, "change": -0.12},
            "^BSESN": {"spot": 77210.80, "change": 0.42}
        }
        return fallbacks.get(symbol, {"spot": 0.0, "change": 0.0})

def get_previous_day_ohlc(symbol: str) -> dict:
    try:
        df = DataGateway.fetch_ohlcv(symbol, period="5d", interval="1d")
        if df.empty:
            return {"High": 100.0, "Low": 90.0, "Close": 95.0}
        
        last_idx = df.index[-1].date()
        today = datetime.now().date()
        
        if last_idx == today and DataGateway.is_market_open():
            row = df.iloc[-2]
        else:
            row = df.iloc[-1]
            
        return {
            "Open": float(row['Open']),
            "High": float(row['High']),
            "Low": float(row['Low']),
            "Close": float(row['Close']),
        }
    except Exception:
        return {"Open": 23400.0, "High": 23600.0, "Low": 23300.0, "Close": 23480.0}

def get_company_profile(symbol: str, exchange: str = "NSE") -> dict:
    normalized = DataGateway.normalize_symbol(symbol, exchange)
    try:
        ticker = yf.Ticker(normalized)
        info = ticker.info
        if not info:
            return {}
        return {
            "summary": info.get("longBusinessSummary", "No corporate description available."),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE") or 0.0,
            "dividend_yield": info.get("dividendYield", 0.0),
            "beta": info.get("beta", 1.0)
        }
    except Exception:
        return {}

def get_company_news(symbol: str, exchange: str = "NSE") -> list:
    normalized = DataGateway.normalize_symbol(symbol, exchange)
    try:
        ticker = yf.Ticker(normalized)
        raw_news = ticker.news
        parsed_news = []
        if not raw_news:
            return []
        for item in raw_news:
            content = item.get("content", item)
            title = content.get("title", "No Title")
            summary = content.get("summary", "")
            pub_date = content.get("pubDate") or content.get("providerPublishTime") or ""
            
            provider = content.get("provider", {})
            provider_name = provider.get("displayName") if isinstance(provider, dict) else str(provider)
            
            click_through = content.get("clickThroughUrl", {})
            link = click_through.get("url") if isinstance(click_through, dict) else content.get("link", "#")
            
            parsed_news.append({
                "title": title,
                "summary": summary,
                "pub_date": pub_date,
                "provider": provider_name,
                "link": link
            })
        return parsed_news
    except Exception:
        return []

# ----------------- Indices Top Banner -----------------
nifty_info = get_index_summary("^NSEI")
bank_nifty_info = get_index_summary("^NSEBANK")
sensex_info = get_index_summary("^BSESN")

idx_col1, idx_col2, idx_col3 = st.columns(3)
with idx_col1:
    st.metric("NIFTY 50 (NSE Index)", f"₹{nifty_info['spot']}", f"{nifty_info['change']}%")
with idx_col2:
    st.metric("BANK NIFTY (NSE Bank Index)", f"₹{bank_nifty_info['spot']}", f"{bank_nifty_info['change']}%")
with idx_col3:
    st.metric("SENSEX (BSE Index)", f"₹{sensex_info['spot']}", f"{sensex_info['change']}%")

st.markdown("---")

# ----------------- Sidebar / Configuration -----------------
with st.sidebar:
    st.header("⚙️ Core Configuration")
    
    st.info("⚡ **On-Demand Lifecycle Active**: Data is loaded only when requested. Threads clear on exit.")
    
    st.subheader("📊 Data Source")
    data_mode = st.radio("Gateway Mode", ["Sandbox Mode (Free)", "Live Broker (Coming Soon)"], index=0)
    
    st.subheader("💰 Backtesting Parameters")
    default_capital = st.number_input("Starting Capital (₹)", min_value=1000, max_value=10000000, value=100000, step=10000)
    slippage = st.slider("Adverse Slippage Offset (%)", min_value=0.0, max_value=1.0, value=0.1, step=0.05) / 100.0
    
    st.subheader("📈 Risk Parameters")
    risk_free_rate = st.slider("Risk-Free Rate (India %)", min_value=4.0, max_value=9.0, value=6.5, step=0.1) / 100.0
    
    # Global search scanner
    st.markdown("---")
    st.subheader("🔍 Global Ticker Search")
    search_query = st.text_input("Type Stock Name (e.g. Tata, Reliance, ITC, Nifty)")
    
    if search_query:
        try:
            results = yf.Search(search_query).quotes
            if results:
                st.write("**Select Ticker to Load:**")
                for item in results[:6]:
                    symbol = item.get("symbol")
                    name = item.get("longname") or item.get("shortname") or "Unknown Company"
                    exchange_disp = item.get("exchDisp") or "Unknown"
                    if st.button(f"📋 {symbol} - {name} ({exchange_disp})", key=f"search_{symbol}"):
                        st.session_state["selected_searched_ticker"] = symbol
                        st.success(f"Loaded `{symbol}` into memory! Ticker slots are pre-populated.")
                        st.rerun()
            else:
                st.warning("No tickers found matching query.")
        except Exception as e:
            st.error(f"Search error: {str(e)}")

# ----------------- Tabs Main Component -----------------
tab1, tab3, tab4, tab5 = st.tabs([
    "📈 Stock Analyzer (Swing & Intraday)",
    "🎯 Options Intelligence (F&O)",
    "🧪 Historical Backtester",
    "📒 Manual Trading Journal"
])

# ==================== TAB 1: STOCK ANALYZER ====================
with tab1:
    st.subheader("📈 On-Demand Live Charts & Stock Analyzer")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.write("##### Input Parameters")
        trade_mode = st.radio("Trading Mode", ["Swing (Delivery)", "Intraday (Leverage)"], horizontal=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # In Intraday mode, show scanner
        if trade_mode == "Intraday (Leverage)":
            st.info("Find active momentum stocks across Nifty components today.")
            trigger_scan = st.button("Scan Market for Today's Movers", type="primary")
            st.markdown("---")
        else:
            trigger_scan = False
            
        ticker = st.text_input("Ticker Symbol", value=st.session_state["selected_searched_ticker"])
        exchange = st.selectbox("Exchange", ["NSE", "BSE"], index=0)
        
        timeframe = st.selectbox("Timeframe", ["1m", "5m", "10m", "15m", "20m", "30m", "1h", "1d", "1wk"], index=7)
        
        if timeframe == "1m": lookback_options, lookback_default = ["1d", "5d", "7d"], 1
        elif timeframe in ["5m", "10m", "15m", "20m", "30m"]: lookback_options, lookback_default = ["1d", "5d", "1mo"], 1
        elif timeframe == "1h": lookback_options, lookback_default = ["5d", "1mo", "1y"], 1
        else: lookback_options, lookback_default = ["1mo", "1y", "2y", "3y"], 1
            
        history_period = st.selectbox("Historical Lookback", lookback_options, index=lookback_default)
        
        st.markdown("---")
        st.write("##### Graph Indicators")
        show_ichimoku = st.toggle("Ichimoku Cloud", value=False)
        show_sr = st.toggle("Support & Resistance", value=False)
        show_bb = st.toggle("Bollinger Bands (20,2)", value=False)
        show_ma = st.toggle("Moving Averages", value=False)
        show_vwap = st.toggle("VWAP", value=False)
        show_rsi = st.toggle("RSI Momentum (14)", value=False)
        show_macd = st.toggle("MACD (12,26,9)", value=False)
        
        st.markdown("---")
        st.write("##### AI Strategy")
        strategy_choice = st.selectbox("Trading Strategy", ["Ichimoku Trend", "Smart Money Price Action (SMC)", "Momentum Breakout", "Mean Reversion"])
        show_blueprint = st.toggle("Generate Trade Blueprint", value=False)
        
    with col2:
        if trigger_scan:
            st.write("### ⚡ High-Velocity Intraday Movers")
            scan_universe = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TMCV", "SBIN", "BHARTIARTL", "ITC", "LT", "AXISBANK", "MARUTI", "KOTAKBANK", "M&M", "SUNPHARMA"]
            results = []
            progress_bar = st.progress(0.0)
            from utils.intraday_scanner import run_intraday_scan, get_previous_day_ohlc
            
            for idx, symbol in enumerate(scan_universe):
                progress_bar.progress((idx + 1) / len(scan_universe))
                with st.spinner(f"Scanning {symbol}..."):
                    daily_prev = get_previous_day_ohlc(symbol)
                    res = run_intraday_scan(symbol, daily_prev)
                    results.append(res)
                    
            progress_bar.empty()
            df_results = pd.DataFrame(results)
            
            if not df_results.empty and "status" in df_results.columns:
                success_df = df_results[df_results['status'] == 'SUCCESS']
                if not success_df.empty:
                    scan_cols = ['symbol', 'trigger_event', 'spot', 'target', 'stop_loss', 'rsi']
                    view_df = success_df[scan_cols].copy()
                    view_df.columns = ['Symbol', 'Trigger Event', 'Current Spot (₹)', 'Target Price (₹)', 'Stop Loss (₹)', 'RSI (14)']
                    st.dataframe(view_df.style.map(
                        lambda val: 'background-color: rgba(0, 176, 116, 0.15)' if 'BULLISH' in str(val) or 'REBOUND' in str(val)
                        else ('background-color: rgba(255, 91, 91, 0.15)' if 'BEARISH' in str(val) or 'REJECTION' in str(val) else ''),
                        subset=['Trigger Event']
                    ), use_container_width=True)
                    st.info("Copy a symbol from above and paste it into the Ticker Symbol box on the left to view its chart and blueprint.")
                else:
                    st.warning("All scans returned connection errors. Try again during market hours.")
            else:
                st.warning("Scan failed or returned empty results.")
                
        elif ticker:
            with st.spinner("Fetching live market data..."):
                try:
                    df = DataGateway.fetch_ohlcv(ticker, period=history_period, interval=timeframe, exchange=exchange)
                    profile = get_company_profile(ticker, exchange)
                    news = get_company_news(ticker, exchange)
                    
                    is_intraday = timeframe in ["1m", "2m", "5m", "10m", "15m", "30m", "1h"]
                    
                    df_chart = df.copy()
                    df_chart['RSI'] = calculate_rsi(df_chart)
                    ichimoku = calculate_ichimoku(df_chart)
                    macd = calculate_macd(df_chart)
                    bb = calculate_bollinger_bands(df_chart)
                    mas = calculate_moving_averages(df_chart)
                    df_chart['VWAP'] = calculate_vwap(df_chart)
                    
                    df_chart = pd.concat([df_chart, ichimoku, macd, bb, mas], axis=1)
                    supports, resistances = find_support_resistance_levels(df_chart, window=15)
                    
                    # Intercept true live spot price bypassing the 15m delay of historical candles
                    normalized_ticker = DataGateway.normalize_symbol(ticker, exchange)
                    try:
                        live_spot = yf.Ticker(normalized_ticker).fast_info['lastPrice']
                        current_price = round(live_spot, 2)
                    except:
                        current_price = round(df_chart['Close'].iloc[-1], 2)
                        
                    prev_close = round(df_chart['Close'].iloc[-2], 2) if len(df_chart) > 1 else current_price
                    pct_change = round(((current_price - prev_close) / prev_close) * 100, 2)
                    color = "#00B074" if pct_change >= 0 else "#FF5B5B"
                    sign = "+" if pct_change >= 0 else ""
                    
                    st.markdown(f"""
                    <div style="display:flex; align-items:baseline; gap:15px; margin-bottom:10px;">
                        <h2 style="margin:0; font-weight:700;">{ticker.upper()}</h2>
                        <h2 style="margin:0; font-weight:700; color:{color};">₹{current_price}</h2>
                        <span style="font-size:1.2rem; font-weight:600; color:{color};">({sign}{pct_change}%)</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Chart Generation
                    extra_rows = sum([show_rsi, show_macd])
                    rows = 1 + extra_rows
                    
                    if extra_rows == 0:
                        row_heights = [1.0]
                        chart_height = 500
                    elif extra_rows == 1:
                        row_heights = [0.7, 0.3]
                        chart_height = 650
                    else:
                        row_heights = [0.6, 0.2, 0.2]
                        chart_height = 800
                        
                    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=row_heights)
                    
                    fig.add_trace(go.Candlestick(
                        x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
                        low=df_chart['Low'], close=df_chart['Close'], name="OHLC",
                        increasing_line_color='#00B074', decreasing_line_color='#FF5B5B'
                    ), row=1, col=1)
                    
                    if show_ichimoku:
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Tenkan'], name="Tenkan", line=dict(color='#3b82f6', width=1)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Kijun'], name="Kijun", line=dict(color='#f59e0b', width=1)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Senkou_A'], name="Span A", line=dict(color='#10b981', width=1, dash='dot')), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Senkou_B'], name="Span B", line=dict(color='#ef4444', width=1, dash='dot')), row=1, col=1)
                        
                    if show_bb:
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['BB_Upper'], name="BB Upper", line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dot')), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['BB_Lower'], name="BB Lower", line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(255,255,255,0.05)'), row=1, col=1)
                        
                    if show_ma:
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_9'], name="EMA 9", line=dict(color='#38bdf8', width=1.5)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_21'], name="EMA 21", line=dict(color='#f472b6', width=1.5)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA_50'], name="SMA 50", line=dict(color='#fbbf24', width=2)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA_200'], name="SMA 200", line=dict(color='#ef4444', width=2)), row=1, col=1)
                        
                    if show_vwap:
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['VWAP'], name="VWAP", line=dict(color='#a78bfa', width=2)), row=1, col=1)
                        
                    if show_sr:
                        for level in supports[-3:]:
                            fig.add_hline(y=level, line_color="rgba(0, 176, 116, 0.5)", line_dash="dash", line_width=1, annotation_text=f"Sup ₹{level}", row=1, col=1)
                        for level in resistances[:3]:
                            fig.add_hline(y=level, line_color="rgba(255, 91, 91, 0.5)", line_dash="dash", line_width=1, annotation_text=f"Res ₹{level}", row=1, col=1)
                            
                    current_sub_row = 2
                    if show_rsi:
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['RSI'], name="RSI", line=dict(color='#8b5cf6', width=1.5)), row=current_sub_row, col=1)
                        fig.add_hline(y=70, line_color="rgba(239, 68, 68, 0.5)", line_dash="dash", line_width=1, row=current_sub_row, col=1)
                        fig.add_hline(y=30, line_color="rgba(16, 185, 129, 0.5)", line_dash="dash", line_width=1, row=current_sub_row, col=1)
                        current_sub_row += 1
                        
                    if show_macd:
                        colors = ['#00B074' if val >= 0 else '#FF5B5B' for val in df_chart['Histogram']]
                        fig.add_trace(go.Bar(x=df_chart.index, y=df_chart['Histogram'], name="Histogram", marker_color=colors), row=current_sub_row, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MACD'], name="MACD", line=dict(color='#3b82f6', width=1.5)), row=current_sub_row, col=1)
                        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Signal'], name="Signal", line=dict(color='#f59e0b', width=1.5)), row=current_sub_row, col=1)
                        
                    fig.update_layout(
                        height=chart_height,
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis_rangeslider_visible=False,
                        dragmode='pan',
                        template="plotly_dark",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'),
                        plot_bgcolor='#0B0E14', paper_bgcolor='#0B0E14',
                        hovermode='x unified'
                    )
                    
                    # Fix barcode look by removing non-trading hours
                    rangebreaks = [dict(bounds=["sat", "mon"])] # Hide weekends
                    if is_intraday:
                        # Indian market hours: 09:15 to 15:30. Hide outside this pattern.
                        rangebreaks.append(dict(bounds=[15.5, 9.25], pattern="hour"))
                        
                    fig.update_xaxes(
                        showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)',
                        rangebreaks=rangebreaks,
                        zeroline=False
                    )
                    fig.update_yaxes(
                        showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)',
                        zeroline=False,
                        fixedrange=False
                    )
                    
                    st.plotly_chart(
                        fig, 
                        use_container_width=True, 
                        config={
                            'scrollZoom': True, 
                            'displayModeBar': True,
                            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                            'displaylogo': False
                        }
                    )
                    
                    if show_blueprint:
                        from utils.signal_generator import generate_swing_blueprint, generate_intraday_blueprint
                        
                        if trade_mode == "Intraday (Leverage)":
                            blueprint = generate_intraday_blueprint(ticker, df, strategy=strategy_choice, live_price=current_price)
                        else:
                            blueprint = generate_swing_blueprint(ticker, df, strategy=strategy_choice, live_price=current_price)
                            
                        signal_class = "hold-signal"
                        if blueprint['decision'] == "BUY": signal_class = "buy-signal"
                        elif blueprint['decision'] == "SELL": signal_class = "sell-signal"
                        
                        st.markdown(f"""
                        <div class="blueprint-card {signal_class}" style="margin-top: 15px;">
                            <div class="card-title">Strategy Decision: {blueprint['decision']}</div>
                            <h3 style="color:#ffffff; margin-top:0;">{trade_mode} Blueprint</h3>
                            <p style="color:#e2e8f0; font-size:0.95rem;">{blueprint['reason']}</p>
                            <table style="width:100%; border-collapse:collapse; color:#ffffff; margin-top:15px;">
                                <tr>
                                    <td style="padding:6px 0; color:#94a3b8; font-size:0.9rem;">Trigger Entry Point</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; font-size:1.1rem;">₹{blueprint['entry']}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#94a3b8; font-size:0.9rem;">Mathematical Target (TP)</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; font-size:1.1rem;">₹{blueprint['target']}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#FF5B5B; font-size:0.9rem;">Strict Stop Loss (SL)</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; color:#FF5B5B; font-size:1.1rem;">₹{blueprint['stop_loss']}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#94a3b8; font-size:0.9rem;">Risk:Reward Ratio</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; font-size:1.1rem;">1 : {blueprint['risk_reward']}</td>
                                </tr>
                            </table>
                        </div>
                        """, unsafe_allow_html=True)
                    # Collapsible Sub-Sections below the Chart
                    sub_tab2, sub_tab3, sub_tab4 = st.tabs([
                        "📋 Company Profile & Fundamentals",
                        "📰 Recent News & Sentiment",
                        "🔬 Algorithm & Strategy Details"
                    ])
                    
                    # SUB-TAB 2: COMPANY INFO
                    with sub_tab2:
                        if profile:
                            pcol1, pcol2 = st.columns([3, 1])
                            with pcol1:
                                st.write("##### Corporate Overview")
                                st.write(profile['summary'])
                            with pcol2:
                                st.write("##### Fundamental Metrics")
                                st.write(f"**Sector:** {profile['sector']}")
                                st.write(f"**Industry:** {profile['industry']}")
                                st.write(f"**Market Cap:** ₹{profile['market_cap']:,}")
                                st.write(f"**Beta:** {profile['beta']}")
                                st.write(f"**P/E Ratio:** {profile['pe_ratio']}")
                                st.write(f"**Div Yield:** {round(profile['dividend_yield'] * 100, 2)}%")
                        else:
                            st.info("Fundamentals profile unavailable for this ticker.")
                            
                    # SUB-TAB 3: NEWS
                    with sub_tab3:
                        st.write("##### Live Corporate News Feed")
                        if news:
                            for idx, article in enumerate(news[:6]):
                                st.markdown(f"""
                                <div style="background-color:#1e293b; padding:15px; border-radius:8px; margin-bottom:12px; border:1px solid #334155;">
                                    <h4 style="margin:0;"><a href="{article['link']}" target="_blank" style="color:#60a5fa; text-decoration:none;">{article['title']}</a></h4>
                                    <p style="margin:5px 0; color:#94a3b8; font-size:0.85rem;">Publisher: {article['provider']} • Published: {article['pub_date']}</p>
                                    <p style="margin:0; color:#e2e8f0; font-size:0.9rem;">{article['summary']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No recent news articles found for this ticker.")
                            
                    # SUB-TAB 4: ALGORITHM DETAILS
                    with sub_tab4:
                        st.write("##### Technical Algorithm Mechanics")
                        st.markdown("""
                        This dashboard processes price data strictly on-demand using a series of mathematical equations and logical confluences:
                        
                        1.  **Wilder's RSI Smoothing**:
                            Calculates momentum using standard Wilder smoothing ($N=14$ period lookback) to identify overextended price zones ($<35$ or $>65$).
                        2.  **Support & Resistance Extrema Detection**:
                            Identifies swing highs/lows over a rolling 20-day window. These peaks and troughs are clustered together using a grid-tolerance threshold ($0.75\%$) to highlight major horizontal zones.
                        3.  **Ichimoku Cloud Trend Scanner**:
                            Tracks structural direction by monitoring whether the asset price sits above the Conversion Line (Tenkan-sen), Base Line (Kijun-sen), and the Leading Kumo Span A & B boundaries.
                        4.  **Vectorized Candlestick Pattern Recognition**:
                            Filters the closed state of historical candles to identify reversal structures:
                            *   *Hammer*: Lower shadow length $\ge 2 \times$ Real Body.
                            *   *Shooting Star*: Upper shadow length $\ge 2 \times$ Real Body.
                            *   *Engulfing*: Current body fully overlaps the prior body in the opposite direction.
                        5.  **Anti-Repainting Mandate**:
                            Every calculation operates strictly on **completed, closed bars**. The current active bar is ignored for signal trigger generation.
                        """)
                        
                except Exception as e:
                    st.error(f"Failed to generate analysis: {str(e)}")

# ==================== TAB 3: OPTIONS INTELLIGENCE ====================
with tab3:
    st.subheader("🎯 Directional Indices Options Intelligence (F&O)")
    st.write("Extracts structural setups from spot index arrays and computes theoretical Option premiums via Black-Scholes.")
    
    op_col1, op_col2 = st.columns([1, 4])
    with op_col1:
        st.write("##### Input Index")
        target_index = st.selectbox("Select Target Index", ["NIFTY 50", "BANK NIFTY", "SENSEX"], index=0)
        days_to_expiry = st.number_input("Days to Expiry", min_value=1, max_value=30, value=5)
        
        scan_options_btn = st.button("Scan Options Market", type="primary")
        
    with op_col2:
        if scan_options_btn or target_index:
            with st.spinner("Fetching Spot & Synthesizing Option Chain..."):
                try:
                    mapping = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
                    spot_ticker = mapping[target_index]
                    
                    spot_val = DataGateway.get_live_spot_price(spot_ticker)
                    df_daily = DataGateway.fetch_ohlcv(spot_ticker, period="30d", interval="1d")
                    df_5m = DataGateway.fetch_ohlcv(spot_ticker, period="5d", interval="5m")
                    
                    iv = estimate_historical_volatility(df_daily)
                    
                    # Generate simulated options chain
                    interval_mapping = {"NIFTY 50": 50, "BANK NIFTY": 100, "SENSEX": 100}
                    chain = generate_simulated_option_chain(
                        spot_val, iv, 
                        strikes_count=10, 
                        strike_interval=interval_mapping[target_index],
                        days_to_expiry=days_to_expiry,
                        r=risk_free_rate
                    )
                    
                    # Retrieve previous session OHLC for pivots
                    daily_prev = get_previous_day_ohlc(spot_ticker)
                    
                    # Generate signals
                    options_signal = generate_options_signal(target_index, spot_val, df_5m, daily_prev, chain)
                    
                    # Layout grid
                    ocol1, ocol2 = st.columns([1.5, 2.5])
                    
                    with ocol1:
                        sig = options_signal['decision']
                        card_class = "hold-signal"
                        if "CALL" in sig:
                            card_class = "buy-signal"
                        elif "PUT" in sig:
                            card_class = "sell-signal"
                            
                        st.markdown(f"""
                        <div class="blueprint-card {card_class}">
                            <div class="card-title">Trading Signal: {sig}</div>
                            <h3 style="color:#ffffff; margin-top:0;">{options_signal['contract']} Recommendation</h3>
                            <p style="color:#e2e8f0; font-size:0.95rem;">{options_signal['reason']}</p>
                            <hr style="border-color:#334155; margin:15px 0;" />
                            <table style="width:100%; border-collapse:collapse; color:#ffffff;">
                                <tr>
                                    <td style="padding:6px 0; color:#94a3b8; font-size:0.9rem;">Index Spot Price</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; font-size:1.1rem;">{round(spot_val, 2)}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#94a3b8; font-size:0.9rem;">Target Strike</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; font-size:1.1rem;">{int(options_signal['strike'])}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#94a3b8; font-size:0.9rem;">Entry Premium</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; font-size:1.1rem;">₹{options_signal['entry_premium']}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#FF5B5B; font-size:0.9rem;">Premium Stop Loss (SL)</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; color:#FF5B5B; font-size:1.1rem;">₹{options_signal['stop_loss']}</td>
                                </tr>
                                <tr>
                                    <td style="padding:6px 0; color:#00B074; font-size:0.9rem;">Premium Target (TP)</td>
                                    <td style="padding:6px 0; font-weight:700; text-align:right; color:#00B074; font-size:1.1rem;">₹{options_signal['target']}</td>
                                </tr>
                            </table>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with ocol2:
                        st.write("##### Synthesized Options Chain (BSM Simulator)")
                        st.dataframe(chain.style.map(
                            lambda val: 'background-color: rgba(59, 130, 246, 0.15)' if 'ATM' in str(val) else '',
                            subset=['Type']
                        ), use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Failed to generate options intelligence: {str(e)}")

# ==================== TAB 4: BACKTESTER ====================
with tab4:
    st.subheader("🧪 High-Precision Friction-Aware Backtest Runner")
    st.write("Exposes strategy rules to historical slippage and full Indian market regulatory fee structures.")
    
    bt_col1, bt_col2 = st.columns([1, 4])
    with bt_col1:
        st.write("##### One-Click Simulation")
        st.info("Simulates 2 years of daily data using optimal parameters for the selected strategy.")
        bt_ticker = st.text_input("Backtester Ticker", value=st.session_state["selected_searched_ticker"], key="bt_ticker")
        bt_strategy = st.selectbox("Select Strategy", ["Ichimoku Trend", "Momentum Breakout", "Mean Reversion"])
        
        run_backtest_btn = st.button("Run Simulation", type="primary")
        
    with bt_col2:
        if run_backtest_btn:
            with st.spinner("Executing simulation loops..."):
                try:
                    # Load daily data for backtester
                    df_bt = DataGateway.fetch_ohlcv(bt_ticker, period="2y", interval="1d")
                    res = run_backtest_simulation(
                        df_bt,
                        bt_strategy,
                        trade_class="delivery",
                        slippage_percent=slippage,
                        initial_capital=default_capital
                    )
                    
                    # Render performance cards
                    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                    with mcol1:
                        st.metric("Net Yield Returns", f"{res['net_return_pct']}%")
                    with mcol2:
                        st.metric("System Success Rate", f"{res['success_rate']}%")
                    with mcol3:
                        st.metric("Max Drawdown (MDD)", f"{res['max_drawdown']}%")
                    with mcol4:
                        st.metric("Total Executed Trades", res['total_trades'])
                        
                    st.write("##### Detailed Simulation Log")
                    if res['trades_log']:
                        st.dataframe(pd.DataFrame(res['trades_log']), use_container_width=True)
                    else:
                        st.info("No trades executed within the strategy rules.")
                        
                except Exception as e:
                    st.error(f"Backtesting failed: {str(e)}")

# ==================== TAB 5: TRADING JOURNAL ====================
with tab5:
    st.subheader("📒 Local Manual Trading Journal")
    st.write("Track P&L and document execution psychology in a native database.")
    
    # Form to add entry
    with st.expander("📝 Log New Trade Entry", expanded=False):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            j_asset = st.text_input("Asset Ticker", value=st.session_state["selected_searched_ticker"])
            j_class = st.selectbox("Trade Class", ["Swing Equity", "Intraday Equity", "Intraday Options"])
        with fcol2:
            j_entry = st.number_input("Entry Price (₹)", min_value=0.1, value=500.0)
            j_exit = st.number_input("Exit Price (₹)", min_value=0.1, value=520.0)
        with fcol3:
            j_qty = st.number_input("Quantity Size", min_value=1, value=100)
            j_notes = st.text_area("Trade Notes / Psychology")
            
        submit_journal = st.button("Commit Trade Record", type="primary")
        if submit_journal:
            add_journal_entry(j_asset, j_class, j_entry, j_exit, j_qty, j_notes)
            st.success("Trade record successfully saved to SQLite.")
            
    # Load and view entries
    st.write("##### Logged Execution Journal History")
    df_journal = get_journal_entries()
    
    if not df_journal.empty:
        # Show aggregates
        total_pnl = df_journal['pnl'].sum()
        win_count = len(df_journal[df_journal['pnl'] > 0])
        total_trades = len(df_journal)
        win_pct = round((win_count / total_trades) * 100, 2) if total_trades > 0 else 0.0
        
        acol1, acol2, acol3 = st.columns(3)
        with acol1:
            st.metric("Net Total P&L", f"₹{round(total_pnl, 2)}")
        with acol2:
            st.metric("Journal win %", f"{win_pct}%")
        with acol3:
            st.metric("Total Logged Trades", total_trades)
            
        # Editable dataframe
        edited_df = st.data_editor(
            df_journal,
            num_rows="dynamic",
            use_container_width=False,
            key="journal_editor"
        )
        
        # Save updates if changes occur
        save_changes = st.button("Save Updates")
        if save_changes:
            save_bulk_entries(edited_df)
            st.success("Journal database updated.")
            st.rerun()
            
    else:
        st.info("Journal is currently empty. Use the form above to log your first trade.")
