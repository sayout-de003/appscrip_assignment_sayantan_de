import time
from fastapi import HTTPException
from app.core.config import settings

_sessions = {}

def get_session(uid: str):
    if uid not in _sessions:
        _sessions[uid] = {"tokens": settings.RATE_LIMIT_PER_MIN, "last": time.time()}
    return _sessions[uid]


def consume_token(uid: str):
    session = get_session(uid)
    now = time.time()

    if now - session["last"] >= 60:
        session["tokens"] = settings.RATE_LIMIT_PER_MIN
        session["last"] = now

    if session["tokens"] <= 0:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    session["tokens"] -= 1
