import pytest
from fastapi.testclient import TestClient

from merino.main import app
from merino.providers import get_providers
from tests.web.util import get_providers as override_dependency

client = TestClient(app)
app.dependency_overrides[get_providers] = override_dependency


def test_suggest_sponsored():
    response = client.get("/api/v1/suggest?q=sponsored")
    assert response.status_code == 200

    result = response.json()
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["full_keyword"] == "sponsored"
    assert result["request_id"] is not None


def test_suggest_nonsponsored():
    response = client.get("/api/v1/suggest?q=nonsponsored")

    assert response.status_code == 200

    result = response.json()
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["full_keyword"] == "nonsponsored"
    assert result["request_id"] is not None


def test_no_suggestion():
    response = client.get("/api/v1/suggest?q=nope")
    assert response.status_code == 200
    assert len(response.json()["suggestions"]) == 0


@pytest.mark.parametrize("query", ["sponsored", "nonsponsored"])
def test_suggest_from_missing_providers(query):
    """
    Despite the keyword being available for other providers, it should not return any suggestions
    if the requested provider does not exist.
    """
    response = client.get(f"/api/v1/suggest?q={query}&providers=nonexist")
    assert response.status_code == 200
    assert len(response.json()["suggestions"]) == 0


def test_no_query_string():
    response = client.get("/api/v1/suggest")
    assert response.status_code == 400


def test_providers():
    response = client.get("/api/v1/providers")
    assert response.status_code == 200

    providers = response.json()
    assert len(providers) == 2
    assert set([provider["id"] for provider in providers]) == set(
        ["sponsored-provider", "nonsponsored-provider"]
    )


def test_request_logs_contain_required_info(mocker, caplog):
    import logging

    caplog.set_level(logging.INFO)

    # Use a valid IP to avoid the geolocation errors/logs
    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = "127.0.0.1"

    query = "nope"
    sid = "deadbeef-0000-1111-2222-333344445555"
    seq = 0
    root_path = "/api/v1/suggest"
    client.get(f"{root_path}?q={query}&sid={sid}&seq={seq}")

    assert len(caplog.records) == 1

    record = caplog.records[0]

    assert record.path == root_path
    assert record.session_id == sid
    assert record.sequence_no == seq