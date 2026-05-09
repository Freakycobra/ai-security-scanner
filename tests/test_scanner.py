import sys
from unittest.mock import MagicMock, patch
import pytest

sys.modules['openai'] = MagicMock()
sys.modules['semgrep'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['jinja2'] = MagicMock()

from scanner import _get_code_context

def test_get_code_context_happy_path(tmp_path):
    # Create a dummy file with 20 lines
    dummy_file = tmp_path / "dummy.py"
    lines = [f"line {i}" for i in range(1, 21)]
    dummy_file.write_text("\n".join(lines) + "\n")

    # Call with finding on line 10
    result = _get_code_context(str(dummy_file), 10, 10)

    # Context lines is 10 by default, so it should read from line 1 to 20
    # The finding is on line 10, so it should have a '>>>' marker

    assert ">>>   10 | line 10" in result
    assert "       9 | line 9" in result
    assert "      11 | line 11" in result

def test_get_code_context_ioerror():
    with patch('builtins.open', side_effect=IOError("Test IO Error")):
        result = _get_code_context("dummy_path.py", 1, 1)
        assert result == ""
