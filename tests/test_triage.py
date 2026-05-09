import sys
from unittest.mock import MagicMock

# Mock dependencies before importing project modules
sys.modules['openai'] = MagicMock()

from triage import has_high_or_critical


def test_has_high_or_critical_empty_list():
    assert has_high_or_critical([]) is False


def test_has_high_or_critical_no_failing():
    findings = [
        {"risk_level": "low", "is_false_positive": False},
        {"risk_level": "medium", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings) is False


def test_has_high_or_critical_confirmed_high():
    findings = [
        {"risk_level": "low", "is_false_positive": False},
        {"risk_level": "high", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings) is True


def test_has_high_or_critical_confirmed_critical():
    findings = [
        {"risk_level": "critical", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings) is True


def test_has_high_or_critical_false_positive_high():
    findings = [
        {"risk_level": "high", "is_false_positive": True},
    ]
    assert has_high_or_critical(findings) is False


def test_has_high_or_critical_mixed():
    findings = [
        {"risk_level": "high", "is_false_positive": True},
        {"risk_level": "low", "is_false_positive": False},
        {"risk_level": "critical", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings) is True


def test_has_high_or_critical_case_insensitive():
    findings = [
        {"risk_level": "HIGH", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings) is True

    findings2 = [
        {"risk_level": "CrItIcAl", "is_false_positive": False},
    ]
    assert has_high_or_critical(findings2) is True


def test_has_high_or_critical_missing_keys():
    findings = [
        {"is_false_positive": False}, # missing risk_level
        {"risk_level": "high"}, # missing is_false_positive
    ]
    assert has_high_or_critical(findings) is True
