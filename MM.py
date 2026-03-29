import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. CONFIG & LOGO ---
LOGO_FILE = "app_logo.png" 
logo_exists = os.path.exists(LOGO_FILE)

st.set_page_config(
    page_title="MarketMaster Terminal 2026", 
    layout="wide", 
    page_icon=LOGO_FILE if logo_exists else "⚡"
)

# --- 2. COMPLETE STYLING ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; margin-top: 0px !important; }
    header {visibility: hidden;}
    .main { background-color: #0b0e14; }
    h1, h2, h3, p, span, div, label { color: #ffffff !important; font-size: 11px; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 11px !important; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 18px !important; font-family: monospace; }
    [data-testid="stMetric"] { background-color: #1e3a8a !important; border-radius: 4px; padding: 10px !important; border: 1px solid #3b82f6; min-height: 100px; }
    .stats-box { font-size: 10px; color: #ffffff !important; line-height: 1.3; margin-top: 4px; border-top: 1px solid #3b82f6; padding-top: 3px; }
    .section-head { border-left: 4px solid #3b82f6; padding-left: 8px; margin: 15px 0 10px 0; font-weight: bold; color: #3b82f6 !important; font-size: 13px; text-transform: uppercase; }
    div.stButton > button { background-color: #1e3a8a !important; color: white !important; border: 1px solid #3b82f6 !important; width: 100%; height: 90px !important; font-weight: bold; white-space: pre-wrap !important; }
    
    @media (max-width: 768px) {
        [data-testid="stMetricValue"] { font-size: 14px !important; }
        [data-testid="stMetricLabel"] { font-size: 9px !important; }
        div.stButton > button { height: 65px !important; font-size: 10px !important; padding: 2px !important; }
        .section-head { font-size: 11px !important; }
        [data-testid="stPlotlyChart"] { height: 350px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
def get_stable_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2d")
        if df is not None and not df.empty and len(df) >= 2:
            ltp = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            high = df['High'].iloc[-1]
            low = df['Low'].iloc[-1]
            chg = ((ltp - prev) / prev) * 100
            arrow = "▲" if chg >= 0 else "▼"
            return {"ltp": ltp, "prev": prev, "high": high, "low": low, "pct": chg, "arrow": arrow}
    except: return None

# --- 4. SYMBOLS ---
fx_dict = {"USD/INR": "INR=X", "EUR/INR": "EURINR=X", "GBP/INR": "GBPINR=X", "GOLD": "GC=F", "SILVER": "SI=F", "BITCOIN": "BTC-USD"}
wd_dict = {"NASDAQ": "^IXIC", "S&P 500": "^GSPC", "Nikkei 225": "^N225", "DAX": "^GDAXI", "FTSE 100": "^FTSE", "CAC 40": "^FCHI"}
in_dict = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Nifty IT": "^CNXIT", "Nifty Auto": "^CNXAUTO", "Pharma": "^CNXPHARMA", "Midcap 50": "^NSEMDCP50"}

# --- 5. PANELS ---
@st.fragment(run_every=122)
def world_market_panel():
    st.markdown("<div class='section-head'>💵 FOREX & METALS (122s Sync)</div>", unsafe_allow_html=True)
    c1 = st.columns(6)
    for i, (name, sym) in enumerate(fx_dict.items()):
        d = get_stable_data(sym)
        if d:
            c1[i].metric(name, f"{d['ltp']:.2f}", f"{d['arrow']} {d['pct']:.2f}%")
            c1[i].markdown(f"<div class='stats-box'>H: {d['high']:.2f} | L: {d['low']:.2f}<br>P: {d['prev']:.2f}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'>🌍 WORLD INDICES (122s Sync)</div>", unsafe_allow_html=True)
    c2 = st.columns(6)
    for i, (name, sym) in enumerate(wd_dict.items()):
        d = get_stable_data(sym)
        if d:
            c2[i].metric(name, f"{d['ltp']:.2f}", f"{d['arrow']} {d['pct']:.2f}%")
            c2[i].markdown(f"<div class='stats-box'>H: {d['high']:.2f} | L: {d['low']:.2f}</div>", unsafe_allow_html=True)

@st.fragment(run_every=61)
def indian_market_panel():
    st.markdown("<div class='section-head'>🇮🇳 INDIAN MARKET (61s Sync)</div>", unsafe_allow_html=True)
    c3 = st.columns(6)
    for i, (name, sym) in enumerate(in_dict.items()):
        d = get_stable_data(sym)
        if d:
            c3[i].button(f"{name}\n{d['ltp']:.2f}\n{d['arrow']} {d['pct']:.2f}%", key=f"btn_{sym}")
            c3[i].markdown(f"<div class='stats-box'>H: {d['high']:.2f} | L: {d['low']:.2f}</div>", unsafe_allow_html=True)

if logo_exists: st.image(LOGO_FILE, width=150)
world_market_panel()
indian_market_panel()

# --- 6. CHART & MOVERS (FIXED) ---
@st.fragment(run_every=61)
def analysis_panel():
    st.markdown("---")
    st.markdown("<div class='section-head'>🇮🇳 INDIAN CHARTING & MOVERS (61s Sync)</div>", unsafe_allow_html=True)
    
    col_ctrl = st.columns([2, 2, 1, 1])
    # FIXED: naming consistency
    selected_idx = col_ctrl[0].selectbox("Indian Index:", list(in_dict.keys()), index=0)
    raw_search = col_ctrl[1].text_input("Search Stock (e.g. SBIN):", value="")
    
    if raw_search:
        final_target = raw_search.upper() if "." in raw_search else f"{raw_search.upper()}.NS"
    else:
        final_target = in_dict[selected_idx] # Fixed here from selected_in_idx
    
    candle = col_ctrl[2].selectbox("Interval:", ["1m","5m","10m","15m","20m","30m","60m","1d"], index=3)
    period_val = col_ctrl[3].selectbox("Period:", ["1d","7d","15d","30d","2mo","3mo","6mo","1y","2y","3y","5y"], index=3)
    
    try:
        chart_data = yf.download(final_target, period=period_val, interval=candle, progress=False)
        if not chart_data.empty:
            fig = go.Figure(data=[go.Candlestick(x=chart_data.index, open=chart_data['Open'], high=chart_data['High'], low=chart_data['Low'], close=chart_data['Close'])])
            fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, width='stretch')
    except: st.warning("Connecting to NSE Stream...")

    st.markdown("<div class='section-head'>🚀 LIVE NSE TOP MOVERS</div>", unsafe_allow_html=True)
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "BHARTIARTL.NS"]
    m_list = []
    for s in stocks:
        res = get_stable_data(s)
        if res: m_list.append({"Stock": s.replace(".NS",""), "LTP": round(res['ltp'],2), "%": round(res['pct'],2)})
    
    if m_list:
        df = pd.DataFrame(m_list).sort_values(by="%", ascending=False)
        m1, m2 = st.columns(2)
        m1.dataframe(df.head(4), hide_index=True, width='stretch')
        m2.dataframe(df.tail(4), hide_index=True, width='stretch')

analysis_panel()