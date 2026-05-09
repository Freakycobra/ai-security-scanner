import sys
from unittest.mock import MagicMock

# Mock openai module
sys.modules['openai'] = MagicMock()

import triage

def test_triage_finding_error_handling():
    finding = {
        "rule_id": "test-rule",
        "file": "test.py",
        "line_start": 1,
        "message": "test message",
        "context": "test context",
        "code_snippet": "test code snippet"
    }

    triage.client = MagicMock()
    triage.client.chat.completions.create.side_effect = Exception("API timeout")

    result = triage.triage_finding(finding)

    assert result["rule_id"] == "test-rule"
    assert result["file"] == "test.py"
    assert result["is_false_positive"] is False
    assert result["risk_level"] == "medium"
    assert result["explanation"] == "Triage failed: API timeout"
    assert result["attack_scenario"] == ""
    assert result["triage_status"] == "error"
