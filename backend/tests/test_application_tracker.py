import pytest

def test_application_lifecycle_rules():
    valid_statuses = ["Saved", "Viewed", "Applied", "Interview", "Selected", "Rejected"]
    
    # Test valid progression
    current_status = "Saved"
    assert current_status in valid_statuses
    
    current_status = "Applied"
    assert current_status in valid_statuses
    
    current_status = "Interview"
    assert current_status in valid_statuses

def test_response_rate_calculation():
    applied = 10
    interviews = 2
    selected = 1
    
    response_rate = round(((interviews + selected) / applied * 100), 1)
    assert response_rate == 30.0
