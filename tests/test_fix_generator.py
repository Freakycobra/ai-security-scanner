import sys
from unittest.mock import MagicMock, patch

# Mock openai dependency before importing fix_generator
sys.modules['openai'] = MagicMock()

from fix_generator import generate_fixes

@patch('fix_generator.generate_fix')
def test_generate_fixes(mock_generate_fix):
    mock_generate_fix.side_effect = lambda f: {**f, "fix": "fixed_code()"}

    findings = [
        {"file": "a.py", "is_false_positive": False},
        {"file": "b.py", "is_false_positive": True},  # should be skipped
        {"file": "c.py", "is_false_positive": False}
    ]

    results = generate_fixes(findings)
    assert len(results) == 3

    # Check that confirmed findings got fixes
    confirmed = [r for r in results if not r.get("is_false_positive")]
    assert len(confirmed) == 2
    assert confirmed[0]["fix"] == "fixed_code()"
    assert confirmed[1]["fix"] == "fixed_code()"

    # Check that false positive was skipped and has no fix
    fp = [r for r in results if r.get("is_false_positive")]
    assert len(fp) == 1
    assert "fix" not in fp[0]

    assert mock_generate_fix.call_count == 2
