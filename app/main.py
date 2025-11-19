import logging
from fastapi import FastAPI, Depends
from fastapi.responses import Response
from app.api.v1.analyze import router
from app.core.auth import create_token, verify_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="India Market Analysis API",
    version="0.1.0",
    description="API for analyzing trade opportunities in different sectors in India",
)

# Include router with Bearer token authentication
app.include_router(router, tags=["analysis"])

@app.get("/demo-token", tags=["auth"])
def get_demo_token():
    """
    Generate a demo Bearer token for testing.
    Use this token in the Authorization header: Bearer <token>
    """
    token = create_token("guest")
    logger.info("Demo token generated")
    return {
        "token": token,
        "usage": "Add this token to the Authorization header as: Bearer <token>",
        "example": f"Authorization: Bearer {token}"
    }


@app.get("/analyze/{sector}/download", tags=["analysis"])
async def download_markdown(sector: str, user=Depends(verify_token)):
    """
    Download the analysis report as a markdown (.md) file.
    Same as /analyze/{sector} but returns the markdown file for download.
    """
    from app.core.rate_limiter import consume_token
    from app.api.v1.analyze import analyze
    
    # Reuse the analyze endpoint to get the report
    consume_token(user)
    result = await analyze(sector, user)
    markdown_content = result["markdown"]
    
    # Return as downloadable file
    filename = f"{sector}_market_analysis.md"
    logger.info(f"Markdown file downloaded: {filename}")
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
