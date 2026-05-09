import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['openai'] = MagicMock()
sys.modules['config'] = MagicMock()

from triage import filter_confirmed

def test_filter_confirmed_empty():
    """Test filter_confirmed with an empty list."""
    assert filter_confirmed([]) == []

def test_filter_confirmed_all_confirmed():
    """Test filter_confirmed with findings that are all confirmed (is_false_positive is False)."""
    findings = [
        {"id": 1, "is_false_positive": False},
        {"id": 2, "is_false_positive": False},
    ]
    assert filter_confirmed(findings) == findings

def test_filter_confirmed_all_false_positives():
    """Test filter_confirmed with findings that are all false positives (is_false_positive is True)."""
    findings = [
        {"id": 1, "is_false_positive": True},
        {"id": 2, "is_false_positive": True},
    ]
    assert filter_confirmed(findings) == []

def test_filter_confirmed_mixed():
    """Test filter_confirmed with a mix of confirmed and false positive findings."""
    findings = [
        {"id": 1, "is_false_positive": False},
        {"id": 2, "is_false_positive": True},
        {"id": 3, "is_false_positive": False},
        {"id": 4, "is_false_positive": True},
    ]
    expected = [
        {"id": 1, "is_false_positive": False},
        {"id": 3, "is_false_positive": False},
    ]
    assert filter_confirmed(findings) == expected

def test_filter_confirmed_missing_key():
    """Test filter_confirmed with findings that are missing the is_false_positive key."""
    findings = [
        {"id": 1},  # missing key, should default to False (confirmed)
        {"id": 2, "is_false_positive": True},
        {"id": 3},  # missing key
    ]
    expected = [
        {"id": 1},
        {"id": 3},
    ]
    assert filter_confirmed(findings) == expected
