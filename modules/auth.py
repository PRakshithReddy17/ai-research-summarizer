"""
Simple API-key authentication middleware.

When the environment variable API_KEY is set, every request (except the health
check) must include an ``X-API-Key`` header matching that value.

If API_KEY is not set, authentication is disabled — useful for local
development.
"""

import os
from typing import Optional

from fastapi import HTTPException, Request


_api_key: Optional[str] = None


def init_auth() -> None:
    """Read the API key from the environment.  Call once at startup."""
    global _api_key
    _api_key = os.getenv("API_KEY") or None

    if _api_key:
        print("[AUTH] API_KEY is configured — authentication is enabled.")
    else:
        print("[AUTH] API_KEY is not set — authentication is disabled (open access).")


def is_auth_enabled() -> bool:
    return _api_key is not None


async def verify_api_key(request: Request) -> None:
    """
    Dependency / middleware helper that raises 401 if the key is wrong.

    Skip enforcement when:
    - API_KEY is not set (dev mode)
    - The path is /health or /docs or /openapi.json
    """
    if not _api_key:
        return

    skip_paths = {"/health", "/docs", "/openapi.json", "/redoc"}
    if request.url.path in skip_paths:
        return

    provided = request.headers.get("X-API-Key")

    if provided != _api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
