def test_metrics_endpoint_returns_prometheus_text(client):
    client.get("/api/v1/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "hermes_http_requests_total" in response.text
    assert "hermes_http_request_duration_seconds" in response.text


def test_metrics_endpoint_counts_requests(client):
    before = client.get("/metrics").text
    client.get("/api/v1/health")
    after = client.get("/metrics").text
    assert after != before
