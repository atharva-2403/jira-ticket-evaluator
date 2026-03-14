"""
Jira Ticket Evaluator - Demo Run (Mocked)
Produces realistic output without requiring any API keys.
"""

import json
from datetime import datetime

# ── Mocked Jira Ticket ──────────────────────────────────────────────────────
MOCK_TICKET = {
    "id": "PROJ-42",
    "type": "feature_request",
    "title": "Add user authentication with JWT tokens",
    "description": "Implement a secure login system using JWT-based authentication so users can log in and access protected routes.",
    "acceptance_criteria": [
        "User can POST to /auth/login with email and password and receive a JWT token",
        "Invalid credentials must return HTTP 401 with an error message",
        "Protected routes must reject requests without a valid JWT token",
        "Tokens must expire after 24 hours",
        "Passwords must be hashed using bcrypt before storage"
    ]
}

# ── Mocked GitHub PR ─────────────────────────────────────────────────────────
MOCK_PR = {
    "url": "https://github.com/demo-org/demo-repo/pull/17",
    "title": "feat: implement JWT authentication",
    "description": "Adds login endpoint, JWT generation, bcrypt hashing, and middleware for protected routes.",
    "files_changed": [
        "src/auth/login.py",
        "src/auth/middleware.py",
        "src/models/user.py",
        "tests/test_auth.py"
    ],
    "diff_summary": {
        "src/auth/login.py": [
            "+ def login(email, password):",
            "+     user = db.get_user(email)",
            "+     if not bcrypt.checkpw(password, user.password_hash):",
            "+         raise HTTPException(status_code=401, detail='Invalid credentials')",
            "+     token = jwt.encode({'sub': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)}, SECRET_KEY)",
            "+     return {'token': token}"
        ],
        "src/auth/middleware.py": [
            "+ def require_auth(request):",
            "+     token = request.headers.get('Authorization', '').replace('Bearer ', '')",
            "+     if not token:",
            "+         raise HTTPException(status_code=401, detail='Missing token')",
            "+     payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])",
            "+     return payload"
        ],
        "src/models/user.py": [
            "+ password_hash = Column(String)  # bcrypt hash stored"
        ],
        "tests/test_auth.py": [
            "+ def test_login_success(): ...",
            "+ def test_login_invalid_credentials(): ...",
            "+ def test_protected_route_no_token(): ..."
        ]
    }
}

# ── Mocked Agent Evaluation ──────────────────────────────────────────────────
def mock_evaluate(ticket, pr):
    print("\n" + "="*60)
    print("  JIRA TICKET EVALUATOR — DEMO RUN")
    print("="*60)
    print(f"\n📋 Ticket  : {ticket['id']} — {ticket['title']}")
    print(f"🔀 PR      : {pr['url']}")
    print(f"📁 Files   : {', '.join(pr['files_changed'])}")
    print(f"🕐 Run at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n── Step 1: Parsing Jira ticket ──────────────────────────")
    print(f"  Model    : llama-3.1-8b (Groq)")
    print(f"  Extracted: {len(ticket['acceptance_criteria'])} acceptance criteria")
    for i, ac in enumerate(ticket['acceptance_criteria'], 1):
        print(f"  [{i}] {ac}")

    print("\n── Step 2: Fetching PR diff ─────────────────────────────")
    print(f"  Model    : gemini-2.5-flash (Google)")
    print(f"  Files    : {len(pr['files_changed'])} changed")
    for f in pr['files_changed']:
        print(f"  + {f}")

    print("\n── Step 3: Matching requirements to code ────────────────")
    print(f"  Model    : gpt-5 (GitHub Models)")

    verdicts = [
        {
            "requirement": "User can POST to /auth/login with email and password and receive a JWT token",
            "verdict": "Pass",
            "evidence": "src/auth/login.py line 6 — jwt.encode() called with user.id and 24h expiry",
            "confidence": 0.97
        },
        {
            "requirement": "Invalid credentials must return HTTP 401 with an error message",
            "verdict": "Pass",
            "evidence": "src/auth/login.py line 4 — HTTPException(status_code=401) raised on bcrypt mismatch",
            "confidence": 0.95
        },
        {
            "requirement": "Protected routes must reject requests without a valid JWT token",
            "verdict": "Pass",
            "evidence": "src/auth/middleware.py line 3-4 — Missing token raises HTTP 401",
            "confidence": 0.93
        },
        {
            "requirement": "Tokens must expire after 24 hours",
            "verdict": "Pass",
            "evidence": "src/auth/login.py line 5 — timedelta(hours=24) passed to jwt.encode()",
            "confidence": 0.98
        },
        {
            "requirement": "Passwords must be hashed using bcrypt before storage",
            "verdict": "Partial",
            "evidence": "src/models/user.py stores password_hash column, bcrypt.checkpw() used in login — but no evidence of hashing on registration in this PR",
            "confidence": 0.71
        }
    ]

    print("\n── Step 4: Generating tests ─────────────────────────────")
    print(f"  Model    : gpt-4.1 (GitHub Models)")
    test_results = [
        {"test": "test_login_returns_jwt_token",        "result": "PASSED"},
        {"test": "test_invalid_password_returns_401",   "result": "PASSED"},
        {"test": "test_missing_token_rejected",         "result": "PASSED"},
        {"test": "test_token_expiry_set_to_24h",        "result": "PASSED"},
        {"test": "test_bcrypt_hash_on_registration",    "result": "FAILED — register endpoint not in PR scope"},
    ]
    for t in test_results:
        icon = "✓" if "PASSED" in t["result"] else "✗"
        print(f"  {icon} {t['test']}: {t['result']}")

    print("\n── Step 5: Synthesizing verdict ─────────────────────────")
    print(f"  Model    : o4-mini (GitHub Models)")

    print("\n" + "="*60)
    print("  EVALUATION RESULT")
    print("="*60)
    print(f"\n  Overall Verdict : ⚠️  PARTIAL")
    print(f"  Ticket          : {ticket['id']}")
    print(f"  PR              : {pr['url']}")
    print()

    col1, col2, col3 = 45, 9, 12
    header = f"  {'Requirement':<{col1}} {'Verdict':<{col2}} {'Confidence':<{col3}}"
    print(header)
    print("  " + "-" * (col1 + col2 + col3 + 4))

    for v in verdicts:
        icon = "✅" if v["verdict"] == "Pass" else "⚠️ "
        req = v["requirement"][:42] + "..." if len(v["requirement"]) > 42 else v["requirement"]
        print(f"  {req:<{col1}} {icon} {v['verdict']:<{col2-2}} {v['confidence']*100:.0f}%")

    print()
    print("  Evidence Summary:")
    for v in verdicts:
        icon = "✅" if v["verdict"] == "Pass" else "⚠️ "
        print(f"  {icon} {v['evidence']}")

    print()
    print("  Test Results: 4/5 passed")
    print("  Note: bcrypt hashing on registration not covered in this PR.")
    print("        Recommend follow-up ticket for registration endpoint.")
    print()
    print("="*60)

    result = {
        "ticket_id": ticket["id"],
        "pr_url": pr["url"],
        "overall": "Partial",
        "requirements": verdicts,
        "test_results": test_results,
        "evaluated_at": datetime.now().isoformat()
    }

    with open("demo_output.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n✅ Full JSON output saved to demo_output.json")
    print("✅ Demo run complete. Ready for presentation.\n")

if __name__ == "__main__":
    mock_evaluate(MOCK_TICKET, MOCK_PR)
