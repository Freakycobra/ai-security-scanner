import sys
from unittest.mock import MagicMock

# Mock openai dependency before importing triage
sys.modules['openai'] = MagicMock()

from triage import filter_confirmed

def test_filter_confirmed():
    # Test case 1: Empty list
    assert filter_confirmed([]) == []

    # Test case 2: All false positives
    findings_all_fp = [
        {"id": 1, "is_false_positive": True},
        {"id": 2, "is_false_positive": True}
    ]
    assert filter_confirmed(findings_all_fp) == []

    # Test case 3: All confirmed
    findings_all_confirmed = [
        {"id": 1, "is_false_positive": False},
        {"id": 2, "is_false_positive": False}
    ]
    assert filter_confirmed(findings_all_confirmed) == findings_all_confirmed

    # Test case 4: Mixed including missing key (defaults to False)
    findings_mixed = [
        {"id": 1, "is_false_positive": True},
        {"id": 2, "is_false_positive": False},
        {"id": 3} # Missing key
    ]
    expected_mixed = [
        {"id": 2, "is_false_positive": False},
        {"id": 3}
    ]
    assert filter_confirmed(findings_mixed) == expected_mixed

    # Test case 5: List without 'is_false_positive' keys
    findings_missing = [
        {"id": 1},
        {"id": 2}
    ]
    assert filter_confirmed(findings_missing) == findings_missing
