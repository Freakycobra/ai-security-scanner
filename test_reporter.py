import sys
from unittest.mock import MagicMock

# Mock missing dependencies
sys.modules['jinja2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['rich.box'] = MagicMock()

import pytest
from reporter import build_report

def test_build_report_empty():
    report = build_report([], "target_repo")
    assert report["target"] == "target_repo"
    assert report["total"] == 0
    assert report["confirmed"] == 0
    assert report["counts"] == {"critical": 0, "high": 0, "medium": 0, "low": 0, "false_positive": 0}
    assert report["confirmed_findings"] == []
    assert report["fp_findings"] == []

def test_build_report_risk_counts():
    findings = [
        {"id": 1, "is_false_positive": False, "risk_level": "critical"},
        {"id": 2, "is_false_positive": False, "risk_level": "high"},
        {"id": 3, "is_false_positive": False, "risk_level": "high"},
        {"id": 4, "is_false_positive": False, "risk_level": "medium"},
        {"id": 5, "is_false_positive": True, "risk_level": "critical"}, # FP
        {"id": 6, "is_false_positive": False, "risk_level": "low"},
        {"id": 7, "is_false_positive": False, "risk_level": "unknown_risk"}, # Unrecognized level
    ]
    report = build_report(findings, "target_repo")

    assert report["total"] == 7
    assert report["confirmed"] == 6
    assert len(report["fp_findings"]) == 1

    counts = report["counts"]
    assert counts["critical"] == 1
    assert counts["high"] == 2
    assert counts["medium"] == 1
    assert counts["low"] == 1
    assert counts["false_positive"] == 1

def test_build_report_risk_sorting():
    findings = [
        {"id": 1, "is_false_positive": False, "risk_level": "low"},
        {"id": 2, "is_false_positive": False, "risk_level": "critical"},
        {"id": 3, "is_false_positive": False, "risk_level": "medium"},
        {"id": 4, "is_false_positive": False, "risk_level": "high"},
    ]
    report = build_report(findings, "target_repo")

    confirmed = report["confirmed_findings"]
    assert [f["risk_level"] for f in confirmed] == ["critical", "high", "medium", "low"]

def test_build_report_missing_risk_level():
    findings = [
        {"id": 1, "is_false_positive": False}, # Missing risk_level
    ]
    report = build_report(findings, "target_repo")

    assert report["confirmed"] == 1
    assert report["counts"]["low"] == 1
    assert report["confirmed_findings"][0].get("risk_level", "low") == "low"
