"""Tests for the Mergington High School activity registration API.

The ``client`` fixture is provided by conftest.py and is auto-discovered by pytest.
"""


def test_get_activities_returns_activity_map(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload


def test_signup_adds_participant_to_selected_activity_only(client):
    signup_email = "newstudent@mergington.edu"

    before_chess = client.get("/activities").json()["Chess Club"]["participants"]
    before_soccer = client.get("/activities").json()["Soccer Team"]["participants"]

    response = client.post("/activities/Chess%20Club/signup", params={"email": signup_email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {signup_email} for Chess Club"

    after_payload = client.get("/activities").json()
    assert signup_email in after_payload["Chess Club"]["participants"]
    assert len(after_payload["Chess Club"]["participants"]) == len(before_chess) + 1
    assert after_payload["Soccer Team"]["participants"] == before_soccer


def test_signup_rejects_duplicate_participant(client):
    existing_email = "michael@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post("/activities/Robotics%20Club/signup", params={"email": "a@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_handles_encoded_email_and_activity_name(client):
    encoded_email = "sam+7@mergington.edu"

    response = client.post("/activities/Science%20Olympiad/signup", params={"email": encoded_email})

    assert response.status_code == 200
    activities_payload = client.get("/activities").json()
    assert encoded_email in activities_payload["Science Olympiad"]["participants"]


def test_unregister_removes_participant(client):
    target_email = "emma@mergington.edu"

    response = client.delete("/activities/Programming%20Class/participants", params={"email": target_email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {target_email} from Programming Class"

    activities_payload = client.get("/activities").json()
    assert target_email not in activities_payload["Programming Class"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete("/activities/Robotics%20Club/participants", params={"email": "a@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_for_non_member(client):
    response = client.delete(
        "/activities/Basketball%20Team/participants",
        params={"email": "doesnotexist@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_rejects_empty_email(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": ""},
    )

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload


def test_signup_rejects_whitespace_email(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "   "},
    )

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload


def test_signup_requires_email_param(client):
    response = client.post("/activities/Chess%20Club/signup")

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload


def test_unregister_rejects_empty_email(client):
    response = client.delete(
        "/activities/Programming%20Class/participants",
        params={"email": ""},
    )

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload


def test_unregister_rejects_whitespace_email(client):
    response = client.delete(
        "/activities/Programming%20Class/participants",
        params={"email": "   "},
    )

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload


def test_unregister_requires_email_param(client):
    response = client.delete("/activities/Programming%20Class/participants")

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload