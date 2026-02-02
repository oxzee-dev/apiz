from fastapi import FastAPI, HTTPException
import yfinance as yf
from exa_py import Exa
import os
from datetime import datetime, timedelta

app = FastAPI(title="Simple Stock + Recent News API")

# ──────────────────────────────────────────────
# STOCK ENDPOINT (unchanged)
# ──────────────────────────────────────────────
@app.get("/ticker/{ticker}")
def get_ticker(ticker: str):
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        mcap = info.get("marketCap")
        
        if not price or not mcap:
            raise ValueError("No price or market cap data")
            
        return {
            "ticker": ticker.upper(),
            "price": float(price),
            "marketCap": int(mcap)
        }
    except Exception as e:
        raise HTTPException(404, f"Error: {str(e)}")


# ──────────────────────────────────────────────
# NEWS ENDPOINT – using exa-py client
# ──────────────────────────────────────────────
@app.get("/news/{topic}")
def get_recent_news(topic: str):
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise HTTPException(500, "EXA_API_KEY environment variable is not set")

    try:
        exa = Exa(api_key=api_key)

        # Calculate date from one week ago
        one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        response = exa.search(
            query=topic,
            # num_results=10,
            # use_autoprompt=True,           # helps improve relevance
            type="auto",                 # semantic/neural search
            start_published_date=one_week_ago,
            numResults=10,
            contents={
                "highlights": true,        # 2 sentences per result
                # "highlights_per_url": 1    # one highlight block per result
            }
        )

        # # Calculate date from one week ago
        # one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        # response = exa.search(
        #     query=topic,
        #     num_results=10,
        #     # use_autoprompt=True,           # helps improve relevance
        #     type="neural",                 # semantic/neural search
        #     start_published_date=one_week_ago,
        #     highlights={
        #         "num_sentences": 2,        # 2 sentences per result
        #         "highlights_per_url": 1    # one highlight block per result
        #     }
        # )


        zee_results = exa.search(
            "blog post about artificial intelligence",
              type="auto",
              contents={"text": True})

        articles = []
        for result in response.results:
            articles.append({
                "title": result.title or "No title",
                "url": result.url,
                "published": result.published_date or "N/A",
                "highlights": result.highlights or ["No highlights available"]
            })

        # return {
        #     "topic": topic,
        #     "articles": articles,
        #     "count": len(articles),
        #     "time_range": f"from {one_week_ago} to now"
        # }
        return zee_results

    except Exception as e:
        raise HTTPException(500, f"Exa error: {str(e)}")


# Health check
@app.get("/health")
def health():
    return {"status": "ok"}
