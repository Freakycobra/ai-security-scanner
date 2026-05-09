import sys
from unittest.mock import MagicMock

# Mock dependencies as per environment constraints
sys.modules["openai"] = MagicMock()

from triage import has_high_or_critical

def test_has_high_or_critical_empty_list():
    assert has_high_or_critical([]) is False

def test_has_high_or_critical_low_medium():
    findings = [
        {"risk_level": "low"},
        {"risk_level": "medium"},
    ]
    assert has_high_or_critical(findings) is False

def test_has_high_or_critical_high_critical():
    findings = [
        {"risk_level": "low"},
        {"risk_level": "high"},
    ]
    assert has_high_or_critical(findings) is True

    findings = [
        {"risk_level": "critical"},
    ]
    assert has_high_or_critical(findings) is True

def test_has_high_or_critical_false_positives():
    findings = [
        {"risk_level": "high", "is_false_positive": True},
        {"risk_level": "critical", "is_false_positive": True},
        {"risk_level": "low", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings) is False

def test_has_high_or_critical_case_insensitivity():
    findings = [
        {"risk_level": "HIGH"},
    ]
    assert has_high_or_critical(findings) is True

    findings = [
        {"risk_level": "CrItIcAl"},
    ]
    assert has_high_or_critical(findings) is True

def test_has_high_or_critical_missing_risk_level():
    findings = [
        {"some_other_key": "value"},
    ]
    assert has_high_or_critical(findings) is False
