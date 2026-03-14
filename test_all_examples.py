import subprocess
import os

def run_example(ticket, pr):
    print(f"\n>>> Running evaluation for {ticket} and {pr}")
    cmd = [
        "PYTHONPATH=.",
        "./venv/bin/python",
        "src/cli.py",
        "--ticket", ticket,
        "--pr", pr
    ]
    # We need to mock the LLM calls. For this script, we'll just check if it runs without error 
    # when using local files, assuming the agent falls back to basic logic if LLM fails 
    # OR we use a real key if available.
    # Since we don't have a real key, it WILL fail unless we mock it in src/agent.py.
    
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

if __name__ == "__main__":
    examples = [
        ("examples/feature_request.json", "examples/feature_pr.json"),
        ("examples/bug_report.json", "examples/bug_pr.json"),
        ("examples/refactor.json", "examples/refactor_pr.json")
    ]
    
    for ticket, pr in examples:
        run_example(ticket, pr)
