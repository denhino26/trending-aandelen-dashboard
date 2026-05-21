import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from data import get_stock_data, WATCHLIST
from agent import analyze_stocks

app = FastAPI(title="Trending Aandelen Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/trending")
def get_trending():
    try:
        stocks = get_stock_data(WATCHLIST)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen marktdata: {e}")

    if not stocks:
        raise HTTPException(status_code=503, detail="Geen marktdata beschikbaar")

    top10 = stocks[:10]

    try:
        analyses = analyze_stocks(top10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij Claude analyse: {e}")

    analyses_by_ticker = {a["ticker"]: a for a in analyses}

    result = []
    for stock in top10:
        ticker = stock["ticker"]
        analyse = analyses_by_ticker.get(ticker, {})
        result.append({**stock, **analyse})

    return {"aandelen": result, "totaal": len(result)}


frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
