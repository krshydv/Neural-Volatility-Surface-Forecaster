import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY, render_metrics
from app.core.rate_limit import build_rate_limiter_middleware

settings = get_settings()
configure_logging(settings.environment)

app = FastAPI(title=settings.app_name, version="0.1.0")

rate_limiter_cls, rate_limiter_kwargs = build_rate_limiter_middleware(
    backend=settings.rate_limit_backend,
    redis_url=settings.redis_url,
    requests_per_window=settings.rate_limit_requests_per_window,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(rate_limiter_cls, **rate_limiter_kwargs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    route = request.scope.get("route")
    path = route.path if route is not None else request.url.path
    REQUEST_COUNT.labels(method=request.method, path=path, status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, path=path).observe(duration)
    return response


@app.get("/metrics")
def metrics():
    body, content_type = render_metrics()
    return Response(content=body, media_type=content_type)


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {"service": settings.app_name, "status": "online"}
