import sys
from unittest.mock import MagicMock, patch

sys.modules['openai'] = MagicMock()

from triage import triage_all

def test_triage_all_empty():
    assert triage_all([]) == []

@patch('triage.triage_finding')
def test_triage_all_multiple(mock_triage_finding):
    findings = [
        {"file": "file1.py", "line_start": 10},
        {"file": "file2.py", "line_start": 20}
    ]
    mock_triage_finding.side_effect = lambda x: {**x, "triage_status": "mocked"}

    result = triage_all(findings)
    assert len(result) == 2
    assert result[0]["triage_status"] == "mocked"
    assert result[1]["triage_status"] == "mocked"

@patch('triage.triage_finding')
@patch('builtins.print')
def test_triage_all_verbose(mock_print, mock_triage_finding):
    findings = [
        {"file": "file1.py", "line_start": 10}
    ]
    mock_triage_finding.return_value = {"mocked": True}

    triage_all(findings, verbose=True)
    mock_print.assert_called_once_with("  triaging [1/1]: file1.py:10")
