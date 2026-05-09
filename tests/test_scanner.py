import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock dependencies before importing our code
sys.modules['openai'] = MagicMock()
sys.modules['semgrep'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['jinja2'] = MagicMock()

# Now we can import the module we want to test
from scanner import _get_code_context


def test_get_code_context_ioerror():
    """Test that _get_code_context handles IOError by returning an empty string."""
    with patch('builtins.open', side_effect=IOError("Mocked IOError")):
        # We don't need a real file path since open() is mocked
        result = _get_code_context("fake/path/to/file.py", 10, 15)

    assert result == "", "Expected an empty string when an IOError occurs"
