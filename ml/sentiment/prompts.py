"""
Prompts pour l'analyse de sentiment avec Mistral.

Prompts optimisés pour l'analyse de headlines financiers.
"""

# Prompt système définissant le rôle et le format de réponse
SENTIMENT_SYSTEM_PROMPT = """Tu es un analyste financier expert en sentiment de marché.

Ton rôle est d'analyser des headlines financiers et de donner un score de sentiment.

RÈGLES:
1. Score entre -1.0 (très négatif) et +1.0 (très positif)
2. 0.0 = neutre
3. Réponds UNIQUEMENT avec un JSON valide
4. Pas d'explications, juste le JSON

FORMAT DE RÉPONSE:
{"score": <float>, "label": "<positive|negative|neutral>"}

EXEMPLES:
- "S&P 500 reaches all-time high amid strong earnings" → {"score": 0.8, "label": "positive"}
- "Markets crash as recession fears grow" → {"score": -0.9, "label": "negative"}
- "Fed holds rates steady, markets unchanged" → {"score": 0.0, "label": "neutral"}
- "Tech stocks rally on AI optimism" → {"score": 0.7, "label": "positive"}
- "Oil prices surge on supply concerns" → {"score": -0.3, "label": "negative"}
"""


def create_sentiment_prompt(headline: str) -> str:
    """
    Crée le prompt utilisateur pour analyser un headline.

    Args:
        headline: Le headline à analyser

    Returns:
        Le prompt formaté
    """
    return f"""Analyse le sentiment de ce headline financier:

"{headline}"

Réponds avec le JSON uniquement."""


def create_batch_prompt(headlines: list[str]) -> str:
    """
    Crée un prompt pour analyser plusieurs headlines en une fois.

    Args:
        headlines: Liste de headlines à analyser

    Returns:
        Le prompt formaté
    """
    headlines_text = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])

    return f"""Analyse le sentiment de ces headlines financiers:

{headlines_text}

Réponds avec un JSON array:
[{{"headline": 1, "score": <float>, "label": "<label>"}}, ...]"""


# Exemples de test pour validation
TEST_HEADLINES = [
    ("S&P 500 reaches all-time high amid strong earnings", 0.8, "positive"),
    ("Markets crash as recession fears grow", -0.9, "negative"),
    ("Fed holds rates steady, markets unchanged", 0.0, "neutral"),
    ("Tech stocks rally on AI optimism", 0.7, "positive"),
    ("Unemployment rises sharply in latest report", -0.6, "negative"),
    ("Bitcoin falls below $30,000 amid regulatory concerns", -0.5, "negative"),
    ("Corporate earnings beat expectations across sectors", 0.6, "positive"),
    ("Trade tensions escalate between US and China", -0.4, "negative"),
]
