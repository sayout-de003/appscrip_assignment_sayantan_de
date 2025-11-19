from browserbase import Browserbase
from playwright.async_api import async_playwright
from app.core.config import settings

async def scrape_sector_page(url: str) -> str:
    """
    Scrape a web page using Browserbase.
    Returns the HTML content of the page.
    """
    print(f"[Browserbase] Creating session for URL: {url}")
    
    bb = Browserbase(api_key=settings.BROWSERBASE_API_KEY)

    # Create browserbase session
    session = bb.sessions.create(project_id=settings.BROWSERBASE_PROJECT_ID)
    print(f"[Browserbase] ✓ Session created: {session.id if hasattr(session, 'id') else 'N/A'}")

    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        print(f"[Browserbase] Navigating to: {url}")
        await page.goto(url)
        content = await page.content()
        print(f"[Browserbase] ✓ Page loaded, content length: {len(content)} characters")

        await page.close()
        await browser.close()

    return content
