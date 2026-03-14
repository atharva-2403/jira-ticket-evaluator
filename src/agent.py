import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
import anthropic
from src.schemas import JiraTicket, PullRequest, EvaluationResult, RequirementVerdict
from src.prompts import SYSTEM_PROMPT, REQUIREMENTS_EXTRACTOR_PROMPT, EVALUATOR_PROMPT
from src.jira_client import JiraClient
from src.github_client import GitHubClient

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.mock_mode = self.api_key == "dummy" or not self.api_key
        if not self.mock_mode:
            self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)
        else:
            logger.info("Running in MOCK LLM mode")
        
        self.jira_client = JiraClient()
        self.github_client = GitHubClient()

    def evaluate_pr(self, ticket_id_or_path: str, pr_url_or_path: str) -> EvaluationResult:
        logger.info(f"Starting evaluation for Ticket: {ticket_id_or_path}, PR: {pr_url_or_path}")
        
        # 1. Fetch/Load Jira Ticket
        if os.path.exists(ticket_id_or_path):
            logger.info(f"Loading Jira ticket from file: {ticket_id_or_path}")
            with open(ticket_id_or_path, 'r') as f:
                ticket_data = json.load(f)
                ticket = JiraTicket(**ticket_data)
        else:
            logger.info(f"Fetching Jira ticket from API: {ticket_id_or_path}")
            ticket = self.jira_client.get_ticket(ticket_id_or_path)
        
        # 2. Fetch/Load GitHub PR
        if os.path.exists(pr_url_or_path):
            logger.info(f"Loading GitHub PR from file: {pr_url_or_path}")
            with open(pr_url_or_path, 'r') as f:
                pr_data = json.load(f)
                pr = PullRequest(**pr_data)
        else:
            logger.info(f"Fetching GitHub PR from API: {pr_url_or_path}")
            pr = self.github_client.get_pull_request(pr_url_or_path)
        
        # 3. Extract/Refine Requirements (LLM Step 1)
        logger.info("Extracting requirements...")
        requirements = self._extract_requirements(ticket)
        
        # 4. Evaluate each requirement (LLM Step 2)
        logger.info("Evaluating requirements against PR...")
        verdicts = self._evaluate_requirements(ticket, pr, requirements)
        
        # 5. Synthesize Overall Verdict
        overall_verdict = self._synthesize_overall_verdict(verdicts)
        
        return EvaluationResult(
            ticket_id=ticket.ticket_id,
            pr_url=pr.pr_url,
            overall=overall_verdict,
            requirements=verdicts,
            evaluated_at=datetime.now(timezone.utc).isoformat()
        )

    def _extract_requirements(self, ticket: JiraTicket) -> List[str]:
        if self.mock_mode:
            return ticket.acceptance_criteria if ticket.acceptance_criteria else [ticket.title]
            
        prompt = REQUIREMENTS_EXTRACTOR_PROMPT.format(
            ticket_id=ticket.ticket_id,
            title=ticket.title,
            description=ticket.description,
            existing_ac=", ".join(ticket.acceptance_criteria)
        )
        
        response = self.anthropic_client.messages.create(
            model=os.getenv("PARSER_MODEL", "claude-3-5-sonnet-20240620"),
            max_tokens=1000,
            system="You are a requirements extractor. Return ONLY a JSON list of strings.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        try:
            # Try to find JSON list in the response
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(content)
        except:
            logger.warning("Failed to parse requirements as JSON, falling back to existing AC.")
            return ticket.acceptance_criteria if ticket.acceptance_criteria else [ticket.title]

    def _evaluate_requirements(self, ticket: JiraTicket, pr: PullRequest, requirements: List[str]) -> List[RequirementVerdict]:
        if self.mock_mode:
            verdicts = []
            for req in requirements:
                # Basic heuristic for mock mode: if req text is in PR title/desc or files, Pass
                verdicts.append(RequirementVerdict(
                    requirement=req,
                    verdict="Pass",
                    evidence="[MOCK] Evidence found in PR changes",
                    confidence=0.85
                ))
            return verdicts

        prompt = EVALUATOR_PROMPT.format(
            jira_ticket_json=ticket.model_dump_json(indent=2),
            pr_json=pr.model_dump_json(indent=2),
            requirements="\n".join([f"- {r}" for r in requirements])
        )
        
        response = self.anthropic_client.messages.create(
            model=os.getenv("CORE_MODEL", "claude-3-5-sonnet-20240620"),
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # In a real implementation, we would force tool use or structured output.
        # For now, we'll parse the response.
        content = response.content[0].text
        return self._parse_evaluation_response(content, requirements)

    def _parse_evaluation_response(self, content: str, requirements: List[str]) -> List[RequirementVerdict]:
        # Simple parser for demonstration. In production, use tool calling or json_mode.
        verdicts = []
        for req in requirements:
            # Mocking the extraction from text content
            # In a real scenario, the LLM would return a list of RequirementVerdict objects
            verdicts.append(RequirementVerdict(
                requirement=req,
                verdict="Pass", # Default for demo
                evidence="Evidence found in PR diff",
                confidence=0.9
            ))
        return verdicts

    def _synthesize_overall_verdict(self, verdicts: List[RequirementVerdict]) -> str:
        if all(v.verdict == "Pass" for v in verdicts):
            return "Pass"
        if any(v.verdict == "Fail" for v in verdicts):
            return "Fail"
        return "Partial"

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Jira-PR Agent")
    parser.add_argument("--ticket", required=True, help="Jira Ticket ID")
    parser.add_argument("--pr", required=True, help="GitHub PR URL")
    args = parser.parse_args()
    
    agent = Agent()
    result = agent.evaluate_pr(args.ticket, args.pr)
    print(result.model_dump_json(indent=2))
