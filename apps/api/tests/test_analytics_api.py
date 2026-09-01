def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "analyticsapi@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "analyticsapi@volaris.ai", "password": "correcthorsebattery"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_regime_endpoint_returns_current_regime(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/analytics/AAPL/regime", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["current_regime"] in {"Low volatility", "Medium volatility", "High volatility"}


def test_regime_endpoint_unknown_symbol(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/analytics/NOTREAL/regime", headers=headers)
    assert response.status_code == 404


def test_scenario_endpoint_returns_contracts(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/analytics/AAPL/scenario",
        json={"spot_shock_pct": 0.1, "vol_shock_pct": 0.2},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["contracts"]) > 0
    assert body["shocked_spot"] > body["base_spot"]


def test_risk_endpoint_returns_exposure(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/analytics/AAPL/risk", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["contract_count"] > 0


def test_analytics_requires_auth(client):
    response = client.get("/api/v1/analytics/AAPL/regime")
    assert response.status_code == 403
