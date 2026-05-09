import pytest
from datetime import datetime
import re
import sys
from unittest.mock import MagicMock

# Mock missing dependencies
sys.modules['jinja2'] = MagicMock()

from reporter import build_report

def test_build_report_empty():
    findings = []
    target = "my_target_project"
    report = build_report(findings, target)

    assert report["target"] == target
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", report["scan_time"])
    assert report["total"] == 0
    assert report["confirmed"] == 0
    assert report["counts"] == {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "false_positive": 0
    }
    assert report["confirmed_findings"] == []
    assert report["fp_findings"] == []

def test_build_report_counts_and_sorting():
    findings = [
        {"id": 1, "risk_level": "medium", "is_false_positive": False},
        {"id": 2, "risk_level": "high", "is_false_positive": False},
        {"id": 3, "risk_level": "low", "is_false_positive": False},
        {"id": 4, "risk_level": "critical", "is_false_positive": False},
        {"id": 5, "risk_level": "high", "is_false_positive": True},
        {"id": 6, "risk_level": "low", "is_false_positive": True},
        {"id": 7, "risk_level": "unknown", "is_false_positive": False}, # Defaults to low ranking/counts
    ]
    target = "test_project"
    report = build_report(findings, target)

    assert report["target"] == target
    assert report["total"] == 7
    assert report["confirmed"] == 5

    assert report["counts"]["critical"] == 1
    assert report["counts"]["high"] == 1
    assert report["counts"]["medium"] == 1
    assert report["counts"]["low"] == 1 # unknown doesn't get counted as low in dict, it gets skipped by `if level in counts:`
    assert report["counts"]["false_positive"] == 2

    # Check sorting
    confirmed_ids = [f["id"] for f in report["confirmed_findings"]]
    # The sort order should be critical(0), high(1), medium(2), low(3), and unknown defaults to 4
    assert confirmed_ids == [4, 2, 1, 3, 7]

    # Check false positives
    fp_ids = [f["id"] for f in report["fp_findings"]]
    assert set(fp_ids) == {5, 6}

    # Verify original findings list isn't strictly modified or confirmed_findings has all the expected fields
    for f in report["confirmed_findings"]:
        assert not f.get("is_false_positive", False)

    for f in report["fp_findings"]:
        assert f.get("is_false_positive", False)
