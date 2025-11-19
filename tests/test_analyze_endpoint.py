from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_token

client = TestClient(app)

def test_analyze():
    token = create_token("test-user")
    res = client.get("/analyze/technology", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code in (200, 429)
