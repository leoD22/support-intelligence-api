from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def verify_api_key(api_key: str | None = Depends(api_key_header)):

    if not API_ACCESS_KEY:
        raise HTTPException(
            status_code=503, detail="API authentication is not configured"
        )

    if not api_key:
        raise HTTPException(status_code=403, detail="Missing API key")

    if not secrets.compare_digest(api_key, API_ACCESS_KEY):
        raise HTTPException(status_code=403, detail="Invalid API key")
