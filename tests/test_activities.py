"""Tests for the activities endpoints"""
import pytest


def test_root_redirect(client):
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that we can fetch all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have activities
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check that each activity has required fields
    for activity_name, activity_data in data.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_get_specific_activities(client):
    """Test that specific activities exist with correct data"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Test Chess Club exists
    assert "Chess Club" in data
    chess_club = data["Chess Club"]
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify the participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]


def test_signup_duplicate_student(client):
    """Test that a student cannot sign up twice for the same activity"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        "/activities/Tennis Club/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        "/activities/Tennis Club/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test that signup fails for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity(client):
    """Test unregistering a participant from an activity"""
    email = "unregister@mergington.edu"
    
    # First, sign up
    client.post(
        "/activities/Drama Club/signup",
        params={"email": email}
    )
    
    # Verify they're registered
    activities = client.get("/activities").json()
    assert email in activities["Drama Club"]["participants"]
    
    # Now unregister
    response = client.delete(
        "/activities/Drama Club/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert email in data["message"]
    assert "Unregistered" in data["message"]
    
    # Verify they're no longer registered
    activities = client.get("/activities").json()
    assert email not in activities["Drama Club"]["participants"]


def test_unregister_nonexistent_activity(client):
    """Test that unregister fails for non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_registered_student(client):
    """Test that unregister fails when student is not registered"""
    response = client.delete(
        "/activities/Art Studio/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_signup_and_unregister_multiple_students(client):
    """Test multiple signup and unregister operations"""
    students = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    activity = "Robotics Club"
    
    # Sign up all students
    for email in students:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all are registered
    activities = client.get("/activities").json()
    for email in students:
        assert email in activities[activity]["participants"]
    
    # Unregister middle student
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": students[1]}
    )
    assert response.status_code == 200
    
    # Verify only middle student was removed
    activities = client.get("/activities").json()
    assert students[0] in activities[activity]["participants"]
    assert students[1] not in activities[activity]["participants"]
    assert students[2] in activities[activity]["participants"]
