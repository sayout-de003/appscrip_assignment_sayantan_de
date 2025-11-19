import re
from fastapi import APIRouter, Depends
from app.models.schemas import AnalyzeResponse, Sector
from app.core.auth import verify_token
from app.core.rate_limiter import consume_token
from app.services.data_collector import fetch_news
from app.services.browserbase_scraper import scrape_sector_page
from app.services.ai_client import analyze_text
from app.services.report_generator import generate_markdown

router = APIRouter()

@router.get("/analyze/{sector}", response_model=AnalyzeResponse)
async def analyze(sector: Sector, user=Depends(verify_token)):
    # Verify Bearer token and rate limit
    consume_token(user)

    # Store intermediate results for each step
    intermediate_results = {
        "step_1_news_data": None,
        "step_2_browserbase_session": None,
        "step_3_scraped_content": None,
        "step_4_ai_analysis": None
    }

    # Step 1: Fetch news data for the sector
    print(f"\n{'='*60}")
    print(f"[STEP 1] Fetching news data for sector: {sector}")
    print(f"{'='*60}")
    news_data = await fetch_news(sector)
    intermediate_results["step_1_news_data"] = {
        "step": "News Data Collection",
        "status": "success",
        "sector": sector,
        "items_count": len(news_data),
        "preview": news_data[:2] if news_data else [],  # First 2 items as preview
        "full_data": news_data,
        "source": "newsdata.io"
    }
    print(f"[STEP 1] ✓ COMPLETE - Retrieved {len(news_data)} news items\n")

    # Step 2 & 3: Browserbase web scraping
    print(f"{'='*60}")
    print(f"[STEP 2-3] Browserbase Session & Web Scraping")
    print(f"{'='*60}")
    scraped_content = None
    scraped_texts = []
    
    try:
        # Scrape sector-specific information from a relevant news/finance website
        # Using a generic URL that can be customized per sector
        sector_url = f"https://www.reuters.com/markets/global-markets/{sector.lower().replace(' ', '-')}"
        
        print(f"[STEP 2] Creating Browserbase session for: {sector_url}")
        scraped_content = await scrape_sector_page(sector_url)
        
        intermediate_results["step_2_browserbase_session"] = {
            "step": "Browserbase Session Creation",
            "status": "success",
            "session_created": True,
            "url_scraped": sector_url,
            "sector": sector
        }
        
        # Extract text content from scraped HTML (basic extraction)
        # You might want to use BeautifulSoup for better extraction
        if scraped_content:
            # Simple text extraction - get text between common HTML tags
            # Remove script and style elements
            scraped_content_clean = re.sub(r'<script[^>]*>.*?</script>', '', scraped_content, flags=re.DOTALL | re.IGNORECASE)
            scraped_content_clean = re.sub(r'<style[^>]*>.*?</style>', '', scraped_content_clean, flags=re.DOTALL | re.IGNORECASE)
            # Extract text from paragraph and heading tags
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', scraped_content_clean, re.DOTALL | re.IGNORECASE)
            headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', scraped_content_clean, re.DOTALL | re.IGNORECASE)
            
            # Clean HTML tags and get text
            def clean_html(text):
                return re.sub(r'<[^>]+>', '', text).strip()
            
            scraped_texts = [clean_html(p) for p in paragraphs[:10] if clean_html(p)]  # Get first 10 paragraphs
            scraped_texts.extend([clean_html(h) for h in headings[:5] if clean_html(h)])  # Get first 5 headings
            
            # Filter out very short texts
            scraped_texts = [t for t in scraped_texts if len(t) > 50]
        
        intermediate_results["step_3_scraped_content"] = {
            "step": "Web Scraping",
            "status": "success",
            "content_length": len(scraped_content),
            "extracted_texts_count": len(scraped_texts),
            "content_preview": scraped_content[:500] if scraped_content else "",
            "extracted_texts_preview": scraped_texts[:3] if scraped_texts else [],
            "url_scraped": sector_url
        }
        print(f"[STEP 2-3] ✓ COMPLETE - Scraped {len(scraped_content)} characters, extracted {len(scraped_texts)} text items\n")
        
    except Exception as e:
        intermediate_results["step_2_browserbase_session"] = {
            "step": "Browserbase Session Creation",
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
        intermediate_results["step_3_scraped_content"] = {
            "step": "Web Scraping",
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(f"[STEP 2-3] ✗ ERROR - Browserbase scraping error: {str(e)}\n")
        # Continue with analysis even if scraping fails

    # Step 4: Call AI client to analyze (combine news data and scraped content)
    print(f"{'='*60}")
    print(f"[STEP 4] AI Analysis with Gemini")
    print(f"{'='*60}")
    
    # Combine news data with scraped content for richer analysis
    combined_data = news_data.copy()
    if scraped_texts:
        combined_data.extend(scraped_texts[:3])  # Add top 3 scraped texts
        print(f"[STEP 4] Combining {len(news_data)} news items with {min(3, len(scraped_texts))} scraped texts")
    
    analysis = await analyze_text(sector, combined_data)
    intermediate_results["step_4_ai_analysis"] = {
        "step": "AI Analysis",
        "status": "success",
        "sector": sector,
        "model": "gemini-2.5-flash",
        "summary_length": len(analysis.get("summary", "")),
        "opportunities_count": len(analysis.get("opportunities", [])),
        "risks_count": len(analysis.get("risks", [])),
        "summary_preview": analysis.get("summary", "")[:200],
        "opportunities": analysis.get("opportunities", []),
        "risks": analysis.get("risks", []),
        "full_markdown": analysis.get("markdown", ""),
        "source": "gemini"
    }
    print(f"[STEP 4] ✓ COMPLETE - Analysis done:")
    print(f"  - Summary: {len(analysis.get('summary', ''))} chars")
    print(f"  - Opportunities: {len(analysis.get('opportunities', []))}")
    print(f"  - Risks: {len(analysis.get('risks', []))}")
    print(f"{'='*60}\n")

    # Generate markdown report
    markdown = generate_markdown(sector, analysis)

    return {
        "sector": sector,
        "summary": analysis["summary"][:200] + "...",
        "markdown": markdown,
        "sources": ["newsdata.io", "browserbase", "gemini"] if scraped_content else ["newsdata.io", "gemini"],
        "intermediate_results": intermediate_results
    }
