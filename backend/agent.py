import json
import os
from typing import List, Dict, Any

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """Je bent een AI trading intelligence agent gespecialiseerd in aandelenanalyse.

Voor elk aandeel analyseer je momentum, risico en sentiment op basis van technische data.
Geef voor elk aandeel: ticker, bedrijfsnaam, score (0-100), sentiment (bullish/bearish/neutraal),
risico (laag/medium/hoog), actie (kopen/watchlist/vermijden), en een korte Nederlandse samenvatting.

Wees eerlijk en data-gedreven. Antwoord uitsluitend in het gevraagde JSON formaat:
{"analyses": [{"ticker": "...", "bedrijf": "...", "score": 0-100, "sentiment": "bullish/bearish/neutraal", "risico": "laag/medium/hoog", "actie": "kopen/watchlist/vermijden", "samenvatting": "..."}]}"""


def analyze_stocks(stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not stocks_data:
        return []

    stocks_text = json.dumps(stocks_data, indent=2, ensure_ascii=False)
    prompt = f"Analyseer de volgende {len(stocks_data)} trending aandelen:\n\n{stocks_text}"

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
        contents=prompt,
    )

    parsed = json.loads(response.text)
    return parsed.get("analyses", [])
