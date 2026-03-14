# Jira Ticket Evaluator — Gemini CLI Instructions

## Project Overview

An AI-powered agent system that takes a Jira ticket + a GitHub PR as inputs and
autonomously decides whether the code changes satisfy the stated requirements.
Produces a structured Pass / Partial / Fail verdict with per-requirement evidence.

**Stack:** Python · GitHub Models / Groq / Gemini / Cerebras APIs · MCP (GitHub + custom Jira) · pytest

---

## How Skills Work in Gemini CLI

Skills live in `.gemini/skills/` (project-level) or `~/.gemini/skills/` (global).
To invoke a skill, include its name naturally in your prompt:

```
Use python-patterns to write the jira_client module.
Use test-driven-development to build the test suite for the agent.
Use api-design-principles to design the MCP server interface.
```

Skills are NOT automatic — you must reference them by name in the prompt.
The skill routing table below tells you which skill to reference for each task.

---

## Skill Setup (run once before starting)

Install the antigravity-awesome-skills library for Gemini CLI:

```bash
npx antigravity-awesome-skills --gemini
# installs 1,239+ skills into ~/.gemini/skills/
```

Verify:
```bash
test -d ~/.gemini/skills && echo "Skills ready"
```

---

## Skill Routing Table

When giving Gemini CLI a task, always prefix the prompt with the skill reference.

| Task                                              | Skill to invoke                        | Source repo          |
|---------------------------------------------------|----------------------------------------|----------------------|
| Writing any Python module (`src/*.py`)            | `python-patterns`                      | antigravity          |
| Writing or running tests (`tests/`)               | `test-driven-development`              | antigravity          |
| Designing the agent orchestrator (`src/agent.py`) | `ai-agent-patterns`                    | antigravity          |
| LLM API calls, model routing, cost management     | `cost-aware-llm-pipeline`              | ECC (manual copy)    |
| MCP server design (`src/*_mcp_server.py`)         | `api-design-principles`                | antigravity          |
| Jira / GitHub API client (`src/*_client.py`)      | `api-design-principles`                | antigravity          |
| Deciding regex vs LLM for text parsing            | `regex-vs-llm-structured-text`         | ECC (manual copy)    |
| Structured output / JSON schemas (`src/schemas.py`)| `python-patterns`                     | antigravity          |
| Test generator (`src/test_generator.py`)          | `test-driven-development`              | antigravity          |
| Security review of any module                     | `security-auditor`                     | antigravity          |
| CI/CD, Docker, deployment setup                   | `deployment-patterns`                  | ECC (manual copy)    |
| Debugging a failing step                          | `debugging-strategies`                 | antigravity          |
| Planning a new module before writing it           | `brainstorming`                        | antigravity          |
| Architecture decisions                            | `architecture`                         | antigravity          |
| Researching a solution before coding              | `search-first`                         | ECC (manual copy)    |
| Writing README or architecture docs               | `doc-coauthoring`                      | antigravity          |
| Creating a GitHub PR from finished work           | `create-pr`                            | antigravity          |
| Pre-commit quality checks                         | `lint-and-validate`                    | antigravity          |

### ECC skills (manual copy — not in antigravity)

A few skills from `everything-claude-code` are not in the antigravity library.
Copy them manually into your project's `.gemini/skills/` folder:

```bash
# from your everything-claude-code directory
cp -r skills/cost-aware-llm-pipeline   /path/to/jira-ticket-evaluator/.gemini/skills/
cp -r skills/regex-vs-llm-structured-text /path/to/jira-ticket-evaluator/.gemini/skills/
cp -r skills/search-first              /path/to/jira-ticket-evaluator/.gemini/skills/
cp -r skills/deployment-patterns       /path/to/jira-ticket-evaluator/.gemini/skills/
cp -r skills/verification-loop         /path/to/jira-ticket-evaluator/.gemini/skills/
```

---

## Project Structure

