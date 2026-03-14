import os
import subprocess
import tempfile
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import anthropic

load_dotenv()
logger = logging.getLogger(__name__)

class TestGenerator:
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_and_run_test(self, requirement: str, code_snippet: str) -> Dict[str, Any]:
        """
        Generates a pytest test for a requirement, runs it, and returns the result.
        """
        logger.info(f"Generating test for requirement: {requirement}")
        
        test_code = self._generate_test_code(requirement, code_snippet)
        
        return self._execute_test(test_code)

    def _generate_test_code(self, requirement: str, code_snippet: str) -> str:
        prompt = f"""
        Given the following requirement and code snippet, write a standalone pytest test file.
        The test should verify if the code snippet satisfies the requirement.
        
        Requirement: {requirement}
        
        Code Snippet:
        {code_snippet}
        
        Return ONLY the python code for the test file. Do not include any explanation or markdown formatting.
        Ensure all necessary imports are included. If you need to mock anything, use unittest.mock.
        Assume the code snippet is in a file named 'implementation.py' and import from it if needed, 
        OR just include the snippet in the test file if it's small.
        """
        
        response = self.anthropic_client.messages.create(
            model=os.getenv("TESTGEN_MODEL", "claude-3-5-sonnet-20240620"),
            max_tokens=2000,
            system="You are a test engineer. Return ONLY python code.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip().strip("```python").strip("```")

    def _execute_test(self, test_code: str) -> Dict[str, Any]:
        """
        Executes the generated test code in a temporary file.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file_path = os.path.join(tmpdir, "test_generated.py")
            with open(test_file_path, "w") as f:
                f.write(test_code)
            
            # Create an empty __init__.py to make it a package if needed
            with open(os.path.join(tmpdir, "__init__.py"), "w") as f:
                pass
                
            logger.info(f"Running generated test at {test_file_path}")
            
            try:
                result = subprocess.run(
                    ["pytest", test_file_path, "--json-report", "--json-report-file=/dev/stdout"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Note: pytest-json-report would be useful here, but let's stick to exit code and stdout
                passed = result.returncode == 0
                return {
                    "passed": passed,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "test_code": test_code
                }
            except subprocess.TimeoutExpired:
                return {
                    "passed": False,
                    "error": "Test execution timed out",
                    "test_code": test_code
                }
            except Exception as e:
                return {
                    "passed": False,
                    "error": str(e),
                    "test_code": test_code
                }

if __name__ == "__main__":
    # Example usage
    gen = TestGenerator()
    # Mock data for demonstration
    req = "Function should add two numbers correctly"
    code = "def add(a, b): return a + b"
    # res = gen.generate_and_run_test(req, code)
    # print(res)
    print("TestGenerator initialized.")
