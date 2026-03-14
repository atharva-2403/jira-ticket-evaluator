import pytest
from unittest.mock import patch, MagicMock
from src.agent import Agent
from src.schemas import JiraTicket, PullRequest, GitHubFile

@pytest.fixture
def agent():
    with patch.dict('os.environ', {
        "ANTHROPIC_API_KEY": "test-key",
        "JIRA_BASE_URL": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
        "GITHUB_TOKEN": "test-token"
    }):
        return Agent()

def test_evaluate_pr_success(agent):
    # Mock JiraClient
    mock_ticket = JiraTicket(
        ticket_id="PROJ-123",
        title="Add login",
        description="Add login feature",
        acceptance_criteria=["Must have email", "Must have password"],
        ticket_type="Story"
    )
    
    # Mock GitHubClient
    mock_pr = PullRequest(
        pr_url="https://github.com/owner/repo/pull/1",
        title="Add login",
        description="Implemented login",
        base_branch="main",
        head_branch="login",
        diff="diff code...",
        files=[GitHubFile(filename="login.py", status="added", additions=10, deletions=0)],
        commit_messages=["Initial commit"]
    )
    
    # Mock Anthropic Response for Requirements Extraction
    mock_resp_extract = MagicMock()
    mock_resp_extract.content = [MagicMock(text='["Must have email", "Must have password"]')]
    
    # Mock Anthropic Response for Evaluation
    mock_resp_eval = MagicMock()
    mock_resp_eval.content = [MagicMock(text='Evaluation details...')]
    
    with patch.object(agent.jira_client, 'get_ticket', return_value=mock_ticket), \
         patch.object(agent.github_client, 'get_pull_request', return_value=mock_pr), \
         patch.object(agent.anthropic_client.messages, 'create', side_effect=[mock_resp_extract, mock_resp_eval]):
        
        result = agent.evaluate_pr("PROJ-123", "https://github.com/owner/repo/pull/1")
        
        assert result.ticket_id == "PROJ-123"
        assert result.overall == "Pass"
        assert len(result.requirements) == 2
        assert result.requirements[0].verdict == "Pass"
