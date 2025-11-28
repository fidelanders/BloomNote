from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

def _rate_limit_exceeded_handler(request, exc):
    """Custom rate limit exceeded handler"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )

# Attach the handler to the exception class
RateLimitExceeded._rate_limit_exceeded_handler = _rate_limit_exceeded_handler