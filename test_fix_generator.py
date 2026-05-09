import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before importing fix_generator
sys.modules['openai'] = MagicMock()
sys.modules['config'] = MagicMock()

import fix_generator

def test_generate_fixes_empty():
    assert fix_generator.generate_fixes([]) == []

def test_generate_fixes_with_mix():
    findings = [
        {"id": 1, "is_false_positive": False, "file": "a.py", "line_start": 10},
        {"id": 2, "is_false_positive": True, "file": "b.py", "line_start": 20},
        {"id": 3, "is_false_positive": False, "file": "c.py", "line_start": 30},
    ]

    with patch('fix_generator.generate_fix') as mock_generate_fix:
        # Predictable mock output
        def side_effect(finding):
            return {**finding, "fix": "mocked fix"}
        mock_generate_fix.side_effect = side_effect

        result = fix_generator.generate_fixes(findings)

        # Ensure only non-false-positive findings are passed to generate_fix
        assert mock_generate_fix.call_count == 2
        mock_generate_fix.assert_any_call(findings[0])
        mock_generate_fix.assert_any_call(findings[2])

        # Assert result contains processed and skipped findings
        assert len(result) == 3
        # Confirmed findings first
        assert result[0] == {**findings[0], "fix": "mocked fix"}
        assert result[1] == {**findings[2], "fix": "mocked fix"}
        # Skipped findings at the end
        assert result[2] == findings[1]

def test_generate_fixes_verbose():
    findings = [
        {"id": 1, "is_false_positive": False, "file": "a.py", "line_start": 10},
    ]

    with patch('fix_generator.generate_fix', return_value={**findings[0], "fix": "mocked fix"}), \
         patch('builtins.print') as mock_print:

        fix_generator.generate_fixes(findings, verbose=True)

        mock_print.assert_called_once_with("  generating fix [1/1]: a.py:10")
