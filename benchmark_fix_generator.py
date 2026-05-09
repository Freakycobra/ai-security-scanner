import time
from fix_generator import generate_fixes
import fix_generator
from unittest.mock import patch

def mock_generate_fix(finding):
    time.sleep(0.5)
    return {**finding, "fix": "mocked fix"}

def run_benchmark():
    findings = [
        {"file": f"test{i}.py", "line_start": i, "is_false_positive": False}
        for i in range(1, 11)
    ]

    with patch('fix_generator.generate_fix', side_effect=mock_generate_fix):
        start = time.time()
        generate_fixes(findings, verbose=True)
        end = time.time()

    print(f"Time taken: {end - start:.2f} seconds")

if __name__ == "__main__":
    run_benchmark()
