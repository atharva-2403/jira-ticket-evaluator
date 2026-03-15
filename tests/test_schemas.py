import pytest
from pydantic import ValidationError
from src.schemas import RequirementVerdict, EvaluationResult

def test_requirement_verdict_valid():
    """Verifies that a valid RequirementVerdict can be instantiated."""
    data = {
        "requirement": "Must have tests",
        "verdict": "Pass",
        "evidence": "tests/test_main.py exists",
        "confidence": 0.95
    }
    verdict = RequirementVerdict(**data)
    assert verdict.requirement == data["requirement"]
    assert verdict.verdict == "Pass"
    assert verdict.confidence == 0.95

def test_evaluation_result_valid():
    """Verifies that a valid EvaluationResult can be instantiated."""
    data = {
        "ticket_id": "PROJ-123",
        "pr_url": "https://github.com/org/repo/pull/1",
        "overall": "Pass",
        "requirements": [
            {
                "requirement": "Requirement 1",
                "verdict": "Pass",
                "evidence": "Line 10",
                "confidence": 1.0
            }
        ]
    }
    result = EvaluationResult(**data)
    assert result.ticket_id == "PROJ-123"
    assert len(result.requirements) == 1
    assert result.overall == "Pass"

def test_invalid_verdict_rejected():
    """Verifies that invalid verdict strings are rejected by Pydantic."""
    with pytest.raises(ValidationError):
        RequirementVerdict(
            requirement="Req",
            verdict="Incomplete",  # Not in Literal["Pass", "Partial", "Fail"]
            evidence="...",
            confidence=0.5
        )

def test_confidence_range_validation():
    """Verifies that confidence must be between 0 and 1."""
    with pytest.raises(ValidationError):
        RequirementVerdict(
            requirement="Req",
            verdict="Pass",
            evidence="...",
            confidence=1.5 # Out of range
        )
