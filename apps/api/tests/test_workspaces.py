def _register_and_login(client, email):
    client.post("/api/v1/auth/register", json={"email": email, "password": "correcthorsebattery"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "correcthorsebattery"})
    return login.json()["access_token"]


def test_create_and_list_workspace(client):
    token = _register_and_login(client, "ws1@volaris.ai")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/api/v1/workspaces",
        json={"name": "SPY Macro Regime Study", "description": "Regime timeline research"},
        headers=headers,
    )
    assert create.status_code == 201

    listing = client.get("/api/v1/workspaces", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert listing.json()[0]["name"] == "SPY Macro Regime Study"


def test_workspace_persists_layout_state(client):
    token = _register_and_login(client, "ws2@volaris.ai")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/api/v1/workspaces", json={"name": "Tech Sector IV"}, headers=headers
    )
    workspace_id = create.json()["id"]

    update = client.patch(
        f"/api/v1/workspaces/{workspace_id}",
        json={"layout_state": {"selected_asset": "NVDA", "active_tab": "surface"}},
        headers=headers,
    )
    assert update.status_code == 200
    assert update.json()["layout_state"]["selected_asset"] == "NVDA"

    fetched = client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert fetched.json()["layout_state"]["active_tab"] == "surface"


def test_users_cannot_access_other_users_workspaces(client):
    token_a = _register_and_login(client, "owner@volaris.ai")
    token_b = _register_and_login(client, "intruder@volaris.ai")

    create = client.post(
        "/api/v1/workspaces",
        json={"name": "Private Research"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    workspace_id = create.json()["id"]

    intruder_access = client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert intruder_access.status_code == 404


def test_delete_workspace(client):
    token = _register_and_login(client, "deleter@volaris.ai")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/api/v1/workspaces", json={"name": "Temp"}, headers=headers)
    workspace_id = create.json()["id"]

    delete = client.delete(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert delete.status_code == 204

    fetched = client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert fetched.status_code == 404
