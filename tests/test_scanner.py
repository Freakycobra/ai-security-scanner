import pytest
from unittest.mock import patch
from scanner import _parse_findings

def test_parse_findings_empty():
    """Test with no results."""
    semgrep_output = {}
    result = _parse_findings(semgrep_output, "/dummy/root")
    assert result == []

    semgrep_output = {"results": []}
    result = _parse_findings(semgrep_output, "/dummy/root")
    assert result == []

@patch("scanner._get_code_context")
def test_parse_findings_single_standard(mock_get_context):
    """Test with a single finding containing all standard fields."""
    mock_get_context.return_value = "dummy context line"
    semgrep_output = {
        "results": [
            {
                "path": "src/main.py",
                "start": {"line": 10},
                "end": {"line": 12},
                "check_id": "rule-123",
                "extra": {
                    "message": "Found a bug",
                    "severity": "ERROR",
                    "lines": "buggy_code()"
                }
            }
        ]
    }

    result = _parse_findings(semgrep_output, "/dummy/root")

    assert len(result) == 1
    finding = result[0]
    assert finding["file"] == "src/main.py"
    assert finding["line_start"] == 10
    assert finding["line_end"] == 12
    assert finding["rule_id"] == "rule-123"
    assert finding["message"] == "Found a bug"
    assert finding["severity"] == "error" # Should be lowercased
    assert finding["code_snippet"] == "buggy_code()"
    assert finding["context"] == "dummy context line"

    # Verify mock was called with correct arguments
    mock_get_context.assert_called_once_with("src/main.py", 10, 12)

@patch("scanner._get_code_context")
def test_parse_findings_missing_fields(mock_get_context):
    """Test finding where optional fields are missing to ensure fallback defaults work."""
    mock_get_context.return_value = ""
    semgrep_output = {
        "results": [
            {
                # missing 'path' -> defaults to ""
                # missing 'start' -> defaults to 0
                # missing 'end' -> defaults to start_line (0)
                # missing 'check_id' -> defaults to "unknown"
                # missing 'extra' -> message="", severity="warning", lines=""
            }
        ]
    }

    result = _parse_findings(semgrep_output, "/dummy/root")

    assert len(result) == 1
    finding = result[0]
    assert finding["file"] == ""
    assert finding["line_start"] == 0
    assert finding["line_end"] == 0
    assert finding["rule_id"] == "unknown"
    assert finding["message"] == ""
    assert finding["severity"] == "warning"
    assert finding["code_snippet"] == ""
    assert finding["context"] == ""

@patch("scanner._get_code_context")
def test_parse_findings_multiple(mock_get_context):
    """Test with multiple findings."""
    mock_get_context.return_value = "context"
    semgrep_output = {
        "results": [
            {
                "path": "file1.py",
                "start": {"line": 1},
                "check_id": "rule-1",
            },
            {
                "path": "file2.py",
                "start": {"line": 5},
                "check_id": "rule-2",
            }
        ]
    }

    result = _parse_findings(semgrep_output, "/dummy/root")

    assert len(result) == 2
    assert result[0]["file"] == "file1.py"
    assert result[0]["rule_id"] == "rule-1"
    assert result[1]["file"] == "file2.py"
    assert result[1]["rule_id"] == "rule-2"
