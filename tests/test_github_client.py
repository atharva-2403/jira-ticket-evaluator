import pytest
from unittest.mock import patch, MagicMock
from src.github_client import GitHubClient
from src.schemas import PullRequest

@pytest.fixture
def github_client():
    with patch.dict('os.environ', {"GITHUB_TOKEN": "test-token"}):
        return GitHubClient()

def test_parse_pr_url(github_client):
    owner, repo, pull = github_client._parse_pr_url("https://github.com/owner/repo/pull/123")
    assert owner == "owner"
    assert repo == "repo"
    assert pull == "123"

def test_get_pull_request_success(github_client):
    # Mock PR metadata
    mock_pr_resp = MagicMock()
    mock_pr_resp.status_code = 200
    mock_pr_resp.json.return_value = {
        "title": "Fix Bug",
        "body": "This PR fixes a bug.",
        "base": {"ref": "main"},
        "head": {"ref": "fix-branch"}
    }
    
    # Mock Files
    mock_files_resp = MagicMock()
    mock_files_resp.status_code = 200
    mock_files_resp.json.return_value = [
        {"filename": "src/main.py", "status": "modified", "additions": 10, "deletions": 5, "patch": "@@ ..."}
    ]
    
    # Mock Diff
    mock_diff_resp = MagicMock()
    mock_diff_resp.status_code = 200
    mock_diff_resp.text = "diff --git a/src/main.py b/src/main.py..."
    
    # Mock Commits
    mock_commits_resp = MagicMock()
    mock_commits_resp.status_code = 200
    mock_commits_resp.json.return_value = [
        {"commit": {"message": "Fixing the bug"}}
    ]
    
    def side_effect(url, headers=None):
        if url.endswith("/123"):
            if headers.get("Accept") == "application/vnd.github.v3.diff":
                return mock_diff_resp
            return mock_pr_resp
        if url.endswith("/files"):
            return mock_files_resp
        if url.endswith("/commits"):
            return mock_commits_resp
        return MagicMock(status_code=404)

    with patch('requests.get', side_effect=side_effect):
        pr = github_client.get_pull_request("https://github.com/owner/repo/pull/123")
        
        assert pr.title == "Fix Bug"
        assert pr.base_branch == "main"
        assert len(pr.files) == 1
        assert pr.files[0].filename == "src/main.py"
        assert "Fixing the bug" in pr.commit_messages
        assert pr.diff.startswith("diff")
