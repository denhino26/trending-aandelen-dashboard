import json
import os
import typing
from typing import List, Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """Je bent een AI trading intelligence agent gespecialiseerd in aandelenanalyse.

Voor elk aandeel analyseer je momentum, risico en sentiment op basis van technische data.
Geef voor elk aandeel: ticker, bedrijfsnaam, score (0-100), sentiment (bullish/bearish/neutraal),
risico (laag/medium/hoog), actie (kopen/watchlist/vermijden), en een korte Nederlandse samenvatting.

Wees eerlijk en data-gedreven. Antwoord uitsluitend in het gevraagde JSON formaat."""


class StockAnalysis(typing.TypedDict):
    ticker: str
    bedrijf: str
    score: int
    sentiment: str
    risico: str
    actie: str
    samenvatting: str


class AnalysisResponse(typing.TypedDict):
    analyses: list[StockAnalysis]


model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=AnalysisResponse,
    ),
)


def analyze_stocks(stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not stocks_data:
        return []

    stocks_text = json.dumps(stocks_data, indent=2, ensure_ascii=False)
    prompt = f"Analyseer de volgende {len(stocks_data)} trending aandelen:\n\n{stocks_text}"

    response = model.generate_content(prompt)
    parsed = json.loads(response.text)
    return parsed.get("analyses", [])
