import pytest
import requests
from unittest.mock import patch, MagicMock
from src.github_client import fetch_pr

@patch('requests.get')
def test_fetch_pr_returns_diff(mock_get):
    """Verifies that fetch_pr correctly gathers PR data from multiple endpoints."""
    # Setup mocks for metadata, files, commits, and diff
    mock_meta = MagicMock()
    mock_meta.json.return_value = {"title": "Fix bug", "body": "Fixed it."}
    
    mock_files = MagicMock()
    mock_files.json.return_value = [{"filename": "main.py"}]
    
    mock_commits = MagicMock()
    mock_commits.json.return_value = [{"commit": {"message": "fix: logic"}}]
    
    mock_diff = MagicMock()
    mock_diff.text = "diff content"
    
    mock_get.side_effect = [mock_meta, mock_files, mock_commits, mock_diff]

    with patch.dict('os.environ', {"GITHUB_TOKEN": "test-token"}):
        data = fetch_pr("https://github.com/owner/repo/pull/1")

    assert data["title"] == "Fix bug"
    assert data["files_changed"] == ["main.py"]
    assert data["diff"] == "diff content"
    assert "fix: logic" in data["commit_messages"]

def test_fetch_pr_invalid_url_raises_error():
    """Verifies that an incorrectly formatted URL is caught early."""
    with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
        fetch_pr("https://notgithub.com/bad/url")

@patch('requests.get')
def test_fetch_pr_api_failure(mock_get):
    """Verifies that GitHub API failures raise an exception."""
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    
    with patch.dict('os.environ', {"GITHUB_TOKEN": "test-token"}):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_pr("https://github.com/owner/repo/pull/1")
