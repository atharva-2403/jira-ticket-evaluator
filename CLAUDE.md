# Jira Ticket Evaluator — Claude Code Instructions

## Project Overview

An AI-powered agent system that takes a Jira ticket + a GitHub PR as inputs and
autonomously decides whether the code changes satisfy the stated requirements.
Produces a structured Pass / Partial / Fail verdict with per-requirement evidence.

**Stack:** Python · Anthropic/OpenAI/Gemini APIs · MCP (GitHub + custom Jira) · pytest

---

## Skill Routing

Before starting any task below, read the corresponding SKILL.md file first.
This is non-negotiable — the skills contain patterns that prevent known failure modes.

### Task → Skill mapping

| When you are working on...                        | Read this skill first                                      |
|---------------------------------------------------|------------------------------------------------------------|
| Any Python module (`src/*.py`)                    | `skills/python-patterns/SKILL.md`                         |
| Writing or running tests (`tests/`)               | `skills/python-testing/SKILL.md`                          |
| The agent orchestrator (`src/agent.py`)           | `skills/cost-aware-llm-pipeline/SKILL.md`                 |
| MCP server files (`src/*_mcp_server.py`)          | `skills/api-design/SKILL.md`                              |
| Jira or GitHub API client (`src/*_client.py`)     | `skills/regex-vs-llm-structured-text/SKILL.md`            |
| Structured output / JSON schemas (`src/schemas.py`)| `skills/regex-vs-llm-structured-text/SKILL.md`           |
| Test generator (`src/test_generator.py`)          | `skills/python-testing/SKILL.md` + `skills/tdd-workflow/SKILL.md` |
| CI/CD, Docker, deployment (`Dockerfile`, `.github/`)| `skills/deployment-patterns/SKILL.md`                  |
| Database migrations or state persistence          | `skills/database-migrations/SKILL.md`                     |
| Security review of any file                       | `skills/security-review/SKILL.md`                         |
| Verification / eval loops                         | `skills/verification-loop/SKILL.md`                       |
| README, docs, architecture writeup                | `skills/article-writing/SKILL.md`                         |
| Search for solutions before coding                | `skills/search-first/SKILL.md`                            |

---

## Agent Routing

Delegate to subagents instead of doing everything inline.

| Task                                              | Use this agent                  |
|---------------------------------------------------|---------------------------------|
| Planning a new module or feature                  | `/plan`                         |
| Writing code test-first                           | `/tdd`                          |
| Reviewing `src/` code before committing           | `/code-review`                  |
| Fixing a failing test or import error             | `/build-fix`                    |
| Security audit on MCP configs or `.env` handling  | `/security-scan`                |
| Removing dead code or unused imports              | `/refactor-clean`               |
| Updating README, docstrings, architecture diagram | `/update-docs`                  |
| Running multi-agent parallel tasks                | `/multi-execute`                |

---

## Project Structure

```
jira-ticket-evaluator/
├── CLAUDE.md                  ← you are here
├── README.md
├── .env                       ← never commit
├── .env.example               ← commit this
├── requirements.txt
├── src/
│   ├── jira_client.py         ← Jira REST API wrapper
│   ├── github_client.py       ← GitHub REST/GraphQL wrapper
│   ├── jira_mcp_server.py     ← Custom MCP server exposing Jira tools
│   ├── agent.py               ← Main orchestrator — multi-step agent loop
│   ├── prompts.py             ← All system prompts (never inline)
│   ├── schemas.py             ← Pydantic schemas for verdict output
│   ├── test_generator.py      ← Generates + executes custom tests
│   └── cli.py                 ← CLI entrypoint (--ticket, --pr flags)
├── tests/
│   ├── test_jira_client.py
│   ├── test_github_client.py
│   ├── test_agent.py
│   └── test_schemas.py
├── examples/
│   ├── feature_request.json
│   ├── bug_report.json
│   └── refactor.json
└── docs/
    └── architecture.md
```

---

## Coding Rules

### Always

- Read the relevant skill file before writing any new module (see Skill Routing above)
- Use `python-dotenv` to load env vars — never hardcode keys
- All LLM calls go through `src/agent.py` — no ad-hoc API calls in other files
- Use Pydantic models from `src/schemas.py` for all structured inputs/outputs
- Every new function needs a docstring and type hints
- Write tests before implementation (`/tdd` workflow)
- Run `pytest tests/` before marking any task done

### Never

- Never commit `.env` — only `.env.example`
- Never use `print()` for logging — use Python's `logging` module
- Never hardcode model names as strings outside `src/agent.py`
- Never make Jira or GitHub API calls directly in `src/agent.py` — use the client modules
- Never call LLM APIs without going through MCP tool invocations in the agent loop

### Python style

- Follow `skills/python-patterns/SKILL.md` for all idioms
- Use `pathlib.Path` not `os.path`
- Use `dataclasses` or Pydantic — no plain dicts for structured data
- All API errors must be caught and re-raised with context

---

## Agent Architecture

The evaluation pipeline runs in these steps. Each step maps to a skill.

```
Step 1 — Parse Jira ticket
  → src/jira_client.py fetches raw ticket
  → LLM extracts structured requirements list
  → Skill: regex-vs-llm-structured-text

Step 2 — Fetch PR diff
  → src/github_client.py fetches diff + files changed
  → Skill: api-design (for MCP tool shape)

Step 3 — Match requirements to code (core agent loop)
  → src/agent.py runs multi-step reasoning via MCP tools
  → For each requirement: find evidence in diff, classify Pass/Partial/Fail
  → Skill: cost-aware-llm-pipeline (model routing per step)

Step 4 — Generate and run tests (optional)
  → src/test_generator.py writes pytest test for each criterion
  → Executes via subprocess, captures result
  → Skill: python-testing

Step 5 — Synthesize verdict
  → All evidence + test results → final structured output
  → Validate against src/schemas.py Pydantic model
  → Skill: verification-loop

Step 6 — Output
  → src/cli.py renders readable report
  → JSON dump also available via --json flag
```

