from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

def create_token(sub: str):
    payload = {
        "sub": sub,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_token(creds: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify Bearer token from Authorization header.
    Expects: Authorization: Bearer <token>
    """
    try:
        data = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        return data["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")
