import yfinance as yf
from typing import List, Dict, Any

WATCHLIST = [
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN",
    "META", "GOOGL", "AMD", "PLTR", "SMCI",
    "ARM", "AVGO", "MSTR", "COIN", "SPY"
]


def get_stock_data(tickers: List[str] = WATCHLIST) -> List[Dict[str, Any]]:
    results = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")

            if hist.empty or len(hist) < 2:
                continue

            current_price = float(hist["Close"].iloc[-1])
            prev_price = float(hist["Close"].iloc[-2])
            price_change_pct = ((current_price - prev_price) / prev_price) * 100

            current_volume = float(hist["Volume"].iloc[-1])
            avg_volume = float(hist["Volume"].iloc[:-1].mean())
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            momentum_score = min(100, max(0,
                50 + price_change_pct * 5 + (volume_ratio - 1) * 20
            ))

            info = stock.fast_info
            company_name = getattr(info, "company_name", ticker) or ticker

            results.append({
                "ticker": ticker,
                "bedrijf": company_name,
                "prijs": round(current_price, 2),
                "verandering_pct": round(price_change_pct, 2),
                "volume": int(current_volume),
                "volume_ratio": round(volume_ratio, 2),
                "momentum_score": round(momentum_score, 1),
            })

        except Exception as e:
            print(f"Fout bij ophalen data voor {ticker}: {e}")
            continue

    results.sort(key=lambda x: x["momentum_score"], reverse=True)
    return results
