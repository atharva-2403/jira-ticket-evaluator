# Jira Ticket Evaluator

An AI-powered agent system that autonomously decides whether GitHub PR changes satisfy Jira ticket requirements.

## 🚀 Overview

The **Jira Ticket Evaluator** streamlines the code review process by automatically matching Pull Request changes against Jira Acceptance Criteria. It produces a structured **Pass / Partial / Fail** verdict with per-requirement evidence and confidence scores.

## 🏗️ Architecture

```text
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Jira Cloud  │◄─────┤ Custom MCP Server│◄─────┤  AI Agent    │
└──────────────┘      └──────────────────┘      │(Orchestrator)│
                                                └──────┬───────┘
                                                       │
┌──────────────┐      ┌──────────────────┐             │
│  GitHub API  │◄─────┤ GitHub MCP Server│◄────────────┘
└──────────────┘      └──────────────────┘             │
                                                       │
                                                ┌──────▼───────┐
                                                │  LLM Models  │
                                                │ (Claude/GPT) │
                                                └──────────────┘
```

1.  **Jira MCP Server**: Exposes Jira ticket data as tools.
2.  **GitHub MCP Server**: Exposes PR metadata and diffs as tools.
3.  **Agent Orchestrator**: The multi-step loop that fetches data, extracts requirements, matches evidence, and synthesizes the verdict.
4.  **LLM Pipeline**: Uses cost-aware routing to select the best model for each step.

## 🛠️ Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/jira-ticket-evaluator
    cd jira-ticket-evaluator
    ```

2.  **Install dependencies**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your API keys:
    ```bash
    cp .env.example .env
    ```

## 📖 Usage

### Evaluate a PR against a Jira Ticket
```bash
python src/cli.py --ticket PROJ-123 --pr https://github.com/owner/repo/pull/1
```

### Run with local JSON files (Demo Mode)
```bash
python src/cli.py --ticket examples/feature_request.json --pr examples/feature_pr.json
```

### Options
- `--ticket`: Jira Ticket ID or local path to ticket JSON.
- `--pr`: GitHub PR URL or local path to PR JSON.
- `--json`: Output raw JSON instead of a formatted table.

## 📊 Example Output

```text
Overall Verdict: Partial
Ticket: PROJ-42
PR: https://github.com/demo-org/demo-repo/pull/17

Requirement Evaluation
Requirement                                Verdict   Confidence  Evidence
User can POST to /auth/login ...           Pass      0.97        src/auth/login.py line 6
Invalid credentials return 401 ...         Pass      0.95        src/auth/login.py line 4
Passwords must be hashed ...               Partial   0.71        bcrypt.checkpw used but no hash on reg
```

## 🧪 Testing

Run the test suite:
```bash
PYTHONPATH=. pytest tests/
```

## 📜 License
MIT
