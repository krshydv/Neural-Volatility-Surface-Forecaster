def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "forecastapi@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "forecastapi@volaris.ai", "password": "correcthorsebattery"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_forecast_requires_auth(client):
    response = client.post("/api/v1/forecast/AAPL/volatility", json={})
    assert response.status_code == 403


def test_forecast_returns_points(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility",
        json={"horizon_days": 5, "epochs": 100},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert len(body["points"]) == 5
    assert body["trained_on_observations"] > 0


def test_forecast_unknown_symbol_returns_404(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/NOTREAL/volatility",
        json={"horizon_days": 5, "epochs": 50},
        headers=headers,
    )
    assert response.status_code == 404


def test_forecast_accepts_mlp_model_type(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility",
        json={"horizon_days": 5, "epochs": 100, "model_type": "mlp"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["model_type"] == "mlp"


def test_forecast_defaults_to_lstm_model_type(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility",
        json={"horizon_days": 5, "epochs": 100},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["model_type"] == "lstm"


def test_forecast_rejects_invalid_model_type(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility",
        json={"horizon_days": 5, "epochs": 100, "model_type": "rnn"},
        headers=headers,
    )
    assert response.status_code == 422


def test_forecast_rejects_invalid_horizon(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility",
        json={"horizon_days": 100, "epochs": 50},
        headers=headers,
    )
    assert response.status_code == 422
