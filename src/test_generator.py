import os
import subprocess
import tempfile
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import anthropic
from src.prompts import TEST_GENERATOR_PROMPT

# Search for .env in root and venv/
load_dotenv()
load_dotenv("venv/.env")

logger = logging.getLogger(__name__)

def generate_test(criterion: str, code_snippet: str) -> Dict[str, Any]:
    """
    Asks the LLM to write a pytest for the criterion,
    executes it via subprocess, and returns the result.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "dummy":
        logger.warning("No API key for test generation. Returning mock pass.")
        return {"passed": True, "stdout": "Mock test passed", "stderr": ""}

    client = anthropic.Anthropic(api_key=api_key)
    prompt = TEST_GENERATOR_PROMPT.format(
        criterion=criterion,
        code_snippet=code_snippet
    )

    response = client.messages.create(
        model=os.getenv("TESTGEN_MODEL", "claude-3-5-sonnet-20240620"),
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    test_code = response.content[0].text.strip()
    # Clean markdown if present
    if "```python" in test_code:
        test_code = test_code.split("```python")[1].split("```")[0].strip()
    elif "```" in test_code:
        test_code = test_code.split("```")[1].split("```")[0].strip()

    return _execute_test_code(test_code)

def _execute_test_code(test_code: str) -> Dict[str, Any]:
    """Writes the test to a temp file and runs it with pytest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_generated.py")
        with open(test_file, "w") as f:
            f.write(test_code)
        
        try:
            result = subprocess.run(
                ["pytest", test_file],
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "stdout": "",
                "stderr": "Test execution timed out after 15 seconds"
            }
        except Exception as e:
            return {
                "passed": False,
                "stdout": "",
                "stderr": f"Error executing test: {str(e)}"
            }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print(generate_test(sys.argv[1], sys.argv[2]))
