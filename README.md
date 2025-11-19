# Trade Opportunities API

A FastAPI-based REST API that analyzes trade opportunities in different sectors in India by collecting news data from NewsData.io, searching for relevant market information via SerpAPI, and using Google Gemini AI to generate comprehensive market analysis reports.

## 📁 Directory Structure

```
trade-opportunities-api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── api/                         # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── analyze.py           # Main analysis endpoint
│   │
│   ├── core/                        # Core functionality
│   │   ├── auth.py                  # JWT authentication & token verification
│   │   ├── config.py                # Configuration & environment variables
│   │   └── rate_limiter.py          # Rate limiting implementation
│   │
│   ├── models/                      # Data models & schemas
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic models for request/response
│   │
│   └── services/                    # Business logic services
│       ├── ai_client.py             # Gemini AI integration
│       ├── browserbase_scraper.py   # Web scraping with Browserbase
│       ├── data_collector.py        # News data collection (NewsData.io)
│       └── report_generator.py      # Markdown report generation
│
├── appscrip_venv/                   # Virtual environment (gitignored)
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (create this)
├── .gitignore
└── README.md                        # This file
```

## 🔑 API Keys Setup

Create a `.env` file in the root directory with the following environment variables:

### Required Environment Variables

```env
# JWT Authentication
SECRET_KEY=your-secret-key-here  # Any random string for JWT signing

# Rate Limiting
RATE_LIMIT_PER_MIN=5  # Maximum requests per minute per user

# NewsData.io API (News Data Collection)
NEWSDATA_API_KEY=your-newsdata-api-key

# SerpAPI (Web Search)
SERPAPI_KEY=your-serpapi-api-key

# Google Gemini AI (AI Analysis)
GEMINI_API_KEY=your-gemini-api-key

# Browserbase (Optional - Web Scraping, not currently used)
BROWSERBASE_API_KEY=your-browserbase-api-key  # Optional
BROWSERBASE_PROJECT_ID=your-browserbase-project-id  # Optional

# Legacy (optional, not currently used)
NEWS_API_KEY=your-news-api-key  # Optional, for alternative news source
```

### How to Generate API Keys

#### 1. **NewsData.io API Key** (`NEWSDATA_API_KEY`)
- **Website**: https://newsdata.io/
- **Sign up**: Create a free account at https://newsdata.io/register
- **Get API Key**: 
  1. Log in to your dashboard
  2. Navigate to "API" section
  3. Copy your API key
  4. Free tier: 200 requests/day
- **Documentation**: https://newsdata.io/docs

#### 2. **SerpAPI Key** (`SERPAPI_KEY`)
- **Website**: https://serpapi.com/
- **Sign up**: Create a free account at https://serpapi.com/users/sign_up
- **Get API Key**:
  1. Log in to your SerpAPI dashboard
  2. Navigate to "Dashboard" → "API Key"
  3. Copy your API key (starts with `...`)
  4. Free tier: 100 searches/month
  5. Used for: Searching Google for relevant market news links
- **Documentation**: https://serpapi.com/search-api

#### 3. **Google Gemini API Key** (`GEMINI_API_KEY`)
- **Website**: https://makersuite.google.com/app/apikey
- **Sign up**: Use your Google account
- **Get API Key**:
  1. Visit https://aistudio.google.com/app/apikey
  2. Click "Create API Key"
  3. Select or create a Google Cloud project
  4. Copy the generated API key
  5. Free tier: 15 RPM (requests per minute)
- **Documentation**: https://ai.google.dev/docs

#### 4. **Browserbase API Key & Project ID** (`BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`) - Optional
- **Website**: https://www.browserbase.com/
- **Sign up**: Create an account at https://www.browserbase.com/sign-up
- **Get API Key & Project ID**:
  1. Log in to your dashboard
  2. Create a new project (if needed)
  3. Go to "Settings" → "API Keys"
  4. Copy your API key
  5. Copy your Project ID from the project settings
  6. Free tier: Limited requests/month
- **Documentation**: https://docs.browserbase.com/

