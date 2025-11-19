import logging
import httpx
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)

API_KEY = settings.NEWSDATA_API_KEY

async def fetch_news(sector: str):
    url = f"https://newsdata.io/api/1/news"

    params = {
        "apikey": API_KEY,
        "q": f"{sector} India",  # Explicitly search for sector in India
        "language": "en",
        "country": "in",  # India country code
    }

    logger.info(f"Fetching news for sector: {sector} (India)")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
    except Exception as e:
        logger.error(f"News API unreachable: {str(e)}")
        raise HTTPException(status_code=500, detail=f"News API unreachable: {str(e)}")

    if resp.status_code != 200:
        logger.error(f"News API HTTP {resp.status_code} error")
        raise HTTPException(status_code=500, detail=f"News API error {resp.status_code}")

    data = resp.json()

    # NewsData.io returns results under 'results'
    if "results" not in data or not data["results"]:
        logger.warning(f"No news results found for sector: {sector}")
        raise HTTPException(status_code=500, detail="No news found for this sector")

    # Extract text materials
    texts = []
    for item in data["results"]:
        if "description" in item and item["description"]:
            texts.append(item["description"])
        elif "title" in item and item["title"]:
            texts.append(item["title"])

    if not texts:
        logger.warning(f"No text content extracted for sector: {sector}")
        raise HTTPException(status_code=500, detail="News API returned empty results")

    logger.info(f"Retrieved {len(texts)} news items for sector: {sector}")
    return texts[:5]
