import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import random
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIG & VISIBILITY RE-BALANCE ---
st.set_page_config(page_title="MoneyMaster Terminal 2026", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    /* Fixed: Increased padding to ensure top row is NOT cut off */
    .block-container {
        padding-top: 2.5rem !important; 
        padding-bottom: 2rem !important;
        margin-top: 0px !important; 
    }
    header {visibility: hidden;}
    .main { background-color: #0b0e14; color: white !important; font-size: 11px !important; }

    /* Metric Cards - Blue Theme */
    [data-testid="stMetric"] {
        background-color: #1e3a8a !important; 
        border-radius: 4px; padding: 5px !important; border: 1px solid #3b82f6;
        min-height: 40px !important;
    }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 10px !important; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 14px !important; font-family: monospace; }
    
    .section-head {
        border-left: 4px solid #3b82f6; padding-left: 8px; margin: 10px 0 5px 0; 
        font-weight: bold; color: #3b82f6; font-size: 12px; text-transform: uppercase;
    }
    
    /* BUY/SELL COLORS FIXED */
    div.stButton > button[kind="primary"] { background-color: #16a34a !important; color: white !important; border: none !important; width: 100%; }
    div.stButton > button[kind="secondary"] { background-color: #dc2626 !important; color: white !important; border: none !important; width: 100%; }
    
    .stTextInput > div > div > input { background-color: #161a25; color: white; border: 1px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

if 'selected_scrip' not in st.session_state:
    st.session_state.selected_scrip = "RELIANCE.NS"

# --- 2. DATA FUNCTIONS ---
def get_price_data(symbol):
    try:
        data = yf.download(symbol, period="2d", interval="1d", progress=False)
        if not data.empty and len(data) >= 2:
            ltp = float(data['Close'].iloc[-1].item())
            prev_close = float(data['Close'].iloc[-2].item())
            color = "#00ffcc" if ltp >= prev_close else "#ff4b4b"
            return ltp, color
        return 0.00, "#ffffff"
    except: return 0.00, "#ffffff"

def get_moneycontrol_news(query):
    try:
        q = query.split('.')[0].replace('^', '')
        url = f"https://www.moneycontrol.com/news/tags/{q.lower()}.html"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        news = []
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            arts = soup.find_all('li', class_='clearfix', limit=5)
            for a in arts:
                t_tag = a.find('h2').find('a')
                if t_tag: news.append({'title': t_tag.text.strip(), 'link': t_tag['href']})
        return news
    except: return []

# --- 3. MARKET ROWS (WITH TIMERS) ---

@st.fragment(run_every=61)
def forex_panel():
    st.markdown("<div class='section-head'>💵 FOREX MARKET (61s)</div>", unsafe_allow_html=True)
    c1 = st.columns(6)
    fx = {"USD/INR": "INR=X", "EUR/INR": "EURINR=X", "GBP/INR": "GBPINR=X", "Gold": "GC=F", "Silver": "SI=F", "Crude": "CL=F"}
    for i, (n, s) in enumerate(fx.items()):
        p, _ = get_price_data(s)
        c1[i].metric(n, f"{p:.4f}")

@st.fragment(run_every=31)
def commodity_crypto_panel():
    st.markdown("<div class='section-head'>🌍 WORLD INDICES & CRYPTO (31s)</div>", unsafe_allow_html=True)
    c2 = st.columns(6)
    wd = {"NASDAQ": "^IXIC", "Nikkei": "^N225", "DAX": "^GDAXI", "FTSE": "^FTSE", "BTC": "BTC-USD", "ETH": "ETH-USD"}
    for i, (n, s) in enumerate(wd.items()):
        p, _ = get_price_data(s)
        c2[i].metric(n, f"{p:.2f}")

def indian_market_panel():
    st.markdown("<div class='section-head'>🇮🇳 INDIAN INDICES (Click for Chart)</div>", unsafe_allow_html=True)
    c3 = st.columns(6)
    ind = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "IT": "^CNXIT", "Auto": "^CNXAUTO", "Pharma": "^CNXPHARMA", "Midcap": "^NSEMDCP50"}
    for i, (n, s) in enumerate(ind.items()):
        p, _ = get_price_data(s)
        if c3[i].button(f"{n}\n{p:.2f}", key=f"idx_{s}"):
            st.session_state.selected_scrip = s
            st.rerun()

# Rendering Panels
forex_panel()
commodity_crypto_panel()
indian_market_panel()

# --- 4. MAIN ANALYSIS AREA (CHART LOGIC) ---
st.markdown("---")
col_chart, col_depth = st.columns([3.2, 0.8])

with col_chart:
    st.markdown(f"<div class='section-head'>📈 CHART: {st.session_state.selected_scrip}</div>", unsafe_allow_html=True)
    
    # Selection Controls
    ctrl_1, ctrl_2, ctrl_3 = st.columns([1, 1, 3])
    target = ctrl_1.text_input("Symbol", value=st.session_state.selected_scrip).upper()
    candle = ctrl_2.selectbox("Candle:", ["1m","3m","5m","10m","15m","30m","1h","1d"], index=4)
    period = ctrl_3.radio("Period:", ["1D","1W","1M","3M","6M","1Y","2Y","3Y","5Y"], index=2, horizontal=True)
    
    try:
        p_map = {"1D":"1d","1W":"5d","1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","3Y":"3y","5Y":"5y"}
        h = yf.download(target, period=p_map[period], interval=candle, progress=False)
        
        if not h.empty:
            fig = go.Figure(data=[go.Candlestick(x=h.index, open=h['Open'], high=h['High'], low=h['Low'], close=h['Close'])])
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, width='stretch')
    except: st.error("Chart Syncing...")

with col_depth:
    ltp, ltp_color = get_price_data(target)
    st.markdown(f"<h2 style='text-align:center; color:{ltp_color}; margin-top:35px;'>{ltp:.2f}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'>📊 Depth</div>", unsafe_allow_html=True)
    bid, ask = [], []
    for i in range(5):
        b_p, a_p = ltp - (0.2*(i+1)), ltp + (0.2*(i+1))
        bid.append({"Bid": f"{b_p:.2f}", "BQ": random.randint(100, 5000)})
        ask.append({"Ask": f"{a_p:.2f}", "AQ": random.randint(100, 5000)})
    st.dataframe(pd.concat([pd.DataFrame(bid), pd.DataFrame(ask)], axis=1), hide_index=True, width='stretch')
    st.button("🟢 BUY", type="primary")
    st.button("🔴 SELL", type="secondary")

# --- 5. DUAL NEWS ---
st.markdown("---")
news_search = st.text_input("🔍 Search News:", value=target).upper()
n1, n2 = st.columns(2)
with n1:
    try:
        for n in yf.Ticker(news_search).news[:5]:
            st.markdown(f"<div class='news-card'><a class='news-link' target='_blank' href='{n['link']}'>🔹 {n['title']}</a></div>", unsafe_allow_html=True)
    except: pass
with n2:
    mc_news = get_moneycontrol_news(news_search)
    for n in mc_news:
        st.markdown(f"<div class='news-card'><a class='news-link' target='_blank' href='{n['link']}'>🔸 {n['title']}</a></div>", unsafe_allow_html=True)