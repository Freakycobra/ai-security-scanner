import sys
from unittest.mock import MagicMock, patch

# Mock openai before importing the module to avoid ModuleNotFoundError
sys.modules["openai"] = MagicMock()
import config
config.OPENAI_API_KEY = "test_key"
import fix_generator

def test_generate_fixes_empty_list():
    """Test generate_fixes with an empty list."""
    findings = []
    result = fix_generator.generate_fixes(findings)
    assert result == []

@patch("fix_generator.generate_fix")
def test_generate_fixes_only_true_positives(mock_generate_fix):
    """Test generate_fixes with a list of only true positive findings."""
    mock_generate_fix.side_effect = lambda f: {**f, "fix": "fixed code"}

    findings = [
        {"id": 1, "is_false_positive": False, "file": "file1.py", "line_start": 1},
        {"id": 2, "is_false_positive": False, "file": "file2.py", "line_start": 2},
    ]

    result = fix_generator.generate_fixes(findings, verbose=False)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["fix"] == "fixed code"
    assert result[1]["id"] == 2
    assert result[1]["fix"] == "fixed code"
    assert mock_generate_fix.call_count == 2

@patch("fix_generator.generate_fix")
def test_generate_fixes_only_false_positives(mock_generate_fix):
    """Test generate_fixes with a list of only false positive findings."""
    findings = [
        {"id": 1, "is_false_positive": True},
        {"id": 2, "is_false_positive": True},
    ]

    result = fix_generator.generate_fixes(findings, verbose=False)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert "fix" not in result[0]  # False positives bypass generate_fix completely
    assert result[1]["id"] == 2
    assert mock_generate_fix.call_count == 0

@patch("fix_generator.generate_fix")
def test_generate_fixes_mixed_findings(mock_generate_fix):
    """Test generate_fixes with a mix of true and false positives."""
    mock_generate_fix.side_effect = lambda f: {**f, "fix": "fixed code"}

    findings = [
        {"id": 1, "is_false_positive": False, "file": "file1.py", "line_start": 1},
        {"id": 2, "is_false_positive": True},
        {"id": 3, "is_false_positive": False, "file": "file3.py", "line_start": 3},
    ]

    result = fix_generator.generate_fixes(findings, verbose=True)

    assert len(result) == 3
    # Note: the result order changes! `generate_fixes` appends skipped ones at the end.

    # First the confirmed ones (id 1 and 3)
    assert result[0]["id"] == 1
    assert result[0]["fix"] == "fixed code"
    assert result[1]["id"] == 3
    assert result[1]["fix"] == "fixed code"

    # Then the false positive ones (id 2)
    assert result[2]["id"] == 2
    assert "fix" not in result[2]

    assert mock_generate_fix.call_count == 2
