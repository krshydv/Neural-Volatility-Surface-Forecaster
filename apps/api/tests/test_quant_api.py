import pytest


def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "quantapi@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "quantapi@volaris.ai", "password": "correcthorsebattery"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_price_endpoint_requires_auth(client):
    response = client.post(
        "/api/v1/quant/price",
        json={
            "spot": 100,
            "strike": 100,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "volatility": 0.2,
        },
    )
    assert response.status_code == 403


def test_price_endpoint_returns_call_and_put_with_greeks(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/quant/price",
        json={
            "spot": 100,
            "strike": 100,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "volatility": 0.2,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["call_price"] == pytest.approx(10.4506, abs=1e-3)
    assert body["put_price"] == pytest.approx(5.5735, abs=1e-3)
    assert "delta" in body["call_greeks"]
    assert "vega" in body["put_greeks"]


def test_implied_volatility_endpoint_recovers_known_volatility(client):
    headers = _auth_headers(client)
    price_response = client.post(
        "/api/v1/quant/price",
        json={
            "spot": 100,
            "strike": 105,
            "time_to_expiry": 0.5,
            "risk_free_rate": 0.04,
            "volatility": 0.25,
        },
        headers=headers,
    )
    market_price = price_response.json()["call_price"]

    iv_response = client.post(
        "/api/v1/quant/implied-volatility",
        json={
            "market_price": market_price,
            "spot": 100,
            "strike": 105,
            "time_to_expiry": 0.5,
            "risk_free_rate": 0.04,
            "option_type": "call",
        },
        headers=headers,
    )
    assert iv_response.status_code == 200
    assert iv_response.json()["implied_volatility"] == pytest.approx(0.25, abs=1e-3)


def test_implied_volatility_endpoint_rejects_arbitrage_violation(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/quant/implied-volatility",
        json={
            "market_price": 500,
            "spot": 100,
            "strike": 100,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "option_type": "call",
        },
        headers=headers,
    )
    assert response.status_code == 400


def test_historical_volatility_endpoint(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/quant/historical-volatility",
        json={"prices": [100.0, 101.0, 99.0, 100.5, 98.5, 102.0, 103.5]},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["realized_volatility"] > 0
