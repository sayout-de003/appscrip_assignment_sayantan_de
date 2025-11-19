# Trade Opportunities API

A FastAPI-based REST API that analyzes trade opportunities in different sectors by collecting news data, scraping web content, and using AI to generate comprehensive market analysis reports.

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

# Google Gemini AI (AI Analysis)
GEMINI_API_KEY=your-gemini-api-key

# Browserbase (Web Scraping)
BROWSERBASE_API_KEY=your-browserbase-api-key
BROWSERBASE_PROJECT_ID=your-browserbase-project-id

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

#### 2. **Google Gemini API Key** (`GEMINI_API_KEY`)
- **Website**: https://makersuite.google.com/app/apikey
- **Sign up**: Use your Google account
- **Get API Key**:
  1. Visit https://aistudio.google.com/app/apikey
  2. Click "Create API Key"
  3. Select or create a Google Cloud project
  4. Copy the generated API key
  5. Free tier: 15 RPM (requests per minute)
- **Documentation**: https://ai.google.dev/docs

#### 3. **Browserbase API Key & Project ID** (`BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`)
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

#### 4. **SECRET_KEY** (JWT Authentication)
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
   git clone <repository-url>
   cd trade-opportunities-api
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

4. **Install Playwright browsers** (required for Browserbase)
   ```bash
   playwright install chromium
   ```

5. **Create `.env` file**
   ```bash
   cp .env.example .env  # If you have an example file
   # Or create manually:
   touch .env
   ```
   
   Then add all the required environment variables as shown in the [API Keys Setup](#-api-keys-setup) section.

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API Base URL: http://localhost:8000
   - Interactive API Docs (Swagger): http://localhost:8000/docs
   - Alternative API Docs (ReDoc): http://localhost:8000/redoc

## 🔄 Workflow

The API follows a 4-step workflow for analyzing trade opportunities:

### Step 1: News Data Collection
- **Service**: `app/services/data_collector.py`
- **API Used**: NewsData.io
- **Process**:
  1. Fetches news articles related to the specified sector
  2. Extracts text content from news descriptions and titles
  3. Returns top 5 relevant news items
- **Output**: Array of news text items
- **Status**: Tracked in `intermediate_results.step_1_news_data`

### Step 2: Browserbase Session Creation
- **Service**: `app/services/browserbase_scraper.py`
- **API Used**: Browserbase
- **Process**:
  1. Creates a Browserbase session for web scraping
  2. Connects to the browser via CDP (Chrome DevTools Protocol)
  3. Prepares for content extraction
- **Output**: Browserbase session connection URL
- **Status**: Tracked in `intermediate_results.step_2_browserbase_session`

### Step 3: Web Scraping
- **Service**: `app/services/browserbase_scraper.py`
- **Process**:
  1. Navigates to sector-specific URL (e.g., Reuters markets page)
  2. Loads and waits for page content
  3. Extracts HTML content from the page
  4. Parses HTML to extract relevant text:
     - Removes script and style tags
     - Extracts paragraph and heading text
     - Filters out short text snippets (< 50 characters)
  5. Returns top 10 paragraphs and 5 headings
- **Output**: Array of extracted text items from web scraping
- **Status**: Tracked in `intermediate_results.step_3_scraped_content`

### Step 4: AI Analysis
- **Service**: `app/services/ai_client.py`
- **API Used**: Google Gemini 2.5 Flash
- **Process**:
  1. Combines news data (Step 1) with scraped content (Step 3)
  2. Constructs a prompt asking for:
     - Summary of the sector
     - Trade opportunities
     - Risks
  3. Sends combined data to Gemini API
  4. Parses the AI response to extract:
     - Summary text
     - List of opportunities
     - List of risks
     - Full markdown formatted response
  5. Generates formatted markdown report
- **Output**: Analysis object with summary, opportunities, risks, and markdown
- **Status**: Tracked in `intermediate_results.step_4_ai_analysis`

### Final Response
- Combines all results into a structured response
- Includes:
  - Sector name
  - Summary (truncated to 200 chars)
  - Full markdown report
  - Sources used (newsdata.io, browserbase, gemini)
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
  "sources": ["newsdata.io", "browserbase", "gemini"],
  "intermediate_results": {
    "step_1_news_data": {
      "step": "News Data Collection",
      "status": "success",
      "items_count": 5,
      "preview": [...],
      "full_data": [...]
    },
    "step_2_browserbase_session": {
      "step": "Browserbase Session Creation",
      "status": "success",
      "session_created": true,
      "url_scraped": "https://www.reuters.com/...",
      "sector": "technology"
    },
    "step_3_scraped_content": {
      "step": "Web Scraping",
      "status": "success",
      "content_length": 12345,
      "extracted_texts_count": 8,
      "content_preview": "...",
      "extracted_texts_preview": [...]
    },
    "step_4_ai_analysis": {
      "step": "AI Analysis",
      "status": "success",
      "model": "gemini-2.5-flash",
      "summary_length": 500,
      "opportunities_count": 2,
      "risks_count": 2,
      "opportunities": [...],
      "risks": [...],
      "full_markdown": "..."
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

3. **Browserbase connection errors**
   - Verify `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID` are correct
   - Check Browserbase account status and credits
   - Ensure Playwright browsers are installed: `playwright install chromium`

4. **Gemini API errors**
   - Check API key is valid and not expired
   - Verify quota limits (free tier: 15 RPM)
   - Ensure model name is correct (currently using `gemini-2.5-flash`)

5. **NewsData.io errors**
   - Verify API key is correct
   - Check daily request limit (free tier: 200/day)
   - Ensure internet connection is available

## 📝 Environment Variables Reference

| Variable                  | Description            | Required  Example                        |
|---------------            |---------------         |----------|---------                      |
| `SECRET_KEY`              | JWT signing secret     | Yes      | `your-secret-key-32-chars`    |
| `RATE_LIMIT_PER_MIN`      | Rate limit per user    | No       | `5` (default)                 |
| `NEWSDATA_API_KEY`        | NewsData.io API key    | Yes      | `pub_12345...`                |
| `GEMINI_API_KEY`          | Google Gemini API key  | Yes      | `AIza...`                     |
| `BROWSERBASE_API_KEY`     | Browserbase API key    | Yes      | `bb_...`                      |
| `BROWSERBASE_PROJECT_ID`  | Browserbase project ID | Yes      | `proj_...`                    |
| `NEWS_API_KEY`            | Legacy news API key    | No       | (optional)                    |

## 📚 Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type annotations
- **PyJWT**: JWT token encoding/decoding
- **httpx**: Async HTTP client for API calls
- **Browserbase**: Browser automation and web scraping
- **Playwright**: Browser automation library
- **BeautifulSoup4**: HTML parsing (for web scraping)
- **python-dotenv**: Environment variable management

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the [Troubleshooting](#-troubleshooting) section
- Review API documentation at `/docs` endpoint

---

**Note**: This API requires active internet connection and valid API keys for all services to function properly.

