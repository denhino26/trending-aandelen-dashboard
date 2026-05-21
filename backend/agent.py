import json
import os
import re
import time
from typing import List, Dict, Any

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
]

SYSTEM_PROMPT = """Je bent een AI trading intelligence agent gespecialiseerd in aandelenanalyse.

Voor elk aandeel analyseer je momentum, risico en sentiment op basis van technische data.
Geef voor elk aandeel een beoordeling met: ticker, bedrijfsnaam, score (0-100 geheel getal),
sentiment (bullish/bearish/neutraal), risico (laag/medium/hoog),
actie (kopen/watchlist/vermijden), en een korte Nederlandse samenvatting.

Antwoord UITSLUITEND met een JSON object in dit formaat, zonder markdown of uitleg:
{"analyses":[{"ticker":"...","bedrijf":"...","score":50,"sentiment":"bullish","risico":"medium","actie":"kopen","samenvatting":"..."}]}"""


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def _call_gemini(prompt: str) -> str:
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                    ),
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_error = e
                err = str(e)
                if "503" in err or "429" in err or "UNAVAILABLE" in err or "RESOURCE_EXHAUSTED" in err:
                    if attempt == 0:
                        time.sleep(3)
                    continue
                break
    raise last_error


def analyze_stocks(stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not stocks_data:
        return []

    stocks_text = json.dumps(stocks_data, indent=2, ensure_ascii=False)
    prompt = f"Analyseer de volgende {len(stocks_data)} trending aandelen:\n\n{stocks_text}"

    text = _call_gemini(prompt)
    parsed = _parse_json(text)
    return parsed.get("analyses", [])
