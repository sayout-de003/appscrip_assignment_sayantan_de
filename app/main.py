from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api.v1.analyze import router
from app.core.auth import create_token

app = FastAPI(
    title="Market Analysis API",
    version="0.1.0",
    description="API for analyzing trade opportunities in different sectors",
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
    return {
        "token": token,
        "usage": "Add this token to the Authorization header as: Bearer <token>",
        "example": f"Authorization: Bearer {token}"
    }
