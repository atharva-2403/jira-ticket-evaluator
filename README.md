# Jira Ticket Evaluator

**Jira Ticket Evaluator** is an AI agent system that autonomously decides whether GitHub PR changes satisfy Jira ticket requirements. It leverages the Model Context Protocol (MCP) and multi-model LLM routing to provide high-accuracy code reviews.

## 🚀 Project Overview

Manually verifying that a Pull Request meets all Acceptance Criteria (AC) in a Jira ticket is tedious and error-prone. This tool automates that process by:
1.  Fetching the ticket and PR data using **MCP tools**.
2.  Extracting verifiable requirements from the ticket.
3.  Matching those requirements to specific code evidence in the PR.
4.  Generating and running automated tests to verify compliance.
5.  Providing a structured **Pass / Partial / Fail** verdict.

## 🏗️ Architecture Summary

The system follows a decoupled architecture using MCP:
*   **Agent**: Orchestrates the multi-step reasoning loop.
*   **MCP Servers**: Provide standardized interfaces to Jira and GitHub.
*   **LLM Pipeline**: Routes tasks to specialized models (e.g., GPT-5 for matching, Gemini for diff analysis).

## 🛠️ Setup

1.  **Install Dependencies**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Place your API keys in the root `.env`:
    ```bash
    cp .env.example .env
    ```

3.  **Run Tests**:
    ```bash
    PYTHONPATH=. pytest tests/
    ```

## 📖 Usage

### Standard Run
```bash
python src/cli.py --ticket PROJ-123 --pr https://github.com/owner/repo/pull/1
```

### Run Demo (Mocked)
If you don't have API keys, you can run the pre-configured demo:
```bash
python demo_run.py
```

## 📊 Example Output (from demo_run.py)

```text
  Overall Verdict : ⚠️  PARTIAL
  Ticket          : PROJ-42
  PR              : https://github.com/demo-org/demo-repo/pull/17

  Requirement                                   Verdict   Confidence  
  ----------------------------------------------------------------------
  User can POST to /auth/login with email an... ✅ Pass    97%
  Invalid credentials must return HTTP 401 w... ✅ Pass    95%
  Protected routes must reject requests with... ✅ Pass    93%
  Tokens must expire after 24 hours             ✅ Pass    98%
  Passwords must be hashed using bcrypt befo... ⚠️  Partial 71%

  Evidence Summary:
  ✅ src/auth/login.py line 6 — jwt.encode() called with user.id and 24h expiry
  ✅ src/auth/login.py line 4 — HTTPException(status_code=401) raised on bcrypt mismatch
  ✅ src/auth/middleware.py line 3-4 — Missing token raises HTTP 401
  ✅ src/auth/login.py line 5 — timedelta(hours=24) passed to jwt.encode()
  ⚠️  src/models/user.py stores password_hash column, bcrypt.checkpw() used in login
```

## 📜 License
MIT
