from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class JiraTicket(BaseModel):
    ticket_id: str
    title: str
    description: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    ticket_type: Literal["Story", "Bug", "Task", "Sub-task", "Epic"] = "Story"

class GitHubFile(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    patch: Optional[str] = None

class PullRequest(BaseModel):
    pr_url: str
    title: str
    description: str
    base_branch: str
    head_branch: str
    diff: str
    files: list[GitHubFile]
    commit_messages: list[str]

class RequirementVerdict(BaseModel):
    requirement: str
    verdict: Literal["Pass", "Partial", "Fail"]
    evidence: str           # file path + line number
    confidence: float       # 0.0 to 1.0

class EvaluationResult(BaseModel):
    ticket_id: str
    pr_url: str
    overall: Literal["Pass", "Partial", "Fail"]
    requirements: list[RequirementVerdict]
    test_results: Optional[list[dict]] = None
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
