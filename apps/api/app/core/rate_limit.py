import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class InMemoryRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_window: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_key = _client_key(request)
        now = time.monotonic()
        window = self._hits[client_key]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.requests_per_window:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again shortly."},
            )

        window.append(now)
        return await call_next(request)


class RedisRateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_url: str,
        requests_per_window: int = 120,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        import redis

        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._client = redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        self._client.ping()

    async def dispatch(self, request: Request, call_next):
        client_key = f"ratelimit:{_client_key(request)}"
        now = time.time()
        window_start = now - self.window_seconds

        try:
            pipe = self._client.pipeline()
            pipe.zremrangebyscore(client_key, 0, window_start)
            pipe.zcard(client_key)
            pipe.zadd(client_key, {str(now): now})
            pipe.expire(client_key, self.window_seconds)
            _, current_count, *_ = pipe.execute()
        except Exception:
            return await call_next(request)

        if current_count >= self.requests_per_window:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again shortly."},
            )

        return await call_next(request)


def build_rate_limiter_middleware(
    backend: str, redis_url: str, requests_per_window: int, window_seconds: int
):
    if backend == "redis":
        try:
            import redis as _redis

            probe = _redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
            probe.ping()
            return (
                RedisRateLimiter,
                {
                    "redis_url": redis_url,
                    "requests_per_window": requests_per_window,
                    "window_seconds": window_seconds,
                },
            )
        except Exception:
            pass

    return (
        InMemoryRateLimiter,
        {"requests_per_window": requests_per_window, "window_seconds": window_seconds},
    )
