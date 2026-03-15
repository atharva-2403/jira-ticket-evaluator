# Architecture: Jira Ticket Evaluator

## Pipeline Diagram

```text
User Input (--ticket, --pr)
      │
      ▼
┌───────────────┐      ┌──────────────────┐      ┌────────────────┐
│   CLI Layer   │◄────►│ Agent Orchestrator│◄────►│   LLM Models   │
└───────┬───────┘      └────────┬─────────┘      └────────────────┘
        │                       │                        ▲
        │              ┌────────┴─────────┐              │
        │              │   MCP Client     │              │
        │              └────────┬─────────┘              │
        │                       │                        │
        │              ┌────────┴─────────┐              │
        │              │   MCP Servers    │              │
        │              │ (Jira / GitHub)  │              │
        │              └────────┬─────────┘              │
        │                       │                        │
        ▼                       ▼                        │
┌───────────────┐      ┌──────────────────┐              │
│ Final Verdict │◄─────┤  Result Parser   │◄─────────────┘
└───────────────┘      └──────────────────┘
```

## Step-by-Step Process

1.  **Data Ingestion**: The CLI captures the Jira Ticket ID and GitHub PR URL.
2.  **Orchestration**: The `AgentOrchestrator` triggers a multi-step loop.
3.  **Jira Parsing**:
    *   **Tool**: `get_ticket` via Jira MCP Server.
    *   **Model**: `llama-3.1-8b` (Parser).
    *   **Action**: Extracts acceptance criteria and technical requirements from the ticket.
4.  **PR Analysis**:
    *   **Tool**: `fetch_pr` via GitHub MCP Server.
    *   **Model**: `gemini-2.5-flash` (Diff Analyzer).
    *   **Action**: Analyzes the diff, files changed, and commit messages.
5.  **Requirement Matching**:
    *   **Model**: `gpt-5` (Core Matcher).
    *   **Action**: Matches each extracted requirement to specific code evidence found in the PR.
6.  **Automated Testing**:
    *   **Model**: `gpt-4.1` (Test Generator).
    *   **Action**: Generates a `pytest` file for the most critical requirement and executes it.
7.  **Verdict Synthesis**:
    *   **Model**: `o4-mini` (Synthesizer).
    *   **Action**: Combines evidence and test results into a structured `EvaluationResult`.

## MCP Integration

This project leverages the **Model Context Protocol (MCP)** to decouple data retrieval from agent logic.

*   **Custom Jira Server**: Implemented in `src/jira_mcp_server.py`. It wraps the Atlassian REST API and exposes tools like `get_ticket` and `get_acceptance_criteria`.
*   **Decoupling**: The Agent never calls the Jira API directly; it interacts solely through MCP tool invocations, ensuring the system can easily swap data sources (e.g., switching from Jira to Linear).
