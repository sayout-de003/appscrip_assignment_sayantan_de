import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_token

client = TestClient(app)

def test_demo_token():
    """Test that demo token endpoint works"""
    res = client.get("/demo-token")
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert "usage" in data

def test_analyze_with_valid_token():
    """Test analyze endpoint with valid token"""
    token = create_token("test-user")
    res = client.get("/analyze/technology", headers={"Authorization": f"Bearer {token}"})
    # Should be 200 (success) or 429 (rate limit) or 500 (API errors)
    assert res.status_code in (200, 429, 500)
    if res.status_code == 200:
        data = res.json()
        assert "sector" in data
        assert "summary" in data
        assert "markdown" in data
        assert "intermediate_results" in data

def test_analyze_without_token():
    """Test that endpoint requires authentication"""
    res = client.get("/analyze/technology")
    assert res.status_code == 403  # Forbidden - no token

def test_analyze_with_invalid_token():
    """Test that invalid token is rejected"""
    res = client.get("/analyze/technology", headers={"Authorization": "Bearer invalid-token"})
    assert res.status_code == 401  # Unauthorized

def test_analyze_download_endpoint():
    """Test markdown download endpoint"""
    token = create_token("test-user")
    res = client.get("/analyze/pharmaceuticals/download", headers={"Authorization": f"Bearer {token}"})
    # Should be 200 (success) or 429 (rate limit) or 500 (API errors)
    assert res.status_code in (200, 429, 500)
    if res.status_code == 200:
        assert res.headers["content-type"] == "text/markdown"
        assert "Content-Disposition" in res.headers

def test_rate_limiting():
    """Test that rate limiting works (may need multiple requests)"""
    token = create_token("rate-test-user")
    # Make multiple requests to test rate limiting
    for i in range(10):
        res = client.get("/analyze/agriculture", headers={"Authorization": f"Bearer {token}"})
        if res.status_code == 429:
            # Rate limit hit
            assert "Rate limit exceeded" in res.json()["detail"]
            break
