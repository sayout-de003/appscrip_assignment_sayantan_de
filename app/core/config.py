import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    RATE_LIMIT_PER_MIN: int = int(os.getenv("RATE_LIMIT_PER_MIN", 5))

    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    NEWSDATA_API_KEY: str = os.getenv("NEWSDATA_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    BROWSERBASE_API_KEY: str = os.getenv("BROWSERBASE_API_KEY")
    BROWSERBASE_PROJECT_ID: str = os.getenv("BROWSERBASE_PROJECT_ID")

settings = Settings()
