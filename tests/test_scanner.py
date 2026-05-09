import sys
import json
from unittest.mock import patch, MagicMock

from scanner import run_semgrep

@patch('scanner._find_semgrep', return_value='/mock/path/semgrep')
@patch('subprocess.run')
@patch('pathlib.Path.exists', return_value=True)
def test_run_semgrep_success(mock_exists, mock_run, mock_find):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "results": [
                {
                    "path": "test.py",
                    "start": {"line": 10},
                    "end": {"line": 10},
                    "check_id": "rule-1",
                    "extra": {
                        "message": "Found issue",
                        "severity": "WARNING",
                        "lines": "print(1)"
                    }
                }
            ]
        })
    )

    with patch('scanner._get_code_context', return_value=">>>   10 | print(1)"):
        findings = run_semgrep("fake_dir")

    assert len(findings) == 1
    f = findings[0]
    assert f["file"] == "test.py"
    assert f["line_start"] == 10
    assert f["rule_id"] == "rule-1"
    assert f["message"] == "Found issue"
    assert f["severity"] == "warning"
    assert f["context"] == ">>>   10 | print(1)"

@patch('scanner.Path.exists', return_value=False)
def test_run_semgrep_target_not_found(mock_exists):
    try:
        run_semgrep("missing_dir")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
