import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from typing import Optional
import re
from src.schemas import JiraTicket

load_dotenv()

class JiraClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("Missing Jira configuration in environment variables.")
        
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_ticket(self, ticket_id: str) -> JiraTicket:
        """
        Fetches a Jira ticket by ID and returns a JiraTicket Pydantic model.
        """
        url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        
        if response.status_code != 200:
            response.raise_for_status()
            
        data = response.json()
        fields = data.get("fields", {})
        
        title = fields.get("summary", "")
        # description in Jira API v3 is ADF (Atlassian Document Format), which is a complex JSON.
        # For simplicity in this evaluator, we'll try to extract plain text if possible
        # or handle it if it's already a string (some setups might return string).
        description_raw = fields.get("description", "")
        description = self._parse_adf_to_text(description_raw) if isinstance(description_raw, dict) else str(description_raw)
        
        ticket_type = fields.get("issuetype", {}).get("name", "Story")
        
        acceptance_criteria = self._extract_acceptance_criteria(description)
        
        return JiraTicket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            ticket_type=ticket_type
        )

    def _parse_adf_to_text(self, adf: dict) -> str:
        """
        Simplistic ADF to text conversion.
        """
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

    def _extract_acceptance_criteria(self, description: str) -> list[str]:
        """
        Extracts acceptance criteria from description using common patterns.
        Looks for sections like "Acceptance Criteria", "AC:", "Requirements", etc.
        """
        criteria = []
        
        # Try to find a section header
        patterns = [
            r"(?i)Acceptance Criteria[:\s]*(.*)",
            r"(?i)AC[:\s]*(.*)",
            r"(?i)Requirements[:\s]*(.*)"
        ]
        
        found_section = False
        lines = description.split("\n")
        
        ac_start_index = -1
        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    ac_start_index = i
                    found_section = True
                    break
            if found_section:
                break
        
        if ac_start_index != -1:
            # Extract bullet points following the header
            for line in lines[ac_start_index+1:]:
                line = line.strip()
                if not line:
                    continue
                # If we hit another header-like line, stop
                if line.endswith(":") and len(line) < 30:
                    break
                # Match common bullet point markers: -, *, 1., 1)
                match = re.match(r"^([\-\*\•]|\d+[\.\)])\s*(.*)", line)
                if match:
                    criteria.append(match.group(2).strip())
                else:
                    # If it's not a bullet point but we are in the section, maybe it's just a line of text
                    if criteria: # only if we already found some bullet points
                        break
                    # If no bullet point found yet, maybe the first line is the criterion
                    if line:
                        criteria.append(line)
                        # but then we stop unless more bullet points follow? 
                        # Actually Jira often uses list types in ADF.
        
        # If no criteria found via headers, try to find any bulleted list at the end
        if not criteria:
            for line in lines:
                match = re.match(r"^([\-\*\•]|\d+[\.\)])\s*(.*)", line)
                if match:
                    criteria.append(match.group(2).strip())
                    
        return criteria

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Jira Client CLI")
    parser.add_argument("--ticket", required=True, help="Jira Ticket ID (e.g., PROJ-123)")
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        ticket = client.get_ticket(args.ticket)
        print(ticket.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
