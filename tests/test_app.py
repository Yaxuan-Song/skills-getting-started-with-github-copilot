import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

# Create a test client
client = TestClient(app)

class TestActivitiesAPI:
    def test_root_redirect(self):
        """Test that root path redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        
        # Check that we have some expected activities
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        
        # Verify activity structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
        assert isinstance(chess_club["participants"], list)
        assert isinstance(chess_club["max_participants"], int)

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        # Use an activity with available spots
        response = client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "test@mergington.edu" in result["message"]
        assert "Basketball Team" in result["message"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_signup_duplicate_participant(self):
        """Test that duplicate signup is prevented"""
        # First signup
        client.post("/activities/Swimming Club/signup?email=duplicate@mergington.edu")
        
        # Second signup (should fail)
        response = client.post("/activities/Swimming Club/signup?email=duplicate@mergington.edu")
        assert response.status_code == 400
        
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_remove_participant_success(self):
        """Test successful removal of a participant"""
        # First add a participant
        client.post("/activities/Art Studio/signup?email=toremove@mergington.edu")
        
        # Then remove them
        response = client.delete("/activities/Art Studio/participants/toremove@mergington.edu")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Removed toremove@mergington.edu from Art Studio" == result["message"]

    def test_remove_nonexistent_participant(self):
        """Test removal of non-existent participant"""
        response = client.delete("/activities/Drama Club/participants/nonexistent@mergington.edu")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Participant not found in this activity"

    def test_remove_participant_from_nonexistent_activity(self):
        """Test removal from non-existent activity"""
        response = client.delete("/activities/Nonexistent Activity/participants/test@mergington.edu")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_activity_capacity_tracking(self):
        """Test that activity capacity is properly tracked"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            participants_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            # Ensure participants count doesn't exceed maximum
            assert participants_count <= max_participants
            
            # Ensure all required fields exist
            assert "description" in activity_data
            assert "schedule" in activity_data
            
    def test_email_validation_format(self):
        """Test that email parameter is properly handled"""
        # Test with URL encoded email
        response = client.post("/activities/Science Club/signup?email=test%40mergington.edu")
        assert response.status_code == 200
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "test@mergington.edu" in activities["Science Club"]["participants"]