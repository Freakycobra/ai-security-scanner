import pytest
import json
from unittest.mock import patch, MagicMock
from scanner import run_semgrep

@patch("scanner.Path.exists")
@patch("scanner._find_semgrep")
@patch("scanner.subprocess.run")
@patch("scanner._parse_findings")
def test_run_semgrep_success(mock_parse_findings, mock_run, mock_find_semgrep, mock_exists):
    """Test successful execution of run_semgrep."""
    mock_exists.return_value = True
    mock_find_semgrep.return_value = "/mock/semgrep"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = '{"results": []}'
    mock_run.return_value = mock_result

    expected_findings = [{"rule_id": "test_rule"}]
    mock_parse_findings.return_value = expected_findings

    findings = run_semgrep("/dummy/target")

    assert findings == expected_findings
    mock_run.assert_called_once()

    # We can't strictly assert the path string value easily with MagicMock resolving,
    # so we just assert it was called.
    assert mock_parse_findings.call_count == 1

@patch("scanner.Path.exists")
@patch("scanner._find_semgrep")
@patch("scanner.subprocess.run")
def test_run_semgrep_success_full(mock_run, mock_find_semgrep, mock_exists):
    """Test successful execution of run_semgrep parsing raw json."""
    mock_exists.return_value = True
    mock_find_semgrep.return_value = "/mock/semgrep"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({
        "results": [
            {
                "path": "test.py",
                "start": {"line": 1},
                "check_id": "test-rule",
                "extra": {"message": "Test issue"}
            }
        ]
    })
    mock_run.return_value = mock_result

    # Also need to mock _get_code_context to avoid file reads during tests
    with patch("scanner._get_code_context", return_value="test context"):
        findings = run_semgrep("/dummy/target")

        assert len(findings) == 1
        assert findings[0]["file"] == "test.py"
        assert findings[0]["rule_id"] == "test-rule"
        assert findings[0]["message"] == "Test issue"
        assert findings[0]["context"] == "test context"

@patch("scanner.Path.exists")
def test_run_semgrep_target_not_found(mock_exists):
    """Test when the target path does not exist."""
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError, match="Target path does not exist"):
        run_semgrep("/nonexistent/target")

@patch("scanner.Path.exists")
@patch("scanner._find_semgrep")
@patch("scanner.subprocess.run")
def test_run_semgrep_run_failure(mock_run, mock_find_semgrep, mock_exists):
    """Test when semgrep executable returns a failure code (e.g. 2)."""
    mock_exists.return_value = True
    mock_find_semgrep.return_value = "/mock/semgrep"

    mock_result = MagicMock()
    mock_result.returncode = 2
    mock_result.stderr = "Some semgrep error"
    mock_run.return_value = mock_result

    with pytest.raises(RuntimeError, match="Semgrep failed"):
        run_semgrep("/dummy/target")

@patch("scanner.Path.exists")
@patch("scanner._find_semgrep")
@patch("scanner.subprocess.run")
def test_run_semgrep_invalid_json(mock_run, mock_find_semgrep, mock_exists):
    """Test when semgrep returns invalid JSON."""
    mock_exists.return_value = True
    mock_find_semgrep.return_value = "/mock/semgrep"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "This is not valid JSON"
    mock_run.return_value = mock_result

    with pytest.raises(RuntimeError, match="Could not parse semgrep output"):
        run_semgrep("/dummy/target")
