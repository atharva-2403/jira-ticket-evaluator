import pytest
import requests
from unittest.mock import patch, MagicMock
from src.jira_client import fetch_ticket

@patch('requests.get')
def test_fetch_ticket_returns_structured_data(mock_get):
    """Verifies that fetch_ticket correctly parses a successful Jira response."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "fields": {
            "summary": "Mock Title",
            "description": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Requirements:"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "- Use Python 3.12"}]
                    }
                ]
            },
            "issuetype": {"name": "Bug"}
        }
    }
    mock_get.return_value = mock_response

    # Call function
    with patch.dict('os.environ', {
        "JIRA_BASE_URL": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "token"
    }):
        data = fetch_ticket("PROJ-123")

    # Assertions
    assert data["title"] == "Mock Title"
    assert "Use Python 3.12" in data["description"]
    assert "Use Python 3.12" in data["acceptance_criteria"]
    assert data["ticket_type"] == "Bug"

@patch('requests.get')
def test_fetch_ticket_invalid_id_raises_error(mock_get):
    """Verifies that an API error raises an exception."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    with patch.dict('os.environ', {
        "JIRA_BASE_URL": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "token"
    }):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_ticket("INVALID-1")
