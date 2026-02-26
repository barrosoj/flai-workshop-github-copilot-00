from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_normalized_participant():
    response = client.post("/activities/Chess Club/signup", params={"email": " NewStudent@Mergington.edu "})

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_409():
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 409
    assert "already signed up" in response.json()["detail"]


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_from_activity():
    response = client.delete("/activities/Chess Club/participants", params={"email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete("/activities/Chess Club/participants", params={"email": "ghost@mergington.edu"})

    assert response.status_code == 404
    assert "is not signed up" in response.json()["detail"]


def test_unregister_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown Club/participants", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
