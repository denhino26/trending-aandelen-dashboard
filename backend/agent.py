from typing import List, Dict, Any


def analyze_stocks(stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for s in stocks_data:
        score = s.get("momentum_score", 50)
        pct = s.get("verandering_pct", 0)
        ratio = s.get("volume_ratio", 1)

        if score >= 65 and pct > 0:
            sentiment = "bullish"
            actie = "kopen"
        elif score <= 35 or pct < -2:
            sentiment = "bearish"
            actie = "vermijden"
        else:
            sentiment = "neutraal"
            actie = "watchlist"

        if ratio > 2.5 and pct < 0:
            risico = "hoog"
        elif ratio > 1.5 or abs(pct) > 3:
            risico = "medium"
        else:
            risico = "laag"

        samenvatting = (
            f"Momentum score {round(score)}/100. "
            f"Koers {'stijgt' if pct > 0 else 'daalt'} {abs(pct):.1f}% "
            f"met {ratio:.1f}x het normale volume."
        )

        results.append({
            "ticker": s["ticker"],
            "bedrijf": s.get("bedrijf", s["ticker"]),
            "score": round(score),
            "sentiment": sentiment,
            "risico": risico,
            "actie": actie,
            "samenvatting": samenvatting,
        })

    return results
