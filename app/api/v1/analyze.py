import os
import httpx
from fastapi import APIRouter, Depends
from app.models.schemas import AnalyzeResponse, Sector
from app.core.auth import verify_token
from app.core.rate_limiter import consume_token
from app.services.data_collector import fetch_news
from app.services.ai_client import analyze_text
from app.services.report_generator import generate_markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
NUM_SEARCH_RESULTS = 5
EXCLUDE_DOMAINS = []  # Can be used to filter specific domains if needed


router = APIRouter()

# ======= SerpAPI search =======
async def serpapi_search(query: str, num_results: int = NUM_SEARCH_RESULTS) -> list[str]:
    """Use SerpAPI to search Google and return top URLs."""
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": SERPAPI_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            links = []

            # SerpAPI returns organic results in 'organic_results'
            for item in data.get("organic_results", []):
                link = item.get("link")
                if link and not any(domain in link for domain in EXCLUDE_DOMAINS):
                    links.append(link)

            return links[:num_results]
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []

# ======= API endpoint =======
@router.get("/analyze/{sector}", response_model=AnalyzeResponse)
async def analyze(sector: Sector, user=Depends(verify_token)):
    # Rate-limit check
    consume_token(user)

    # Step 1: Fetch news from NewsData.io API
    news_data = await fetch_news(sector)

    # Step 2: SerpAPI search for generic market news
    query = f"{sector} India market news"
    search_links = await serpapi_search(query, num_results=NUM_SEARCH_RESULTS)

    # Step 3: Combine news text + optional URLs (we're not scraping them)
    combined_texts = news_data.copy()
    combined_texts.extend(search_links[:3])  # optional: include snippets from links

    # Step 4: AI analysis using Gemini API
    analysis = await analyze_text(sector, combined_texts)

    # Step 5: Generate markdown report
    markdown = generate_markdown(sector, analysis)

    # Intermediate results for debugging
    intermediate_results = {
        "step_1_news_data": {"items_count": len(news_data), "preview": news_data[:2]},
        "step_2_search_links": {
            "links": search_links,
            "total_links": len(search_links)
        },
        "step_3_ai_analysis": {
            "summary_length": len(analysis.get("summary", "")),
            "opportunities_count": len(analysis.get("opportunities", [])),
            "risks_count": len(analysis.get("risks", [])),
        }
    }

    return {
        "sector": sector,
        "summary": analysis["summary"][:200] + "...",
        "markdown": markdown,
        "sources": ["newsdata.io", "serpapi", "gemini"],
        "intermediate_results": intermediate_results
    }
