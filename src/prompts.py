"""
Centralized prompts for the Jira Ticket Evaluator.
"""

TICKET_PARSER_PROMPT = """
Analyze the following Jira ticket data and provide a clean summary.
Extract the core intent, ticket type, and any explicitly stated technical constraints.

Jira Ticket Data:
{ticket_data}
"""

REQUIREMENTS_EXTRACTOR_PROMPT = """
Extract a structured list of acceptance criteria from the Jira ticket.
Ticket ID: {ticket_id}
Title: {title}
Description: {description}

Return a JSON list of strings, where each string is a single verifiable requirement.
"""

CODE_MATCHER_PROMPT = """
You are a senior code reviewer. Match the following requirements to the changes in this Pull Request.

Requirements:
{requirements}

PR Description:
{pr_description}

PR Diff:
{pr_diff}

For each requirement, find the specific code evidence (file paths, functions, or logic changes) that address it.
If a requirement is not addressed, note it as missing.
"""

TEST_GENERATOR_PROMPT = """
Write a standalone pytest test file to verify this specific requirement against the provided code snippet.

Requirement: {criterion}

Code Snippet:
{code_snippet}

Instructions:
1. Use `pytest` and `unittest.mock` if needed.
2. The test must be executable by `pytest`.
3. Return ONLY the Python code. No markdown, no explanation.
"""

VERDICT_SYNTHESIZER_PROMPT = """
Synthesize the final evaluation result based on the evidence collected.

Requirements & Evidence:
{matching_results}

Test Results:
{test_results}

PR Context:
{pr_metadata}

Provide an overall verdict (Pass, Partial, or Fail) and a detailed verdict for each requirement.
Follow the EvaluationResult JSON schema strictly.
"""
