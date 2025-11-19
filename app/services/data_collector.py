import httpx
from fastapi import HTTPException
from app.core.config import settings

API_KEY = settings.NEWSDATA_API_KEY

async def fetch_news(sector: str):
    url = f"https://newsdata.io/api/1/news"

    params = {
        "apikey": API_KEY,
        "q": sector,
        "language": "en",
        "country": "us",
    }

    print(f"[News API] Fetching news for sector: {sector}")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
    except Exception as e:
        print(f"[News API] ✗ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"News API unreachable: {str(e)}")

    if resp.status_code != 200:
        print(f"[News API] ✗ HTTP {resp.status_code} error")
        raise HTTPException(status_code=500, detail=f"News API error {resp.status_code}")

    data = resp.json()

    # NewsData.io returns results under 'results'
    if "results" not in data or not data["results"]:
        print(f"[News API] ✗ No results found")
        raise HTTPException(status_code=500, detail="No news found for this sector")

    # Extract text materials
    texts = []
    for item in data["results"]:
        if "description" in item and item["description"]:
            texts.append(item["description"])
        elif "title" in item and item["title"]:
            texts.append(item["title"])

    if not texts:
        print(f"[News API] ✗ No text content extracted")
        raise HTTPException(status_code=500, detail="News API returned empty results")

    print(f"[News API] ✓ Retrieved {len(texts)} news items")
    return texts[:5]
