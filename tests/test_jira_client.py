import pytest
from unittest.mock import patch, MagicMock
from src.jira_client import JiraClient
from src.schemas import JiraTicket

@pytest.fixture
def jira_client():
    with patch.dict('os.environ', {
        "JIRA_BASE_URL": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token"
    }):
        return JiraClient()

def test_get_ticket_success(jira_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "fields": {
            "summary": "Test Ticket",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "This is a test ticket."}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Acceptance Criteria:"}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "- Requirement 1"}
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "- Requirement 2"}
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Story"}
        }
    }
    
    with patch('requests.get', return_value=mock_response):
        ticket = jira_client.get_ticket("PROJ-123")
        
        assert ticket.ticket_id == "PROJ-123"
        assert ticket.title == "Test Ticket"
        assert "This is a test ticket." in ticket.description
        assert "Requirement 1" in ticket.acceptance_criteria
        assert "Requirement 2" in ticket.acceptance_criteria
        assert len(ticket.acceptance_criteria) == 2

def test_extract_acceptance_criteria_simple_text():
    client = MagicMock(spec=JiraClient)
    # Using real method for testing extraction logic
    client._extract_acceptance_criteria = JiraClient._extract_acceptance_criteria.__get__(client, JiraClient)
    
    description = """
    Some description here.
    
    Acceptance Criteria:
    - Must be fast
    - Must be secure
    * Should be easy to use
    """
    
    criteria = client._extract_acceptance_criteria(description)
    assert "Must be fast" in criteria
    assert "Must be secure" in criteria
    assert "Should be easy to use" in criteria
    assert len(criteria) == 3

def test_extract_acceptance_criteria_ac_header():
    client = MagicMock(spec=JiraClient)
    client._extract_acceptance_criteria = JiraClient._extract_acceptance_criteria.__get__(client, JiraClient)
    
    description = """
    AC:
    1. Do this
    2. Do that
    """
    
    criteria = client._extract_acceptance_criteria(description)
    assert "Do this" in criteria
    assert "Do that" in criteria
    assert len(criteria) == 2
