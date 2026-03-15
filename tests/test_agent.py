import pytest
import json
from unittest.mock import patch, MagicMock
from src.agent import run_evaluation
from src.schemas import EvaluationResult

@patch('src.agent.AgentOrchestrator.call_tool')
@patch('anthropic.Anthropic')
def test_run_evaluation_returns_evaluation_result(mock_anthropic, mock_call_tool):
    """Verifies that the orchestrator returns a valid EvaluationResult."""
    # 1. Mock Tools
    mock_call_tool.side_effect = [
        {"title": "T", "description": "D", "acceptance_criteria": ["R1"]}, # get_ticket
        {"title": "PR", "diff": "Diff", "pr_description": "Body"}, # fetch_pr
        {"passed": True, "stdout": "", "stderr": ""} # generate_test
    ]

    # 2. Mock LLM Responses
    mock_client = mock_anthropic.return_value
    mock_msg_extract = MagicMock()
    mock_msg_extract.content = [MagicMock(text='["R1"]')]
    
    mock_msg_match = MagicMock()
    mock_msg_match.content = [MagicMock(text='Evidence for R1')]
    
    mock_msg_synth = MagicMock()
    mock_msg_synth.content = [MagicMock(text=json.dumps({
        "overall": "Pass",
        "requirements": [
            {"requirement": "R1", "verdict": "Pass", "evidence": "E1", "confidence": 0.9}
        ]
    }))]
    
    mock_client.messages.create.side_effect = [mock_msg_extract, mock_msg_match, mock_msg_synth]

    with patch.dict('os.environ', {"ANTHROPIC_API_KEY": "test-key"}):
        result = run_evaluation("PROJ-123", "https://github.com/owner/repo/pull/1")

    assert isinstance(result, EvaluationResult)
    assert result.overall == "Pass"
    assert len(result.requirements) == 1
    assert result.requirements[0].requirement == "R1"

@patch('src.agent.AgentOrchestrator.call_tool')
@patch('anthropic.Anthropic')
def test_partial_verdict_when_criteria_not_met(mock_anthropic, mock_call_tool):
    """Verifies that the agent correctly reports a Partial status."""
    mock_call_tool.side_effect = [
        {"title": "T", "acceptance_criteria": ["R1", "R2"]}, 
        {"title": "PR", "diff": "Diff"},
        {"passed": False, "stdout": "", "stderr": "Failed"} 
    ]

    mock_client = mock_anthropic.return_value
    
    # Mock sequence of responses
    m1 = MagicMock()
    m1.content = [MagicMock(text='["R1", "R2"]')]
    
    m2 = MagicMock()
    m2.content = [MagicMock(text='Evidence...')]
    
    m3 = MagicMock()
    m3.content = [MagicMock(text=json.dumps({
        "overall": "Partial",
        "requirements": [
            {"requirement": "R1", "verdict": "Pass", "evidence": "E1", "confidence": 0.9},
            {"requirement": "R2", "verdict": "Fail", "evidence": "Not found", "confidence": 0.8}
        ]
    }))]
    
    mock_client.messages.create.side_effect = [m1, m2, m3]

    with patch.dict('os.environ', {"ANTHROPIC_API_KEY": "test-key"}):
        result = run_evaluation("PROJ-123", "https://github.com/owner/repo/pull/1")

    assert result.overall == "Partial"
    assert any(r.verdict == "Fail" for r in result.requirements)
