import json
import os
from typing import List, Dict, Any

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """Je bent een AI trading intelligence agent gespecialiseerd in aandelenanalyse voor de Nederlandse markt.

Je taak is om trending aandelen te analyseren op basis van technische indicatoren en een duidelijke beoordeling te geven.

Voor elk aandeel analyseer je:
- Momentum (prijs verandering + volume ratio)
- Risicoprofiel (volatiliteit, sector, marktpositie)
- Sentiment (bullish/bearish/neutraal op basis van technische data)
- Actie advies: kopen (sterke koopkans), watchlist (interessant maar afwachten), vermijden (te risicovol of negatief momentum)

Geef altijd eerlijke, data-gedreven analyses. Overdrijf niet en wees realistisch over risico's.
Antwoord uitsluitend in het gevraagde JSON formaat."""

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "analyses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "bedrijf": {"type": "string"},
                    "score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutraal"]},
                    "risico": {"type": "string", "enum": ["laag", "medium", "hoog"]},
                    "actie": {"type": "string", "enum": ["kopen", "watchlist", "vermijden"]},
                    "samenvatting": {"type": "string"},
                },
                "required": ["ticker", "bedrijf", "score", "sentiment", "risico", "actie", "samenvatting"],
                "additionalProperties": False,
            }
        }
    },
    "required": ["analyses"],
    "additionalProperties": False,
}


def analyze_stocks(stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not stocks_data:
        return []

    stocks_text = json.dumps(stocks_data, indent=2, ensure_ascii=False)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Analyseer de volgende {len(stocks_data)} trending aandelen en geef voor elk een beoordeling:\n\n{stocks_text}",
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "stock_analyses",
                    "schema": ANALYSIS_SCHEMA,
                    "strict": True,
                },
            }
        },
    )

    parsed = json.loads(response.content[0].text)
    return parsed.get("analyses", [])
