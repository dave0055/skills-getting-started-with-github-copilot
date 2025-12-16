import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Preserve original state and restore after each test to avoid cross-test pollution
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert "Basketball" in data
    assert isinstance(data, dict)


def test_signup_and_duplicate(client):
    email = "test.user@example.com"
    # Signup
    resp = client.post("/activities/Tennis Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")
    assert email in activities["Tennis Club"]["participants"]

    # Duplicate signup should fail
    resp2 = client.post("/activities/Tennis Club/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister_and_errors(client):
    # Ensure a known participant exists
    assert "lucas@mergington.edu" in activities["Art Studio"]["participants"]

    # Unregister existing participant
    resp = client.delete("/activities/Art Studio/participants", params={"email": "lucas@mergington.edu"})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")
    assert "lucas@mergington.edu" not in activities["Art Studio"]["participants"]

    # Unregister unknown participant returns 400
    resp2 = client.delete("/activities/Art Studio/participants", params={"email": "unknown@x.com"})
    assert resp2.status_code == 400

    # Unregister on non-existing activity returns 404
    resp3 = client.delete("/activities/Nonexistent/participants", params={"email": "a@b.com"})
    assert resp3.status_code == 404
