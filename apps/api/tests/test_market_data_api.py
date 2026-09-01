def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "marketapi@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "marketapi@volaris.ai", "password": "correcthorsebattery"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_list_assets_requires_auth(client):
    response = client.get("/api/v1/assets")
    assert response.status_code == 403


def test_list_assets_returns_registry(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/assets", headers=headers)
    assert response.status_code == 200
    symbols = {a["symbol"] for a in response.json()}
    assert "AAPL" in symbols


def test_get_asset_returns_details(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/assets/AAPL", headers=headers)
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"


def test_get_asset_unknown_symbol_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/assets/NOTREAL", headers=headers)
    assert response.status_code == 404


def test_get_asset_events(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/assets/AAPL/events", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_options_chain(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/options/SPY/chain", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "SPY"
    assert len(body["contracts"]) > 0
    assert body["spot"] > 0


def test_get_options_chain_unknown_symbol_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/options/NOTREAL/chain", headers=headers)
    assert response.status_code == 404


def test_build_volatility_surface_from_real_chain(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/volatility/SPY/surface",
        json={"method": "linear", "grid_resolution": 12},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "SPY"
    assert len(body["moneyness_grid"]) == 12
    assert len(body["volatility_grid"]) == 12
    assert all(v > 0 for row in body["volatility_grid"] for v in row)


def test_build_volatility_surface_unknown_symbol_returns_404(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/volatility/NOTREAL/surface", json={}, headers=headers
    )
    assert response.status_code == 404


def test_build_volatility_surface_rejects_unknown_method(client):
    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/volatility/SPY/surface", json={"method": "bogus"}, headers=headers
    )
    assert response.status_code == 400