#### 5. **SECRET_KEY** (JWT Authentication)
- **Generate**: Use any random string (recommended: 32+ characters)
- **Example**: 
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Or use any secure random string generator

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/sayout-de003/appscrip_assignment_sayantan_de.git
    cd appscrip_assignment_sayantan_de

   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv appscrip_venv
   source appscrip_venv/bin/activate  # On Windows: appscrip_venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```bash
   cp .env.example .env  # If you have an example file
   # Or create manually:
   touch .env
   ```
   
   Then add all the required environment variables as shown in the [API Keys Setup](#-api-keys-setup) section.

   **Note**: Only `SECRET_KEY`, `NEWSDATA_API_KEY`, `SERPAPI_KEY`, and `GEMINI_API_KEY` are required. Browserbase keys are optional.

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API Base URL: http://localhost:8000
   - Interactive API Docs (Swagger): http://localhost:8000/docs
   - Alternative API Docs (ReDoc): http://localhost:8000/redoc

## 🔄 Workflow

The API follows a 4-step workflow for analyzing trade opportunities in India:

### Step 1: News Data Collection
- **Service**: `app/services/data_collector.py`
- **API Used**: NewsData.io
- **Process**:
  1. Fetches news articles related to the specified sector in India
  2. Uses India country code (`in`) for localized news
  3. Extracts text content from news descriptions and titles
  4. Returns top 5 relevant news items
- **Output**: Array of news text items
- **Status**: Tracked in `intermediate_results.step_1_news_data`

### Step 2: Web Search with SerpAPI
- **Service**: `app/api/v1/analyze.py`
- **API Used**: SerpAPI (Google Search API)
- **Process**:
  1. Constructs search query: `"{sector} India market news"`
  2. Uses SerpAPI to search Google for relevant market news
  3. Retrieves top 5 search result links
  4. Filters out excluded domains (configurable)
  5. Returns list of relevant URLs for reference
- **Output**: Array of search result URLs
- **Status**: Tracked in `intermediate_results.step_2_search_links`
- **Note**: URLs are collected but not scraped (no content extraction)

### Step 3: AI Analysis
- **Service**: `app/services/ai_client.py`
- **API Used**: Google Gemini 2.5 Flash
- **Process**:
  1. Combines news data (Step 1) with search links (Step 2) as context
  2. Constructs a prompt focused on Indian market analysis:
     - Summary of the sector in India
     - Trade opportunities specific to Indian market
     - Risks and challenges in India
  3. Sends combined data to Gemini API
  4. Parses the AI response to extract:
     - Summary text
     - List of opportunities
     - List of risks
     - Full markdown formatted response
  5. Generates formatted markdown report
- **Output**: Analysis object with summary, opportunities, risks, and markdown
- **Status**: Tracked in `intermediate_results.step_3_ai_analysis`

### Step 4: Markdown Report Generation
- **Service**: `app/services/report_generator.py`
- **Process**:
  1. Formats the AI analysis into structured markdown
  2. Creates sections for Summary, Opportunities, and Risks
  3. Generates a complete markdown document
- **Output**: Formatted markdown string ready for saving as `.md` file

### Final Response
- Combines all results into a structured response
- Includes:
  - Sector name
  - Summary (truncated to 200 chars)
  - Full markdown report (can be saved as `.md` file)
  - Sources used (newsdata.io, serpapi, gemini)
  - Complete intermediate results from all steps

## 📡 API Endpoints

### 1. Get Demo Token
```http
GET /demo-token
```
Generates a JWT token for testing purposes.

**Response**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usage": "Add this token to the Authorization header as: Bearer <token>",
  "example": "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Analyze Sector
```http
GET /analyze/{sector}
Authorization: Bearer <your-token>
```

**Parameters**:
- `sector` (path parameter): The sector to analyze (e.g., "technology", "healthcare", "finance")
  - Must match pattern: `^[a-zA-Z\s-]{2,50}$`

**Headers**:
- `Authorization: Bearer <token>` (required)

**Response**:
```json
{
  "sector": "technology",
  "summary": "The technology sector shows strong growth potential...",
  "markdown": "# Technology Sector Market Report\n\n## Summary\n...",
  "sources": ["newsdata.io", "serpapi", "gemini"],
  "intermediate_results": {
    "step_1_news_data": {
      "items_count": 5,
      "preview": [...]
    },
    "step_2_search_links": {
      "links": ["https://...", "https://..."],
      "total_links": 5
    },
    "step_3_ai_analysis": {
      "summary_length": 500,
      "opportunities_count": 2,
      "risks_count": 2
    }
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: API errors (check `intermediate_results` for details)

## 🔒 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Get a token**: Call `/demo-token` endpoint
2. **Use the token**: Include in the `Authorization` header as:
   ```
   Authorization: Bearer <your-token>
   ```
3. **Token expiration**: Tokens expire after 1 hour

## ⚡ Rate Limiting

- Default: 5 requests per minute per user
- Configured via `RATE_LIMIT_PER_MIN` in `.env`
- Tracked per user (JWT `sub` claim)
- Returns `429 Too Many Requests` when limit exceeded

## 🧪 Testing

### Using Swagger UI
1. Visit http://localhost:8000/docs
2. Click "Authorize" button
3. Get a token from `/demo-token` endpoint
4. Enter token as: `Bearer <your-token>`
5. Test the `/analyze/{sector}` endpoint

### Using cURL
```bash
# Get a token
TOKEN=$(curl -s http://localhost:8000/demo-token | jq -r '.token')

# Analyze a sector
curl -X GET "http://localhost:8000/analyze/technology" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python
```python
import requests

# Get token
response = requests.get("http://localhost:8000/demo-token")
token = response.json()["token"]

# Analyze sector
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/analyze/technology",
    headers=headers
)
print(response.json())
```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **API key errors**
   - Verify all API keys are correctly set in `.env`
   - Check for extra spaces or quotes around keys
   - Ensure `.env` file is in the root directory

3. **SerpAPI errors**
   - Verify `SERPAPI_KEY` is correct
   - Check SerpAPI account status and credits (free tier: 100 searches/month)
   - Ensure internet connection is available
   - If rate limited, wait before making more requests

4. **Browserbase connection errors** (if using)
   - Verify `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID` are correct
   - Check Browserbase account status and credits
   - Ensure Playwright browsers are installed: `playwright install chromium`
   - Note: Browserbase is optional and not currently used in the workflow

5. **Gemini API errors**
   - Check API key is valid and not expired
   - Verify quota limits (free tier: 15 RPM)
   - Ensure model name is correct (currently using `gemini-2.5-flash`)

6. **NewsData.io errors**
   - Verify API key is correct
   - Check daily request limit (free tier: 200/day)
   - Ensure internet connection is available

## 📝 Environment Variables Reference

| Variable                  | Description            | Required  | Example                        |
|---------------------------|------------------------|-----------|--------------------------------|
| `SECRET_KEY`              | JWT signing secret     | Yes       | `your-secret-key-32-chars`    |
| `RATE_LIMIT_PER_MIN`      | Rate limit per user    | No        | `5` (default)                 |
| `NEWSDATA_API_KEY`        | NewsData.io API key    | Yes       | `pub_12345...`                |
| `SERPAPI_KEY`             | SerpAPI key            | Yes       | `...`                         |
| `GEMINI_API_KEY`          | Google Gemini API key  | Yes       | `AIza...`                     |
| `BROWSERBASE_API_KEY`     | Browserbase API key    | No        | `bb_...` (optional)           |
| `BROWSERBASE_PROJECT_ID`  | Browserbase project ID | No        | `proj_...` (optional)         |
| `NEWS_API_KEY`            | Legacy news API key    | No        | (optional)                    |

## 📚 Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type annotations
- **PyJWT**: JWT token encoding/decoding
- **httpx**: Async HTTP client for API calls
- **python-dotenv**: Environment variable management
- **Browserbase**: Browser automation (optional, not currently used)
- **Playwright**: Browser automation library (optional, for Browserbase)
- **BeautifulSoup4**: HTML parsing (optional, for web scraping)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


#

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the [Troubleshooting](#-troubleshooting) section
- Review API documentation at `/docs` endpoint


contact : desayantan1947@gmail.com
---

**Note**: This API requires active internet connection and valid API keys for all services to function properly.

