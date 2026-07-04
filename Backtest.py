"""
StockSense AI — Sentiment Backtest
-----------------------------------
Question this answers: does news sentiment on day X actually predict
the stock's price move on day X+1?

How it works, step by step:
1. Pull daily price history for the ticker (via yfinance).
2. For each day in that history, fetch news headlines published on
   that specific day (via NewsAPI's date-range filtering).
3. Score those headlines with the same VADER+TextBlob ensemble used
   in app.py, and average them into one "sentiment score" for the day.
4. Compare that day's sentiment score to the ACTUAL price return from
   that day's close to the next day's close.
5. Check two things across all days:
   - Correlation: as sentiment goes up, does next-day return tend to
     go up too? (Pearson correlation, ranges -1 to +1)
   - Hit rate: what % of days did the SIGN of sentiment (positive/
     negative) match the SIGN of the next day's return?

A hit rate around 50% means sentiment is no better than a coin flip.
Meaningfully above 50% (and a positive correlation) means there's
something real here worth building a signal on.

IMPORTANT LIMITATION: NewsAPI's free tier only returns articles from
roughly the last 30 days, and caps you at 100 requests/day. This
script makes 1 request per day tested, so don't set days_back above
~25-30 or you'll burn your daily quota and/or hit the free-tier date
limit.
"""

import time
from datetime import datetime, timedelta
from urllib.parse import quote

import requests
import yfinance as yf
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

vader = SentimentIntensityAnalyzer()


