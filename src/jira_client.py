import os
import requests
import re
from typing import Dict, Any, List
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Search for .env in root and venv/
load_dotenv()
load_dotenv("venv/.env")

def fetch_ticket(ticket_id: str) -> Dict[str, Any]:
    """
    Fetches a Jira ticket by ID using the REST API v3.
    Returns a dict with title, description, and acceptance_criteria.
    """
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError("JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be set in .env")

    url = f"{base_url.rstrip('/')}/rest/api/3/issue/{ticket_id}"
    auth = HTTPBasicAuth(email, api_token)
    headers = {"Accept": "application/json"}

    response = requests.get(url, auth=auth, headers=headers)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    fields = data.get("fields", {})
    
    # Title
    title = fields.get("summary", "")
    
    # Description (ADF format in v3)
    description_raw = fields.get("description", {})
    description = _parse_adf_to_text(description_raw) if isinstance(description_raw, dict) else str(description_raw)
    
    # Extract Acceptance Criteria
    ac = _extract_ac_from_text(description)
    
    return {
        "title": title,
        "description": description,
        "acceptance_criteria": ac,
        "ticket_type": fields.get("issuetype", {}).get("name", "Story")
    }

def _parse_adf_to_text(adf: Dict[str, Any]) -> str:
    """Simplistic ADF to text conversion."""
    text_parts = []
    def traverse(node):
        if node.get("type") == "text":
            text_parts.append(node.get("text", ""))
        if "content" in node:
            for child in node["content"]:
                traverse(child)
        if node.get("type") in ["paragraph", "heading"]:
            text_parts.append("\n")
    
    traverse(adf)
    return "".join(text_parts).strip()

def _extract_ac_from_text(text: str) -> List[str]:
    """Extracts lines that look like acceptance criteria or bullet points."""
    lines = text.split("\n")
    ac = []
    # Heuristic: look for lines starting with -, *, or numbered lists after an 'AC' header
    ac_header_pattern = re.compile(r"(?i)(acceptance criteria|ac|requirements):")
    bullet_pattern = re.compile(r"^([\-\*\•]|\d+[\.\)])\s*(.*)")
    
    recording = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if ac_header_pattern.search(line):
            recording = True
            continue
            
        if recording:
            match = bullet_pattern.match(line)
            if match:
                ac.append(match.group(2).strip())
            elif line.endswith(":") and len(line) < 30: # New section starts
                break
    
    # Fallback: if no section found, just take anything that looks like a list
    if not ac:
        for line in lines:
            match = bullet_pattern.match(line.strip())
            if match:
                ac.append(match.group(2).strip())
                
    return ac

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        print(json.dumps(fetch_ticket(sys.argv[1]), indent=2))
