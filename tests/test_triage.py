import sys
from unittest.mock import MagicMock, patch

# Mock openai dependency before importing triage
sys.modules['openai'] = MagicMock()

from triage import triage_all, has_high_or_critical

@patch('triage.triage_finding')
def test_triage_all(mock_triage_finding):
    mock_triage_finding.side_effect = lambda f: {**f, "triage_status": "mocked"}

    findings = [
        {"file": "a.py", "line_start": 1},
        {"file": "b.py", "line_start": 2}
    ]

    results = triage_all(findings)
    assert len(results) == 2
    assert results[0]["triage_status"] == "mocked"
    assert results[1]["triage_status"] == "mocked"
    assert mock_triage_finding.call_count == 2

def test_has_high_or_critical():
    # Mix of low, medium, false positive, and critical
    findings = [
        {"is_false_positive": False, "risk_level": "low"},
        {"is_false_positive": False, "risk_level": "medium"},
        {"is_false_positive": True, "risk_level": "critical"},  # false positive, so ignored
    ]
    assert not has_high_or_critical(findings)

    findings.append({"is_false_positive": False, "risk_level": "high"})
    assert has_high_or_critical(findings)
