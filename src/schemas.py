from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class RequirementVerdict(BaseModel):
    """Structured verdict for a single requirement."""
    requirement: str = Field(..., description="The text of the acceptance criterion")
    verdict: Literal["Pass", "Partial", "Fail"] = Field(..., description="The compliance status")
    evidence: str = Field(..., description="File path, line numbers, or code snippets proving the verdict")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

class EvaluationResult(BaseModel):
    """The final structured output of the PR evaluation."""
    ticket_id: str = Field(..., description="The Jira ticket key (e.g., PROJ-123)")
    pr_url: str = Field(..., description="The URL of the GitHub Pull Request")
    overall: Literal["Pass", "Partial", "Fail"] = Field(..., description="The overall verdict for the PR")
    requirements: List[RequirementVerdict] = Field(..., description="Detailed verdicts for each requirement")
    test_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results from automated test generation")
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of when the evaluation was performed"
    )
