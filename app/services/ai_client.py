import re
import logging
import httpx
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)

async def analyze_text(sector: str, texts: list):
    prompt = f"""
    Analyze the {sector} sector in India.
    Focus on Indian market trends, regulations, and opportunities.
    Provide:
    - Summary of the current state of the {sector} sector in India
    - Trade opportunities specific to the Indian market
    - Risks and challenges facing the {sector} sector in India
    
    Use the following market data and news:
    {texts}
    
    Format your response in markdown with sections: ## Summary, ### Opportunities, ### Risks
    """

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
    )

    logger.info(f"Analyzing {sector} sector (India) with {len(texts)} text items")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{url}?key={settings.GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=60
            )
    except Exception as e:
        logger.error(f"Gemini API unreachable: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini API unreachable: {str(e)}")

    if res.status_code != 200:
        try:
            msg = res.json().get("error", {}).get("message", res.text)
        except Exception:
            msg = res.text
        logger.error(f"Gemini API HTTP {res.status_code}: {msg}")
        raise HTTPException(status_code=500, detail=f"Gemini API error: {msg}")

    data = res.json()

    # Check for expected Gemini response keys
    if "candidates" not in data or not data["candidates"]:
        logger.error("Gemini API returned no candidates in response")
        raise HTTPException(status_code=500, detail="Gemini API returned no candidates")

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    logger.info(f"Analysis complete for {sector} sector, response length: {len(text)} characters")

    # --- Parse markdown for Summary, Opportunities, Risks ---
    def extract_section(pattern: str, text: str):
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # Split bullet points if any
            items = re.findall(r"\*{1,2}\s*(.+)", content)
            return items if items else [content]
        return []

    # Summary: grab first paragraph under "## Summary"
    summary_match = re.search(r"## Summary\s*(.+?)(\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    summary = summary_match.group(1).strip() if summary_match else text[:300]

    opportunities = extract_section(r"###.*Opportunities\s*(.+?)(\n###|\Z)", text)
    risks = extract_section(r"###.*Risks\s*(.+?)(\n###|\Z)", text)

    return {
        "summary": summary,
        "opportunities": opportunities,
        "risks": risks,
        "markdown": text,
        "sources": ["gemini"]
    }
