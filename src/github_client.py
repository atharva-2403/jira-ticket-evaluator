import os
import requests
from dotenv import load_dotenv
from typing import Optional, List
from src.schemas import PullRequest, GitHubFile

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("Missing GITHUB_TOKEN in environment variables.")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _parse_pr_url(self, pr_url: str):
        """
        Parses GitHub PR URL to extract owner, repo, and pull_number.
        Example: https://github.com/owner/repo/pull/1
        """
        parts = pr_url.rstrip("/").split("/")
        if "github.com" not in parts or "pull" not in parts:
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
        
        pull_index = parts.index("pull")
        owner = parts[pull_index - 2]
        repo = parts[pull_index - 1]
        pull_number = parts[pull_index + 1]
        
        return owner, repo, pull_number

    def get_pull_request(self, pr_url: str) -> PullRequest:
        """
        Fetches PR details from GitHub and returns a PullRequest Pydantic model.
        """
        owner, repo, pull_number = self._parse_pr_url(pr_url)
        base_api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
        
        # 1. Fetch PR Metadata
        resp = requests.get(base_api_url, headers=self.headers)
        resp.raise_for_status()
        pr_data = resp.json()
        
        # 2. Fetch Files
        files_url = f"{base_api_url}/files"
        resp_files = requests.get(files_url, headers=self.headers)
        resp_files.raise_for_status()
        files_data = resp_files.json()
        
        files = [
            GitHubFile(
                filename=f["filename"],
                status=f["status"],
                additions=f["additions"],
                deletions=f["deletions"],
                patch=f.get("patch")
            )
            for f in files_data
        ]
        
        # 3. Fetch Diff
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        resp_diff = requests.get(base_api_url, headers=diff_headers)
        resp_diff.raise_for_status()
        diff = resp_diff.text
        
        # 4. Fetch Commits
        commits_url = f"{base_api_url}/commits"
        resp_commits = requests.get(commits_url, headers=self.headers)
        resp_commits.raise_for_status()
        commits_data = resp_commits.json()
        commit_messages = [c["commit"]["message"] for c in commits_data]
        
        return PullRequest(
            pr_url=pr_url,
            title=pr_data.get("title", ""),
            description=pr_data.get("body") or "",
            base_branch=pr_data.get("base", {}).get("ref", ""),
            head_branch=pr_data.get("head", {}).get("ref", ""),
            diff=diff,
            files=files,
            commit_messages=commit_messages
        )

if __name__ == "__main__":
    import sys
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="GitHub Client CLI")
    parser.add_argument("--pr", required=True, help="GitHub PR URL")
    args = parser.parse_args()
    
    try:
        client = GitHubClient()
        pr = client.get_pull_request(args.pr)
        print(pr.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