```
jira-ticket-evaluator/
├── GEMINI.md                  ← you are here
├── README.md
├── .env                       ← never commit
├── .env.example               ← commit this
├── requirements.txt
├── .gemini/
│   └── skills/                ← project-level skills (ECC overrides)
│       ├── cost-aware-llm-pipeline/SKILL.md
│       ├── regex-vs-llm-structured-text/SKILL.md
│       ├── search-first/SKILL.md
│       ├── deployment-patterns/SKILL.md
│       └── verification-loop/SKILL.md
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

## Example Prompts for Each Phase

Copy-paste these directly into Gemini CLI as you work through the project phases.

### Phase 2 — Jira client
```
Use python-patterns and api-design-principles to write src/jira_client.py.
It should fetch a Jira ticket by ID using the REST API v3 and return
title, description, and acceptance criteria as a structured Pydantic model.
Load credentials from environment variables using python-dotenv.
```

### Phase 3 — GitHub PR client
```
Use python-patterns and api-design-principles to write src/github_client.py.
It should fetch a PR diff, list of changed files, PR description, and commit
messages from the GitHub REST API. Use GITHUB_TOKEN from environment.
```

### Phase 4 — MCP server
```
Use api-design-principles to design src/jira_mcp_server.py.
It should expose three MCP tools: get_ticket, get_acceptance_criteria,
get_ticket_type. Each tool takes a ticket_id string and returns structured data.
```

### Phase 5 — Agent orchestrator
```
Use ai-agent-patterns and cost-aware-llm-pipeline to write src/agent.py.
It must run a multi-step pipeline: parse ticket → fetch PR → match each
requirement to code evidence → synthesize verdict. All data retrieval must
go through MCP tool calls. Output must conform to the EvaluationResult
Pydantic schema in src/schemas.py.
```

### Phase 6 — Test generator
```
Use test-driven-development to write src/test_generator.py.
Given an acceptance criterion string and a code snippet, it should ask
the LLM to write a pytest test, execute it via subprocess, and return
the pass/fail result with stdout/stderr.
```

### Phase 7 — Security check
```
Use security-auditor to review src/jira_client.py, src/github_client.py,
and src/jira_mcp_server.py for: hardcoded secrets, missing input validation,
unsafe subprocess calls, and insecure API patterns.
```

### Phase 9 — README
```
Use doc-coauthoring to write README.md for the jira-ticket-evaluator project.
It must include: setup instructions, architecture overview with a text diagram,
usage guide with example commands, and example input/output.
```

### Pre-commit quality check
```
Use lint-and-validate to check all files in src/ for: unused imports,
missing type hints, missing docstrings, and any print() statements
that should be logging calls.
```

---

## Coding Rules

### Always
- Reference a skill before writing any new module (see routing table above)
- Use `python-dotenv` for all env vars — never hardcode credentials
- All LLM calls go through `src/agent.py` — never ad-hoc API calls elsewhere
- Use Pydantic models from `src/schemas.py` for all structured output
- Every function needs type hints and a docstring
- Follow the `search-first` skill before implementing anything unfamiliar

### Never
- Never commit `.env` — only `.env.example`
- Never use `print()` — use Python's `logging` module
- Never hardcode model names as strings outside `src/agent.py`
- Never call Jira/GitHub APIs directly inside `src/agent.py`
- Never call LLM APIs without going through MCP tool invocations

---

## Model Routing

Each pipeline step uses a different model. Configure in `.env`.

| Step                          | Model                    | Provider        |
|-------------------------------|--------------------------|-----------------|
| Jira parser                   | `llama-3.1-8b`           | Groq            |
| PR diff analysis              | `gemini-2.5-flash`       | Google AI Studio|
| Requirements matcher (core)   | `gpt-5`                  | GitHub Models   |
| Test generator                | `gpt-4.1`                | GitHub Models   |
| Verdict synthesizer           | `o4-mini`                | GitHub Models   |
| Output formatter              | `llama-3.1-8b`           | Cerebras        |

---

## Verdict Schema

All output must conform to this structure (defined in `src/schemas.py`):

```python
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
    test_results: list[dict] | None
    evaluated_at: str       # ISO 8601
```

---

## Verification Checklist

Run before every commit:

```bash
pytest tests/ -v
mypy src/
ruff check src/
grep -r "sk-\|ghp_\|AKIA\|api_key\s*=" src/ && echo "SECRET FOUND" || echo "Clean"
python src/cli.py --ticket examples/feature_request.json --pr examples/feature_pr.json
```

---

## Environment Variables

```
JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
GITHUB_TOKEN=
GROQ_API_KEY=
GOOGLE_AI_API_KEY=
GITHUB_MODELS_TOKEN=
CEREBRAS_API_KEY=
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

## Hackathon Criteria → Skill Coverage

| Criterion (weight)     | File responsible              | Skill to use                     |
|------------------------|-------------------------------|----------------------------------|
| Accuracy (30%)         | `src/agent.py` steps 3 + 5   | `ai-agent-patterns`              |
| Agent Design (25%)     | `src/agent.py` full loop     | `cost-aware-llm-pipeline`        |
| MCP Integration (20%)  | `src/jira_mcp_server.py`     | `api-design-principles`          |
| Test Generation (15%)  | `src/test_generator.py`      | `test-driven-development`        |
| Presentation (10%)     | `README.md` + `docs/`        | `doc-coauthoring`                |
