from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.rate_limit import InMemoryRateLimiter, build_rate_limiter_middleware


def _build_app(limit: int = 3, window: int = 60) -> FastAPI:
    app = FastAPI()
    app.add_middleware(InMemoryRateLimiter, requests_per_window=limit, window_seconds=window)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    return app


def test_allows_requests_under_limit():
    client = TestClient(_build_app(limit=3))
    for _ in range(3):
        response = client.get("/ping")
        assert response.status_code == 200


def test_blocks_requests_over_limit():
    client = TestClient(_build_app(limit=2))
    client.get("/ping")
    client.get("/ping")
    response = client.get("/ping")
    assert response.status_code == 429


def test_different_clients_have_independent_limits():
    client = TestClient(_build_app(limit=1))
    first = client.get("/ping", headers={"x-forwarded-for": "1.1.1.1"})
    second = client.get("/ping", headers={"x-forwarded-for": "2.2.2.2"})
    assert first.status_code == 200
    assert second.status_code == 200


def test_factory_falls_back_to_memory_when_redis_unreachable():
    cls, kwargs = build_rate_limiter_middleware(
        backend="redis",
        redis_url="redis://localhost:1/0",
        requests_per_window=5,
        window_seconds=60,
    )
    assert cls is InMemoryRateLimiter
    assert kwargs == {"requests_per_window": 5, "window_seconds": 60}


def test_factory_uses_memory_backend_by_default():
    cls, kwargs = build_rate_limiter_middleware(
        backend="memory",
        redis_url="redis://localhost:6379/0",
        requests_per_window=10,
        window_seconds=30,
    )
    assert cls is InMemoryRateLimiter
    assert kwargs == {"requests_per_window": 10, "window_seconds": 30}
