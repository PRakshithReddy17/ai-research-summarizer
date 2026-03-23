"""
Lightweight in-memory rate limiter for FastAPI.

Uses a sliding-window approach per client IP.  Configurable via environment
variables:

    RATE_LIMIT_RPM  – max requests per minute per IP (default 30)
    RATE_LIMIT_ENABLED – set to "false" to disable (default "true")
"""

import os
import time
from collections import defaultdict
from typing import List

from fastapi import HTTPException, Request


_enabled: bool = True
_max_rpm: int = 30
_window: int = 60  # seconds

# { ip_address: [timestamp, timestamp, ...] }
_request_log: dict[str, List[float]] = defaultdict(list)


def init_rate_limiter() -> None:
    """Read configuration from the environment.  Call once at startup."""
    global _enabled, _max_rpm

    _enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() != "false"
    _max_rpm = int(os.getenv("RATE_LIMIT_RPM", "30"))

    if _enabled:
        print(f"[RATE-LIMIT] Enabled — {_max_rpm} requests/min per IP.")
    else:
        print("[RATE-LIMIT] Disabled.")


def _client_ip(request: Request) -> str:
    """Best-effort client IP extraction (respects X-Forwarded-For)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def check_rate_limit(request: Request) -> None:
    """
    Middleware-style check.  Call before processing expensive endpoints.

    Raises 429 Too Many Requests when the limit is exceeded.
    """
    if not _enabled:
        return

    # Skip rate limiting for health checks
    if request.url.path == "/health":
        return

    ip = _client_ip(request)
    now = time.time()
    cutoff = now - _window

    # Prune old entries
    log = _request_log[ip]
    _request_log[ip] = [t for t in log if t > cutoff]

    if len(_request_log[ip]) >= _max_rpm:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {_max_rpm} requests per minute.",
        )

    _request_log[ip].append(now)
