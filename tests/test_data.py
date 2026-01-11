import pytest
import sys
import os

# Add the src directory to the Python path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import activities

class TestDataStructure:
    def test_activities_data_structure(self):
        """Test that activities data structure is valid"""
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            
            # Check required fields
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            
            # Check field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Check that participants list contains only strings (emails)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation

    def test_initial_data_consistency(self):
        """Test that initial data is consistent"""
        for activity_name, activity_data in activities.items():
            participants_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            # Participants count should not exceed maximum
            assert participants_count <= max_participants, f"Activity '{activity_name}' has too many participants"
            
            # Description and schedule should not be empty
            assert activity_data["description"].strip() != "", f"Activity '{activity_name}' has empty description"
            assert activity_data["schedule"].strip() != "", f"Activity '{activity_name}' has empty schedule"

    def test_expected_activities_exist(self):
        """Test that expected activities are present"""
        expected_activities = [
            "Chess Club",
            "Programming Class", 
            "Gym Class",
            "Basketball Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        for expected_activity in expected_activities:
            assert expected_activity in activities, f"Expected activity '{expected_activity}' not found"