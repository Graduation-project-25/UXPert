import pytest
import pandas as pd 
import json
import os 
from unittest.mock import patch, MagicMock
from io import StringIO

from flask import Flask  # Ensure Flask is imported

import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now you can import app (the module)
import app as app_module  # Rename to avoid confusion with the Flask app fixture

# Helper functions for test data
def create_test_elements():
    return [
        {
            "id": "1", 
            "name": "Button1", 
            "type": "BUTTON", 
            "x": 10, 
            "y": 20, 
            "width": 100, 
            "height": 50, 
            "isIconLabeled": True
        },
        {
            "id": "2", 
            "name": "Text1", 
            "type": "TEXT", 
            "x": 120, 
            "y": 30, 
            "width": 150, 
            "height": 30, 
            "isIconLabeled": False
        },
    ]

def create_test_frame_info():
    return {
        "frameName": "Frame1",
        "screen_width": 800, 
        "screen_height": 600
    }

def create_test_request_data():
    return {
        "user_name": "TestUser",
        "design_name": "TestDesign",
        "page_name": "TestPage",
        "frame": create_test_frame_info(),
        "elements": create_test_elements(),
    }

def create_test_saved_design():
    return {
        "frames": [
            {
                "elements": create_test_elements()
            }
        ]
    }

def create_test_minimalist_results():
    return {
        "White Space Ratio: 50%": "50%",
        "Number of Elements: 10": "10",
        "Irrelevant Elements: 2": "2",
        "Score: 80": "80"
    }

def create_test_error_prevention_results():
    return {
        "ErrorPreventionScore": 90,
        "ValidationIssues": ["Issue1"],
        "ConfirmationIssues": ["Issue2"],
        "Feedback": {"detail": "feedback details"}
    }

def create_test_error_handling_results():
    return {
        "ErrorHandlingScore": 85,
        "ErrorIssues": ["Issue3"],
        "RecoveryIssues": ["Issue4"],
        "Feedback" : {"detail" : "error handling feedback"}
    }

def create_test_consistency_results():
    return {
        "ColorConsistency": 95,
        "AlignmentConsistency": 90,
        "SizeProportionality": 88,
        "Feedback": {"detail": "consistency feedback"}
    }

def create_test_recognition_results():
    return {"recognition_detail": "recognition feedback"}

# Mocking database repositories
@pytest.fixture
def app():
    # Use the actual Flask app from app_module instead of creating a new one
    app = app_module.app
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def mock_figma_repository():
    with patch('app.FigmaFeaturesRepository') as MockRepo:  # Changed from 'app_module' to 'app'
        mock_repo = MockRepo.return_value
        yield mock_repo

@pytest.fixture
def mock_feedback_repository():
    with patch('app.FeedbackRepository') as MockRepo:  # Changed from 'app_module' to 'app'
        mock_repo = MockRepo.return_value
        yield mock_repo

@pytest.fixture
def mock_heuristic_factory():
    with patch('app.HeuristicFactory') as MockFactory:  # Changed from 'app_module' to 'app'
        mock_factory = MockFactory.return_value
        yield mock_factory

def test_process_elements_general_exception(app, mock_figma_repository):
    client = app.test_client()  # Use test client
    with app.test_request_context(method='POST', data=json.dumps(create_test_request_data()), content_type='application/json'):
        mock_figma_repository.update_or_insert_frame.side_effect = Exception("Test exception")

        response = client.post('/process', data=json.dumps(create_test_request_data()), content_type='application/json')  # Simulate POST request with data
        result = response.get_json()
        status_code = response.status_code

        assert status_code == 500
        assert "Server error" in result["error"]

# Test cases for get_latest_minimalist_results function
def test_get_latest_minimalist_results_file_exists():
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", MagicMock()) as mock_open, \
         patch("json.load", return_value={"key": [{"evaluation": "test_evaluation"}]}):

        result = app_module.get_latest_minimalist_results()  # Call from the module
        assert result == "test_evaluation"

def test_get_latest_minimalist_results_file_not_exists():
    with patch("os.path.exists", return_value=False):
        result = app_module.get_latest_minimalist_results()  # Call from the module
        assert result == {}

# Test cases for get_new_filename
def test_get_new_filename():
    with patch("os.listdir", return_value=["design_1.json", "design_2.json"]):
        result = app_module.get_new_filename()  # Call from the module
        assert result == os.path.join(app_module.output_folder, "design_3.json")

# Test cases for clean_prefix
def test_clean_prefix():
    assert app_module.clean_prefix("1: Test text") == "Test text"  # Call from the module
    assert app_module.clean_prefix("0: Another text") == "Another text"  # Call from the module
    assert app_module.clean_prefix("No prefix") == "No prefix"  # Call from the module






# # Test cases for process_elements function (using test client)
# def test_process_elements_success(app, mock_figma_repository, mock_feedback_repository, mock_heuristic_factory, capsys):
#     client = app.test_client()  # Use test client to simulate request
#     with app.test_request_context(method='POST', data=json.dumps(create_test_request_data()), content_type='application/json'):
#         mock_figma_repository.update_or_insert_frame.return_value = MagicMock(matched_count=1)
#         mock_figma_repository.get_saved_design.return_value = create_test_saved_design()

#         mock_heuristic_factory.check_rule.return_value.evaluate_rule.side_effect = [
#             create_test_consistency_results(),
#             create_test_minimalist_results(),
#             create_test_recognition_results(),
#             create_test_error_handling_results(),
#             create_test_error_prevention_results()
#         ]

#         response = client.post('/process', data=json.dumps(create_test_request_data()), content_type='application/json')  # Simulate POST request with data
#         result = response.get_json()
#         status_code = response.status_code

#         assert status_code == 200
#         assert "message" in result
#         assert "error_prevention_results" in result
#         assert "consistency_results" in result
#         assert "error_handling_results" in result
#         assert "minimalist_results" in result
#         assert "recognition_results" in result

#         captured = capsys.readouterr()
#         assert "Data inserted successfully." in captured.out
#         assert "Feedback saved successfully." in captured.out

# def test_process_elements_db_error(app, mock_figma_repository, mock_feedback_repository):
#     client = app.test_client()  # Use test client
#     with app.test_request_context(method='POST', data=json.dumps(create_test_request_data()), content_type='application/json'):
#         mock_figma_repository.update_or_insert_frame.return_value = MagicMock(matched_count=1)
#         mock_figma_repository.get_saved_design.return_value = create_test_saved_design()
#         mock_feedback_repository.update_feedback.return_value = MagicMock(matched_count=0)

#         response = client.post('/process', data=json.dumps(create_test_request_data()), content_type='application/json')  # Simulate POST request with data
#         result = response.get_json()
#         status_code = response.status_code

#         assert status_code == 500
#         assert result == {"error": "Failed to update feedback in database"}

# def test_process_elements_retrieve_design_error(app, mock_figma_repository):
#     client = app.test_client()  # Use test client
#     with app.test_request_context(method='POST', data=json.dumps(create_test_request_data()), content_type='application/json'):
#         mock_figma_repository.update_or_insert_frame.return_value = MagicMock(matched_count=1)
#         mock_figma_repository.get_saved_design.return_value = None

#         response = client.post('/process', data=json.dumps(create_test_request_data()), content_type='application/json')  # Simulate POST request with data
#         result = response.get_json()
#         status_code = response.status_code

#         assert status_code == 500
#         assert result == {"error": "Failed to retrieve saved design data"}

