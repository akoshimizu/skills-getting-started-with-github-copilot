import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == original_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = quote("Basketball Team", safe="")
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Team"
    }
    assert email in activities["Basketball Team"]["participants"]


def test_signup_for_activity_returns_400_when_already_signed_up():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = quote("Nonexistent Club", safe="")
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_successfully_removes_participant():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from Chess Club"
    }
    assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_returns_404_when_participant_missing():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "not-registered@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_returns_404_for_missing_activity():
    # Arrange
    activity_name = quote("Nonexistent Club", safe="")
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
