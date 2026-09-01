import pytest

from app.core.config import get_settings
from app.services import oauth_service as oauth_service_module
from app.services.oauth_service import GoogleOAuthService, OAuthConfigurationError


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture()
def configured_settings(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "google_oauth_client_id", "test-client-id")
    monkeypatch.setattr(settings, "google_oauth_client_secret", "test-client-secret")
    return settings


def test_build_authorization_url_requires_configuration():
    from app.core.config import Settings

    unconfigured = Settings(google_oauth_client_id=None, google_oauth_client_secret=None)
    service = GoogleOAuthService(unconfigured)
    with pytest.raises(OAuthConfigurationError):
        service.build_authorization_url()


def test_build_authorization_url_includes_client_id(configured_settings):
    service = GoogleOAuthService(configured_settings)
    url, state = service.build_authorization_url()
    assert "client_id=test-client-id" in url
    assert state in url


def test_google_login_endpoint_returns_url(client, configured_settings):
    response = client.get("/api/v1/auth/oauth/google/login")
    assert response.status_code == 200
    body = response.json()
    assert "accounts.google.com" in body["authorization_url"]
    assert body["state"]


def test_google_login_endpoint_returns_503_when_unconfigured(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "google_oauth_client_id", None)
    monkeypatch.setattr(settings, "google_oauth_client_secret", None)
    response = client.get("/api/v1/auth/oauth/google/login")
    assert response.status_code == 503


def test_google_callback_creates_new_user(client, configured_settings, monkeypatch):
    def fake_post(url, data=None, timeout=None):
        return _FakeResponse(200, {"access_token": "fake-access-token"})

    def fake_get(url, headers=None, timeout=None):
        return _FakeResponse(
            200,
            {"email": "newuser@gmail.com", "name": "New User", "sub": "google-123"},
        )

    monkeypatch.setattr(oauth_service_module.httpx, "post", fake_post)
    monkeypatch.setattr(oauth_service_module.httpx, "get", fake_get)

    response = client.post("/api/v1/auth/oauth/google/callback", json={"code": "fake-code"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_google_callback_logs_in_existing_user(client, configured_settings, monkeypatch):
    client.post(
        "/api/v1/auth/register",
        json={"email": "existing@gmail.com", "password": "correcthorsebattery"},
    )

    def fake_post(url, data=None, timeout=None):
        return _FakeResponse(200, {"access_token": "fake-access-token"})

    def fake_get(url, headers=None, timeout=None):
        return _FakeResponse(200, {"email": "existing@gmail.com", "name": "Existing"})

    monkeypatch.setattr(oauth_service_module.httpx, "post", fake_post)
    monkeypatch.setattr(oauth_service_module.httpx, "get", fake_get)

    response = client.post("/api/v1/auth/oauth/google/callback", json={"code": "fake-code"})
    assert response.status_code == 200

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.json()["email"] == "existing@gmail.com"


def test_google_callback_rejects_failed_token_exchange(client, configured_settings, monkeypatch):
    def fake_post(url, data=None, timeout=None):
        return _FakeResponse(400, {})

    monkeypatch.setattr(oauth_service_module.httpx, "post", fake_post)

    response = client.post("/api/v1/auth/oauth/google/callback", json={"code": "bad-code"})
    assert response.status_code == 400
