import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Search for .env in root and venv/
load_dotenv()
load_dotenv("venv/.env")

def fetch_pr(pr_url: str) -> Dict[str, Any]:
    """
    Fetches PR details from GitHub using the REST API.
    Returns diff, files_changed, pr_description, and commit_messages.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN must be set in .env")

    owner, repo, pull_number = _parse_pr_url(pr_url)
    base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Fetch Metadata
    resp = requests.get(base_url, headers=headers)
    resp.raise_for_status()
    pr_data = resp.json()

    # 2. Fetch Files Changed
    resp_files = requests.get(f"{base_url}/files", headers=headers)
    resp_files.raise_for_status()
    files_changed = [f["filename"] for f in resp_files.json()]

    # 3. Fetch Commit Messages
    resp_commits = requests.get(f"{base_url}/commits", headers=headers)
    resp_commits.raise_for_status()
    commit_messages = [c["commit"]["message"] for c in resp_commits.json()]

    # 4. Fetch Diff
    diff_headers = headers.copy()
    diff_headers["Accept"] = "application/vnd.github.v3.diff"
    resp_diff = requests.get(base_url, headers=diff_headers)
    resp_diff.raise_for_status()
    diff = resp_diff.text

    return {
        "title": pr_data.get("title", ""),
        "pr_description": pr_data.get("body") or "",
        "files_changed": files_changed,
        "commit_messages": commit_messages,
        "diff": diff
    }

def _parse_pr_url(pr_url: str):
    """Extracts owner, repo, and pull_number from a GitHub PR URL."""
    parts = pr_url.rstrip("/").split("/")
    # https://github.com/owner/repo/pull/123
    if "github.com" not in parts or "pull" not in parts:
        raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
    
    pull_index = parts.index("pull")
    owner = parts[pull_index - 2]
    repo = parts[pull_index - 1]
    pull_number = parts[pull_index + 1]
    
    return owner, repo, pull_number

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        print(json.dumps(fetch_pr(sys.argv[1]), indent=2))
