import yfinance as yf
import plotly.graph_objects as go
from textblob import TextBlob

stock = yf.Ticker("RELIANCE.NS")
data = stock.history(period="1mo")

# Simulate some news headlines about the stock
headlines = [
    "Reliance Industries reports record quarterly profit",
    "Jio expands 5G network across India",
    "Reliance stock falls amid global market concerns",
    "Mukesh Ambani announces major new investment plan",
    "Reliance retail growth slows down this quarter"
]

print("=== AI Sentiment Analysis ===\n")

total_score = 0
for headline in headlines:
    analysis = TextBlob(headline)
    score = analysis.sentiment.polarity
    total_score += score
    
    if score > 0:
        sentiment = "POSITIVE 📈"
    elif score < 0:
        sentiment = "NEGATIVE 📉"
    else:
        sentiment = "NEUTRAL  ➡️"
    
    print(f"{sentiment} | Score: {score:.2f} | {headline}")

average = total_score / len(headlines)
print(f"\nOverall Sentiment: {average:.2f}")

if average > 0:
    print("AI Verdict: BULLISH — Positive market sentiment")
elif average < 0:
    print("AI Verdict: BEARISH — Negative market sentiment")
else:
    print("AI Verdict: NEUTRAL — Mixed signals")