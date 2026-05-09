import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['jinja2'] = MagicMock()

from reporter import build_report

def test_build_report_empty():
    report = build_report([], "target_dir")
    assert report["target"] == "target_dir"
    assert report["total"] == 0
    assert report["confirmed"] == 0
    assert report["counts"] == {"critical": 0, "high": 0, "medium": 0, "low": 0, "false_positive": 0}
    assert report["confirmed_findings"] == []
    assert report["fp_findings"] == []

def test_build_report_mixed_findings():
    findings = [
        {"rule_id": "r1", "is_false_positive": False, "risk_level": "high"},
        {"rule_id": "r2", "is_false_positive": True},
        {"rule_id": "r3", "is_false_positive": False, "risk_level": "low"},
        {"rule_id": "r4", "is_false_positive": False, "risk_level": "high"}
    ]
    report = build_report(findings, "target_dir")
    assert report["total"] == 4
    assert report["confirmed"] == 3
    assert report["counts"]["high"] == 2
    assert report["counts"]["low"] == 1
    assert report["counts"]["false_positive"] == 1
    assert len(report["confirmed_findings"]) == 3
    assert len(report["fp_findings"]) == 1

    # check sorting by risk: high -> low
    assert report["confirmed_findings"][0]["risk_level"] == "high"
    assert report["confirmed_findings"][1]["risk_level"] == "high"
    assert report["confirmed_findings"][2]["risk_level"] == "low"