---

## Model Routing (by task)

These are the recommended models for each agent step.
Read `skills/cost-aware-llm-pipeline/SKILL.md` before changing any of these.

| Step                          | Model                    | Provider        | Why                              |
|-------------------------------|--------------------------|-----------------|----------------------------------|
| Jira parser                   | `Llama 3.1 8B`           | Groq            | Fast, 14k req/day, simple task   |
| PR diff analysis              | `Gemini 2.5 Flash`       | Google AI Studio| 1M context, cheap, large diffs   |
| Requirements matcher (core)   | `gpt-5`                  | GitHub Models   | Strongest reasoning available    |
| Test generator                | `GPT-4.1`                | GitHub Models   | Best code gen in your list       |
| Verdict synthesizer           | `o4-mini`                | GitHub Models   | Reasoning model, structured out  |
| Output formatter              | `Llama 3.1 8B`           | Cerebras        | Free, instant, formatting only   |

Configure these in `.env`:
```
PARSER_MODEL=llama-3.1-8b
PARSER_PROVIDER=groq
DIFF_MODEL=gemini-2.5-flash
DIFF_PROVIDER=google
CORE_MODEL=gpt-5
CORE_PROVIDER=github
TESTGEN_MODEL=gpt-4.1
TESTGEN_PROVIDER=github
VERDICT_MODEL=o4-mini
VERDICT_PROVIDER=github
FORMATTER_MODEL=llama-3.1-8b
FORMATTER_PROVIDER=cerebras
```

---

## MCP Configuration

Two MCP servers must be running before the agent loop starts.

### 1. GitHub MCP (official)
Provides: `get_pull_request`, `list_pr_files`, `get_file_contents`, `get_commit`

### 2. Custom Jira MCP (`src/jira_mcp_server.py`)
Provides: `get_ticket`, `get_acceptance_criteria`, `get_ticket_type`

The agent must call ALL data retrieval via these MCP tools.
Direct API calls in `src/agent.py` will fail code review.

---

## Verdict Schema

All verdicts must conform to this structure (defined in `src/schemas.py`):

```python
class RequirementVerdict(BaseModel):
    requirement: str          # verbatim from Jira ticket
    verdict: Literal["Pass", "Partial", "Fail"]
    evidence: str             # file path + line number or explanation
    confidence: float         # 0.0 to 1.0

class EvaluationResult(BaseModel):
    ticket_id: str
    pr_url: str
    overall: Literal["Pass", "Partial", "Fail"]
    requirements: list[RequirementVerdict]
    test_results: list[dict] | None
    evaluated_at: str         # ISO 8601
```

---

## Verification Checklist

Run this before every commit. See `skills/verification-loop/SKILL.md` for detail.

```bash
# 1. All tests pass
pytest tests/ -v

# 2. No secrets in code
grep -r "sk-\|ghp_\|AKIA\|api_key\s*=" src/ && echo "SECRET FOUND" || echo "Clean"

# 3. Type check
mypy src/

# 4. Lint
ruff check src/

# 5. End-to-end smoke test
python src/cli.py --ticket examples/feature_request.json --pr examples/feature_pr.json
```

---

## Environment Variables Required

Document all of these in `.env.example` (never the values, only the keys):

```
# Jira
JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=

# GitHub
GITHUB_TOKEN=

# LLM Providers
GROQ_API_KEY=
GOOGLE_AI_API_KEY=
GITHUB_MODELS_TOKEN=
CEREBRAS_API_KEY=

# Model routing (see Model Routing section above)
PARSER_MODEL=
PARSER_PROVIDER=
DIFF_MODEL=
DIFF_PROVIDER=
CORE_MODEL=
CORE_PROVIDER=
TESTGEN_MODEL=
TESTGEN_PROVIDER=
VERDICT_MODEL=
VERDICT_PROVIDER=
FORMATTER_MODEL=
FORMATTER_PROVIDER=
```

---

## Hackathon Judging Criteria → Code Mapping

| Criterion (weight)        | Where it's evaluated in code             | Skill to follow                        |
|---------------------------|------------------------------------------|----------------------------------------|
| Accuracy (30%)            | `src/agent.py` step 3 + 5               | `cost-aware-llm-pipeline`              |
| Agent Design (25%)        | `src/agent.py` full orchestration loop  | `cost-aware-llm-pipeline`              |
| MCP Integration (20%)     | `src/jira_mcp_server.py` + GitHub MCP   | `api-design`                           |
| Test Generation (15%)     | `src/test_generator.py`                 | `python-testing` + `tdd-workflow`      |
| Presentation (10%)        | `README.md` + `docs/architecture.md`    | `article-writing`                      |

Prioritize in this order when short on time: accuracy → agent design → MCP → tests → docs.

---

## Quick Commands

```bash
# Run full evaluation
python src/cli.py --ticket examples/feature_request.json --pr examples/feature_pr.json

# Run with JSON output
python src/cli.py --ticket examples/bug_report.json --pr examples/bug_pr.json --json

# Run all tests
pytest tests/ -v

# Type check
mypy src/

# Lint
ruff check src/
```
