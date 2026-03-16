from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_methods_returns_success_response() -> None:
    response = client.get("/api/methods")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["message"] == "ok"
    assert len(payload["data"]) == 3
    assert payload["data"][0]["slug"] == "descriptive_stats"
    assert payload["data"][1]["slug"] == "regression"


def test_get_method_detail_returns_structured_payload() -> None:
    response = client.get("/api/methods/regression")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["message"] == "ok"
    assert payload["data"]["slug"] == "regression"
    assert payload["data"]["input_spec_json"]["min_sample_size"] == 30
    assert payload["data"]["output_spec_json"]["result_blocks"][0]["title"] == "模型摘要"


def test_get_method_detail_returns_unified_not_found_response() -> None:
    response = client.get("/api/methods/unknown-method")

    assert response.status_code == 404
    payload = response.json()

    assert payload == {
        "success": False,
        "message": "method not found",
        "error_code": "METHOD_NOT_FOUND",
        "details": {"slug": "unknown-method"},
    }