def get_daily_sentiment(company_query, date_str, api_key):
    """
    Fetch headlines published on a single specific day and return
    the ensemble sentiment average for that day.

    date_str must be 'YYYY-MM-DD'.

    IMPORTANT BUG FIX: the original version set from=date_str AND
    to=date_str. NewsAPI reads bare dates as midnight timestamps, so
    from=2026-06-12 to=2026-06-12 means "from 2026-06-12T00:00:00 to
    2026-06-12T00:00:00" — a ZERO-SECOND window. That's why every
    single day returned "no news found" regardless of ticker: the
    window never actually covered any part of the day. Setting `to`
    to the NEXT calendar day gives NewsAPI a real 24-hour window that
    covers the intended day.
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    next_day_str = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    url = (
        "https://newsapi.org/v2/everything"
        f"?qInTitle={quote(company_query)}"
        f"&from={date_str}&to={next_day_str}"
        "&language=en&sortBy=relevancy&pageSize=10"
        f"&apiKey={api_key}"
    )
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        # IMPORTANT: don't silently treat API errors the same as "genuinely
        # no news that day" — that hides real problems like hitting your
        # daily rate limit, an invalid key, or a bad request. Print the
        # actual reason so it's obvious what's happening.
        print(f"  -> API error: {data.get('code', '?')} - {data.get('message', 'unknown error')}")
        return None

    if data.get("totalResults", 0) == 0:
        return None  # genuinely no news that day

    scores = []
    for article in data["articles"]:
        headline = article["title"]
        if not headline:
            continue
        tb = TextBlob(headline).sentiment.polarity
        vd = vader.polarity_scores(headline)["compound"]
        scores.append((tb + vd) / 2)

    if not scores:
        return None

    return sum(scores) / len(scores)


def run_backtest(ticker, company_query, api_key, days_back=20):
    print(f"\n=== Backtesting {ticker} over last {days_back} days ===\n")

    # Pull enough price history to cover the window plus one extra day
    # (since we need day X+1's close to measure day X's return).
    stock = yf.Ticker(ticker)
    hist = stock.history(period=f"{days_back + 10}d")
    hist = hist.tail(days_back + 1)  # keep only what we need

    results = []

    # We stop one day before the end, because the last day has no
    # "next day" to compare against yet.
    for i in range(len(hist) - 1):
        date = hist.index[i]
        date_str = date.strftime("%Y-%m-%d")

        close_today = hist["Close"].iloc[i]
        close_tomorrow = hist["Close"].iloc[i + 1]
        actual_return_pct = ((close_tomorrow - close_today) / close_today) * 100

        sentiment = get_daily_sentiment(company_query, date_str, api_key)

        if sentiment is not None:
            results.append({
                "date": date_str,
                "sentiment": sentiment,
                "next_day_return_pct": actual_return_pct,
            })
            print(f"{date_str} | sentiment: {sentiment:+.3f} | "
                  f"next-day return: {actual_return_pct:+.2f}%")
        else:
            print(f"{date_str} | no news found, skipping")

        time.sleep(1)  # be polite to the free-tier rate limit

    if len(results) < 5:
        print("\nNot enough days with news data to draw a real conclusion. "
              "Try a more widely-covered stock or a longer window.")
        return results

    # --- Correlation ---
    n = len(results)
    sentiments = [r["sentiment"] for r in results]
    returns = [r["next_day_return_pct"] for r in results]

    mean_s = sum(sentiments) / n
    mean_r = sum(returns) / n

    cov = sum((s - mean_s) * (r - mean_r) for s, r in zip(sentiments, returns))
    std_s = sum((s - mean_s) ** 2 for s in sentiments) ** 0.5
    std_r = sum((r - mean_r) ** 2 for r in returns) ** 0.5

    correlation = cov / (std_s * std_r) if std_s > 0 and std_r > 0 else 0

    # --- Hit rate: did sentiment's sign match next-day return's sign? ---
    hits = sum(
        1 for r in results
        if (r["sentiment"] > 0 and r["next_day_return_pct"] > 0)
        or (r["sentiment"] < 0 and r["next_day_return_pct"] < 0)
    )
    hit_rate = (hits / n) * 100

    print(f"\n--- Results over {n} usable days ---")
    print(f"Correlation (sentiment vs next-day return): {correlation:+.3f}")
    print(f"Hit rate (sentiment sign matched next-day direction): {hit_rate:.1f}%")

    # --- Statistical significance of the hit rate ---
    # A hit rate of 55% sounds better than a coin flip, but with a small
    # sample size that could easily just be noise. This is a one-sample
    # z-test: it checks how many standard errors away from 50% (pure
    # chance) our observed hit rate actually is.
    #
    # p = observed hit rate (as a fraction, e.g. 0.55)
    # Standard error of a proportion at n samples = sqrt(0.5*0.5/n)
    # z = (p - 0.5) / standard_error
    #
    # |z| > 1.96 roughly corresponds to "statistically significant at the
    # 95% confidence level" — meaning it's unlikely (less than 5% chance)
    # this hit rate happened by pure luck if there were truly no edge.
    p = hits / n
    standard_error = (0.5 * 0.5 / n) ** 0.5
    z_score = (p - 0.5) / standard_error if standard_error > 0 else 0

    print(f"Z-score vs 50% baseline: {z_score:+.2f} (n={n})")

    if n < 30:
        print(f"Note: n={n} is below the recommended minimum (~30) for a "
              f"reliable significance test. Result is directional only.")

    if abs(z_score) >= 1.96:
        direction = "positive" if z_score > 0 else "inverse"
        print(f"Verdict: SIGNIFICANT ({direction} relationship, 95% confidence)")
    else:
        print(f"Verdict: NOT SIGNIFICANT — hit rate not distinguishable "
              f"from chance (50%) at this sample size.")

    return results


if __name__ == "__main__":
    # Fill these in before running:
    NEWS_API_KEY = "fa6662af416d422fbe1c956acbeb6881"
    TICKER = "TCS.NS"

    # Using TCS instead of Reliance here on purpose. "Reliance" is on the
    # ambiguous-word blocklist in app.py (it's also a normal English word),
    # so we search only the exact quoted full name for it — which is safer
    # but much narrower, and turned out to have almost no exact-phrase
    # matches on any single specific day. TCS isn't ambiguous, so we can
    # search both the ticker AND the full name, giving much better daily
    # coverage — good for actually proving the pipeline works end-to-end.
    COMPANY_QUERY = 'TCS OR "Tata Consultancy Services"'

    run_backtest(TICKER, COMPANY_QUERY, NEWS_API_KEY, days_back=15)