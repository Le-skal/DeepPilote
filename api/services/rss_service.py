"""
Service pour récupérer et analyser les news depuis des flux RSS.

Utilise le flux RSS de L'AGEFI pour avoir des news financières françaises.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import httpx

from api.services.sentiment_service import analyze_headlines_async

# Configuration des flux RSS
RSS_FEEDS = {
    "agefi": {
        "url": "https://www.agefi.fr/index.rss",
        "name": "L'AGEFI",
        "language": "fr",
    },
}

# Cache TTL en secondes (1 heure)
CACHE_TTL = 3600


class RSSItem:
    """Un item de flux RSS."""

    def __init__(
        self,
        title: str,
        link: str,
        pub_date: datetime | None = None,
        description: str | None = None,
    ):
        self.title = title
        self.link = link
        self.pub_date = pub_date
        self.description = description


def parse_rss_date(date_str: str) -> datetime | None:
    """Parse une date RSS (format RFC 822)."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


async def fetch_rss_feed(feed_key: str = "agefi") -> list[RSSItem]:
    """
    Récupère et parse un flux RSS.

    Args:
        feed_key: Clé du flux dans RSS_FEEDS

    Returns:
        Liste d'items RSS
    """
    if feed_key not in RSS_FEEDS:
        raise ValueError(f"Flux RSS inconnu: {feed_key}")

    feed_config = RSS_FEEDS[feed_key]
    url = feed_config["url"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()

    # Parser le XML
    root = ET.fromstring(response.content)

    items = []
    # RSS 2.0 structure: rss/channel/item
    for item in root.findall(".//item"):
        title_elem = item.find("title")
        link_elem = item.find("link")
        pub_date_elem = item.find("pubDate")
        desc_elem = item.find("description")

        if title_elem is not None and title_elem.text:
            items.append(
                RSSItem(
                    title=title_elem.text.strip(),
                    link=link_elem.text.strip() if link_elem is not None and link_elem.text else "",
                    pub_date=(
                        parse_rss_date(pub_date_elem.text)
                        if pub_date_elem is not None and pub_date_elem.text
                        else None
                    ),
                    description=(
                        desc_elem.text.strip() if desc_elem is not None and desc_elem.text else None
                    ),
                )
            )

    return items


async def get_recent_headlines(
    feed_key: str = "agefi",
    max_items: int = 50,
    max_days: int = 7,
) -> list[str]:
    """
    Récupère les titres récents d'un flux RSS.

    Args:
        feed_key: Clé du flux
        max_items: Nombre max de titres
        max_days: Ancienneté max en jours

    Returns:
        Liste de titres
    """
    items = await fetch_rss_feed(feed_key)

    # Filtrer par date si disponible
    cutoff_date = datetime.now().astimezone() - timedelta(days=max_days)

    filtered = []
    for item in items:
        # Si pas de date, on garde (on suppose que c'est récent)
        if item.pub_date is None:
            filtered.append(item.title)
        elif item.pub_date.replace(tzinfo=None) > cutoff_date.replace(tzinfo=None):
            filtered.append(item.title)

        if len(filtered) >= max_items:
            break

    return filtered


async def analyze_market_sentiment_from_rss(
    feed_key: str = "agefi",
    max_headlines: int = 30,
) -> dict:
    """
    Analyse le sentiment du marché à partir des news RSS.

    Args:
        feed_key: Clé du flux RSS
        max_headlines: Nombre de titres à analyser

    Returns:
        Dict avec score, label, interpretation, headlines analysés
    """
    # Récupérer les titres récents
    headlines = await get_recent_headlines(feed_key, max_items=max_headlines, max_days=3)

    if not headlines:
        return {
            "score": 0.0,
            "label": "neutre",
            "interpretation": "Aucune news disponible pour l'analyse.",
            "confidence": "low",
            "source": RSS_FEEDS[feed_key]["name"],
            "headlines_count": 0,
            "as_of": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # Analyser avec Mistral (par batch de 10 pour éviter les limites)
    all_scores = []
    batch_size = 10

    for i in range(0, len(headlines), batch_size):
        batch = headlines[i : i + batch_size]
        results = await analyze_headlines_async(batch)

        for result in results:
            all_scores.append(result["score"])

    # Calculer le score moyen
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
    else:
        avg_score = 0.0

    # Déterminer le label et l'interprétation
    if avg_score >= 0.3:
        label = "optimiste"
        interpretation = "Les news financières sont majoritairement positives. Les investisseurs semblent confiants."
    elif avg_score <= -0.3:
        label = "pessimiste"
        interpretation = (
            "Les news financières sont majoritairement négatives. Prudence recommandée."
        )
    else:
        label = "neutre"
        interpretation = "Les news sont mitigées. Pas de tendance claire dans le sentiment."

    # Confiance basée sur le nombre de headlines et la cohérence
    score_std = (
        (sum((s - avg_score) ** 2 for s in all_scores) / len(all_scores)) ** 0.5
        if all_scores
        else 1.0
    )

    if len(all_scores) >= 20 and score_std < 0.3:
        confidence = "high"
    elif len(all_scores) >= 10 and score_std < 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "score": round(avg_score, 3),
        "label": label,
        "interpretation": interpretation,
        "confidence": confidence,
        "source": RSS_FEEDS[feed_key]["name"],
        "headlines_count": len(headlines),
        "analyzed_count": len(all_scores),
        "as_of": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
