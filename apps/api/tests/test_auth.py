def test_register_creates_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "trader@volaris.ai", "password": "correcthorsebattery", "full_name": "Trader"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "trader@volaris.ai"
    assert "hashed_password" not in body


def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@volaris.ai", "password": "correcthorsebattery"}
    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


def test_login_returns_tokens(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@volaris.ai", "password": "correcthorsebattery"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@volaris.ai", "password": "correcthorsebattery"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]


def test_login_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@volaris.ai", "password": "correcthorsebattery"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@volaris.ai", "password": "incorrectpassword"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_me_returns_current_user(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "me@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "me@volaris.ai", "password": "correcthorsebattery"},
    )
    token = login.json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@volaris.ai"


def test_refresh_token_issues_new_access_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@volaris.ai", "password": "correcthorsebattery"},
    )
    refresh_token = login.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["access_token"]
