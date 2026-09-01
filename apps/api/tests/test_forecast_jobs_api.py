class _FakeAsyncResultHandle:
    id = "fake-job-id"


class _FakeTask:
    @staticmethod
    def delay(*args, **kwargs):
        return _FakeAsyncResultHandle()


class _FakeAsyncResult:
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = "SUCCESS"
        self.result = {"symbol": "AAPL", "model_type": "lstm", "points": []}

    def successful(self):
        return True

    def failed(self):
        return False


def _auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "forecastjobs@volaris.ai", "password": "correcthorsebattery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "forecastjobs@volaris.ai", "password": "correcthorsebattery"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_enqueue_forecast_job_returns_job_id(client, monkeypatch):
    import app.workers.forecast_tasks as forecast_tasks

    monkeypatch.setattr(forecast_tasks, "run_volatility_forecast_task", _FakeTask())

    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility/jobs",
        json={"horizon_days": 5, "epochs": 100, "model_type": "lstm"},
        headers=headers,
    )
    assert response.status_code == 202
    assert response.json()["job_id"] == "fake-job-id"
    assert response.json()["status"] == "queued"


def test_get_forecast_job_returns_status(client, monkeypatch):
    import app.workers.celery_app as celery_app_module

    monkeypatch.setattr(
        celery_app_module.celery_app,
        "AsyncResult",
        lambda job_id: _FakeAsyncResult(job_id),
    )

    headers = _auth_headers(client)
    response = client.get("/api/v1/forecast/jobs/fake-job-id", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == "fake-job-id"
    assert body["status"] == "SUCCESS"
    assert body["result"]["symbol"] == "AAPL"


def test_enqueue_forecast_job_requires_auth(client):
    response = client.post(
        "/api/v1/forecast/AAPL/volatility/jobs",
        json={"horizon_days": 5, "epochs": 100},
    )
    assert response.status_code == 403


def test_enqueue_forecast_job_returns_503_when_broker_unreachable(client, monkeypatch):
    def _raise(*args, **kwargs):
        raise ConnectionError("broker unreachable")

    import app.workers.forecast_tasks as forecast_tasks

    monkeypatch.setattr(forecast_tasks.run_volatility_forecast_task, "delay", _raise)

    headers = _auth_headers(client)
    response = client.post(
        "/api/v1/forecast/AAPL/volatility/jobs",
        json={"horizon_days": 5, "epochs": 100},
        headers=headers,
    )
    assert response.status_code == 503
