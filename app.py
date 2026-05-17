import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from textblob import TextBlob
import requests

st.title("StockSense AI")
st.subheader("Indian Market Intelligence Dashboard")

ticker = st.text_input("Enter Stock Symbol", value="RELIANCE.NS")
period = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"])

if ticker:
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)

        if data.empty:
            st.error("Stock symbol not found. Please enter a valid NSE symbol like RELIANCE.NS")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"₹{data['Close'].iloc[-1]:.2f}")
            col2.metric("Day High", f"₹{data['High'].iloc[-1]:.2f}")
            col3.metric("Day Low", f"₹{data['Low'].iloc[-1]:.2f}")

            # Calculate moving averages
            data['MA10'] = data['Close'].rolling(window=10).mean()
            data['MA20'] = data['Close'].rolling(window=20).mean()

            fig = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Price"
            )])

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA10'],
                mode='lines',
                name='MA10',
                line=dict(color='orange', width=1.5)
            ))

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA20'],
                mode='lines',
                name='MA20',
                line=dict(color='cyan', width=1.5)
            ))

            fig.update_layout(
                title=f"{ticker} Price Chart",
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig)

            # Live News + Sentiment
            st.subheader("AI Sentiment Analysis")

            try:
                api_key = st.secrets["NEWS_API_KEY"]
                # Strip .NS or .BO for better news search
                search_term = ticker.replace(".NS", "").replace(".BO", "")
                url = f"https://newsapi.org/v2/everything?q={search_term}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
                response = requests.get(url)
                news_data = response.json()

                if news_data["status"] == "ok" and news_data["totalResults"] > 0:
                    articles = news_data["articles"]
                    total = 0
                    for article in articles:
                        headline = article["title"]
                        score = TextBlob(headline).sentiment.polarity
                        total += score
                        sentiment = "🟢 Positive" if score > 0 else "🔴 Negative" if score < 0 else "🟡 Neutral"
                        st.write(f"{sentiment} — {headline}")

                    avg = total / len(articles)
                    if avg > 0:
                        st.success(f"AI Verdict: BULLISH 📈 (Score: {avg:.2f})")
                    elif avg < 0:
                        st.error(f"AI Verdict: BEARISH 📉 (Score: {avg:.2f})")
                    else:
                        st.warning("AI Verdict: NEUTRAL ➡️")

                else:
                    st.warning("No news found for this stock. Showing generic analysis.")
                    headlines = [
                        "Company reports strong quarterly earnings",
                        "Stock rises amid positive market sentiment",
                        "Analysts upgrade rating to buy",
                        "Revenue growth beats expectations",
                        "Market volatility affects stock price"
                    ]
                    total = 0
                    for h in headlines:
                        score = TextBlob(h).sentiment.polarity
                        total += score
                        sentiment = "🟢 Positive" if score > 0 else "🔴 Negative" if score < 0 else "🟡 Neutral"
                        st.write(f"{sentiment} — {h}")
                    avg = total / len(headlines)
                    if avg > 0:
                        st.success("AI Verdict: BULLISH 📈")
                    elif avg < 0:
                        st.error("AI Verdict: BEARISH 📉")
                    else:
                        st.warning("AI Verdict: NEUTRAL ➡️")

            except Exception as news_error:
                st.warning(f"News fetch failed: {news_error}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")