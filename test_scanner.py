import pytest
import sys
from unittest.mock import patch, MagicMock

# Mock dependencies before importing scanner to handle environment without them
sys.modules['semgrep'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['jinja2'] = MagicMock()
sys.modules['openai'] = MagicMock()

from scanner import _find_semgrep

class TestFindSemgrep:
    @patch('shutil.which')
    def test_find_semgrep_in_path(self, mock_which):
        """Test when semgrep is found in the system PATH."""
        mock_which.return_value = '/usr/local/bin/semgrep'

        result = _find_semgrep()

        assert result == '/usr/local/bin/semgrep'
        mock_which.assert_called_once_with('semgrep')

    @patch('shutil.which')
    @patch('pathlib.Path.exists')
    def test_find_semgrep_in_venv(self, mock_exists, mock_which):
        """Test when semgrep is not in PATH but found in venv bin directory."""
        mock_which.return_value = None

        # We need to simulate that candidate.exists() returns True
        # when name == "semgrep" (first iteration)
        def exists_side_effect():
            # In _find_semgrep, it iterates over ("semgrep", "semgrep.exe", "semgrep.cmd")
            # We want it to be true on the first call
            return True
        mock_exists.side_effect = [True]

        result = _find_semgrep()

        assert result.endswith('semgrep')
        assert 'semgrep.exe' not in result
        mock_which.assert_called_once_with('semgrep')
        assert mock_exists.call_count == 1

    @patch('shutil.which')
    @patch('pathlib.Path.exists')
    def test_find_semgrep_windows_exe(self, mock_exists, mock_which):
        """Test when semgrep.exe is found in venv bin directory (Windows)."""
        mock_which.return_value = None

        # False for 'semgrep', True for 'semgrep.exe'
        mock_exists.side_effect = [False, True]

        result = _find_semgrep()

        assert result.endswith('semgrep.exe')
        mock_which.assert_called_once_with('semgrep')
        assert mock_exists.call_count == 2

    @patch('shutil.which')
    @patch('pathlib.Path.exists')
    def test_find_semgrep_windows_cmd(self, mock_exists, mock_which):
        """Test when semgrep.cmd is found in venv bin directory (Windows fallback)."""
        mock_which.return_value = None

        # False for 'semgrep', False for 'semgrep.exe', True for 'semgrep.cmd'
        mock_exists.side_effect = [False, False, True]

        result = _find_semgrep()

        assert result.endswith('semgrep.cmd')
        mock_which.assert_called_once_with('semgrep')
        assert mock_exists.call_count == 3

    @patch('shutil.which')
    @patch('pathlib.Path.exists')
    def test_find_semgrep_not_found(self, mock_exists, mock_which):
        """Test when semgrep is not found anywhere."""
        mock_which.return_value = None

        # Always return False for exists()
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as excinfo:
            _find_semgrep()

        assert "semgrep not found" in str(excinfo.value)
        mock_which.assert_called_once_with('semgrep')
        assert mock_exists.call_count == 3
