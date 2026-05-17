import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from textblob import TextBlob
import requests
import time

st.set_page_config(
    page_title="StockSense AI",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background-color: #F0FAF7; }
.block-container { padding: 2rem 2.5rem; }

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes fillBar {
    from { width: 0%; }
    to   { width: 100%; }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

.header-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    animation: fadeSlideUp 0.5s ease both;
}
.header-left h1 {
    font-size: 26px;
    font-weight: 700;
    color: #0A3D30;
    margin: 0;
}
.header-left p {
    font-size: 13px;
    color: #7DBFB0;
    margin: 2px 0 0;
}
.live-badge {
    display: flex;
    align-items: center;
    gap: 7px;
    background: #fff;
    border: 1px solid #C8EDE4;
    border-radius: 20px;
    padding: 7px 16px;
}
.live-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #0D9E7E;
    animation: pulse 1.6s ease-in-out infinite;
}
.live-text {
    font-size: 11px;
    font-weight: 700;
    color: #0D9E7E;
    letter-spacing: 0.8px;
}

.metric-card {
    background: #fff;
    border: 1px solid #D6EFE8;
    border-radius: 14px;
    padding: 18px 20px;
    border-top: 3px solid #0D9E7E;
    animation: fadeSlideUp 0.5s ease both;
}
.metric-label {
    font-size: 10px;
    color: #7DBFB0;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #0A3D30;
    margin: 6px 0 4px;
}
.metric-change-up   { font-size: 12px; color: #0D9E7E; font-weight: 500; }
.metric-change-down { font-size: 12px; color: #E05252; font-weight: 500; }
.metric-change-flat { font-size: 12px; color: #7DBFB0; }

.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #0A3D30;
    margin: 0.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeIn 0.6s ease both;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #D6EFE8;
    margin-left: 8px;
}

.news-card {
    background: #fff;
    border: 1px solid #D6EFE8;
    border-radius: 12px;
    padding: 13px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    animation: slideInLeft 0.4s ease both;
}
.news-card:nth-child(1) { animation-delay: 0.05s; }
.news-card:nth-child(2) { animation-delay: 0.15s; }
.news-card:nth-child(3) { animation-delay: 0.25s; }
.news-card:nth-child(4) { animation-delay: 0.35s; }
.news-card:nth-child(5) { animation-delay: 0.45s; }

.news-dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-top: 4px;
    flex-shrink: 0;
}
.news-headline {
    font-size: 13px;
    color: #2D5A50;
    line-height: 1.55;
    font-weight: 500;
}
.news-sentiment {
    font-size: 10px;
    color: #7DBFB0;
    margin-top: 3px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.verdict-box {
    border-radius: 14px;
    padding: 18px 22px;
    text-align: center;
    margin-bottom: 16px;
    animation: fadeSlideUp 0.5s ease both;
}
.verdict-bullish {
    background: #E6F7F3;
    border: 1px solid #A8E0D2;
}
.verdict-bearish {
    background: #FEF0F0;
    border: 1px solid #F5C0C0;
}
.verdict-neutral {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
}
.verdict-label {
    font-size: 10px;
    color: #7DBFB0;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}
.verdict-text-bull { font-size: 22px; font-weight: 700; color: #0D9E7E; margin: 6px 0 4px; }
.verdict-text-bear { font-size: 22px; font-weight: 700; color: #E05252; margin: 6px 0 4px; }
.verdict-text-neut { font-size: 22px; font-weight: 700; color: #D97706; margin: 6px 0 4px; }
.verdict-score { font-size: 12px; color: #7DBFB0; }

.score-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
    animation: fadeIn 0.6s ease both;
}
.score-row:nth-child(1) { animation-delay: 0.1s; }
.score-row:nth-child(2) { animation-delay: 0.2s; }
.score-row:nth-child(3) { animation-delay: 0.3s; }
.score-name { font-size: 12px; color: #7DBFB0; width: 62px; flex-shrink: 0; }
.score-track {
    flex: 1;
    height: 6px;
    background: #F0FAF7;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #D6EFE8;
}
.score-fill {
    height: 100%;
    border-radius: 4px;
    animation: fillBar 1s ease both;
    animation-delay: 0.3s;
}
.score-pct { font-size: 11px; color: #7DBFB0; width: 32px; text-align: right; }

section[data-testid="stSidebar"] {
    background: #fff;
    border-right: 1px solid #D6EFE8;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.2rem;
}

div[data-testid="stMetric"] {
    background: transparent;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:24px'>
        <div style='width:36px;height:36px;background:#0D9E7E;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:18px'>📈</div>
        <div>
            <div style='font-size:15px;font-weight:700;color:#0A3D30'>StockSense AI</div>
            <div style='font-size:10px;color:#7DBFB0;letter-spacing:1px;text-transform:uppercase'>Market Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:10px;color:#A8CFC7;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;margin-bottom:6px'>Stock Symbol</div>", unsafe_allow_html=True)
    ticker = st.text_input("", value="RELIANCE.NS", label_visibility="collapsed")

    st.markdown("<div style='font-size:10px;color:#A8CFC7;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;margin-bottom:6px;margin-top:16px'>Time Period</div>", unsafe_allow_html=True)
    period = st.selectbox("", ["1mo", "3mo", "6mo", "1y"], label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid #D6EFE8;margin:24px 0'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#F0FAF7;border:1px solid #C8EDE4;border-radius:10px;padding:14px'>
        <div style='font-size:12px;font-weight:700;color:#0A3D30'>Antony N.</div>
        <div style='font-size:11px;color:#7DBFB0;line-height:1.7;margin-top:2px'>
            AI & Data Science<br>
            Jerusalem College of Engg.<br>
            Chennai
        </div>
    </div>
    """, unsafe_allow_html=True)

if ticker:
    with st.spinner("Fetching live market data..."):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            time.sleep(0.4)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    if data.empty:
        st.error("Stock symbol not found. Try RELIANCE.NS, TCS.NS, INFY.NS")
        st.stop()

    current = data['Close'].iloc[-1]
    high    = data['High'].iloc[-1]
    low     = data['Low'].iloc[-1]
    prev    = data['Close'].iloc[-2]
    change  = current - prev
    change_pct = (change / prev) * 100
    volume  = data['Volume'].iloc[-1]

    # Header
    st.markdown(f"""
    <div class="header-wrap">
        <div class="header-left">
            <h1>{ticker.replace('.NS','').replace('.BO','')} &nbsp;
                <span style='font-size:13px;background:#E6F7F3;color:#0D9E7E;
                             padding:3px 10px;border-radius:6px;font-weight:600'>NSE</span>
            </h1>
            <p>Live data via yFinance · Updates on refresh</p>
        </div>
        <div class="live-badge">
            <div class="live-dot"></div>
            <div class="live-text">LIVE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    arrow = "▲" if change >= 0 else "▼"
    change_class = "metric-change-up" if change >= 0 else "metric-change-down"
    top_color = "#0D9E7E" if change >= 0 else "#E05252"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color:{top_color};animation-delay:0.05s">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">₹{current:,.2f}</div>
            <div class="{change_class}">{arrow} {abs(change_pct):.2f}% today</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color:#34D399;animation-delay:0.1s">
            <div class="metric-label">Day High</div>
            <div class="metric-value">₹{high:,.2f}</div>
            <div class="metric-change-flat">Session peak</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color:#E05252;animation-delay:0.15s">
            <div class="metric-label">Day Low</div>
            <div class="metric-value">₹{low:,.2f}</div>
            <div class="metric-change-flat">Session floor</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        vol_str = f"{volume/1_000_000:.1f}M" if volume >= 1_000_000 else f"{volume/1_000:.1f}K"
        st.markdown(f"""
        <div class="metric-card" style="border-top-color:#7DBFB0;animation-delay:0.2s">
            <div class="metric-label">Volume</div>
            <div class="metric-value">{vol_str}</div>
            <div class="metric-change-flat">Shares traded</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart
    st.markdown("<div class='section-title'>📊 Price Chart</div>", unsafe_allow_html=True)

    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price",
        increasing=dict(line=dict(color='#0D9E7E'), fillcolor='#0D9E7E'),
        decreasing=dict(line=dict(color='#E05252'), fillcolor='#E05252')
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['MA10'],
        mode='lines', name='MA10',
        line=dict(color='#F59E0B', width=2),
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['MA20'],
        mode='lines', name='MA20',
        line=dict(color='#818CF8', width=2),
    ))
    fig.update_layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#F0FAF7',
        font=dict(family='Inter', color='#0A3D30', size=12),
        xaxis=dict(
            gridcolor='#D6EFE8',
            showgrid=True,
            zeroline=False,
            showline=False
        ),
        yaxis=dict(
            gridcolor='#D6EFE8',
            showgrid=True,
            zeroline=False,
            showline=False,
            tickprefix='₹'
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor='#fff',
            bordercolor='#D6EFE8',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=420,
        margin=dict(l=10, r=10, t=40, b=10),
        transition=dict(duration=600, easing='cubic-in-out')
    )
    st.plotly_chart(fig, use_container_width=True)

    # News + Sentiment side by side
    st.markdown("<div class='section-title'>🧠 AI Sentiment Analysis</div>", unsafe_allow_html=True)

    col_news, col_verdict = st.columns([3, 2])

    with col_news:
        try:
            with st.spinner("Loading live headlines..."):
                api_key = st.secrets["NEWS_API_KEY"]
                search_term = ticker.replace(".NS","").replace(".BO","")
                url = f"https://newsapi.org/v2/everything?q={search_term}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
                response = requests.get(url)
                news_data = response.json()

            if news_data["status"] == "ok" and news_data["totalResults"] > 0:
                articles = news_data["articles"]
                total = 0
                scored = []
                for article in articles:
                    headline = article["title"]
                    score = TextBlob(headline).sentiment.polarity
                    total += score
                    if score > 0:
                        dot_color = "#0D9E7E"
                        label = "Positive"
                    elif score < 0:
                        dot_color = "#E05252"
                        label = "Negative"
                    else:
                        dot_color = "#F59E0B"
                        label = "Neutral"
                    scored.append((headline, dot_color, label, score))

                for headline, dot_color, label, score in scored:
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-dot" style="background:{dot_color}"></div>
                        <div>
                            <div class="news-headline">{headline}</div>
                            <div class="news-sentiment">{label} · Score: {score:.2f}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                avg = total / len(articles)
            else:
                st.warning("No live news found. Showing generic sentiment.")
                avg = 0.1
                scored = []

        except Exception as news_err:
            st.warning(f"News fetch failed: {news_err}")
            avg = 0
            scored = []

    with col_verdict:
        pos_count = sum(1 for _, _, l, _ in scored if l == "Positive")
        neg_count = sum(1 for _, _, l, _ in scored if l == "Negative")
        neu_count = sum(1 for _, _, l, _ in scored if l == "Neutral")
        total_count = max(len(scored), 1)

        pos_pct = int((pos_count / total_count) * 100)
        neg_pct = int((neg_count / total_count) * 100)
        neu_pct = 100 - pos_pct - neg_pct

        if avg > 0:
            verdict_class = "verdict-bullish"
            verdict_text_class = "verdict-text-bull"
            verdict_word = "BULLISH 🚀"
        elif avg < 0:
            verdict_class = "verdict-bearish"
            verdict_text_class = "verdict-text-bear"
            verdict_word = "BEARISH ⚠️"
        else:
            verdict_class = "verdict-neutral"
            verdict_text_class = "verdict-text-neut"
            verdict_word = "NEUTRAL ➡️"

        st.markdown(f"""
        <div class="verdict-box {verdict_class}">
            <div class="verdict-label">AI Verdict</div>
            <div class="{verdict_text_class}">{verdict_word}</div>
            <div class="verdict-score">Sentiment score: {avg:.2f}</div>
        </div>

        <div class="score-row">
            <div class="score-name">Positive</div>
            <div class="score-track">
                <div class="score-fill" style="width:{pos_pct}%;background:#0D9E7E"></div>
            </div>
            <div class="score-pct">{pos_pct}%</div>
        </div>
        <div class="score-row">
            <div class="score-name">Neutral</div>
            <div class="score-track">
                <div class="score-fill" style="width:{neu_pct}%;background:#F59E0B"></div>
            </div>
            <div class="score-pct">{neu_pct}%</div>
        </div>
        <div class="score-row">
            <div class="score-name">Negative</div>
            <div class="score-track">
                <div class="score-fill" style="width:{neg_pct}%;background:#E05252"></div>
            </div>
            <div class="score-pct">{neg_pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;margin-top:2rem;padding-top:1rem;
                border-top:1px solid #D6EFE8;font-size:11px;color:#A8CFC7'>
        StockSense AI · Built by Antony N. · Jerusalem College of Engineering · Chennai
    </div>
    """, unsafe_allow_html=True)