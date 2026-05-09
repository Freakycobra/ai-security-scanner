import os
import pytest
from unittest.mock import patch, mock_open

# Mocking external modules in sys.modules is recommended if needed, but scanner.py only uses standard libraries and config.py
from scanner import _get_code_context
import config

def test_get_code_context_normal(tmp_path):
    f = tmp_path / "test.txt"
    # 20 lines
    lines = [f"line {i}\n" for i in range(1, 21)]
    f.write_text("".join(lines))

    # set context lines to 2 for easier testing
    with patch("scanner.CONTEXT_LINES", 2):
        res = _get_code_context(str(f), 5, 5)
        # Context start = max(0, 5 - 2 - 1) = 2. So lines[2:5+2] -> lines[2:7]
        # lines[2] is line 3, lines[6] is line 7
        expected_lines = [
            "       3 | line 3",
            "       4 | line 4",
            ">>>    5 | line 5",
            "       6 | line 6",
            "       7 | line 7"
        ]
        assert res == "\n".join(expected_lines)

def test_get_code_context_start_of_file(tmp_path):
    f = tmp_path / "test.txt"
    lines = [f"line {i}\n" for i in range(1, 10)]
    f.write_text("".join(lines))

    with patch("scanner.CONTEXT_LINES", 2):
        res = _get_code_context(str(f), 1, 2)
        # context start = max(0, 1 - 2 - 1) = 0
        # context end = min(9, 2 + 2) = 4
        expected_lines = [
            ">>>    1 | line 1",
            ">>>    2 | line 2",
            "       3 | line 3",
            "       4 | line 4"
        ]
        assert res == "\n".join(expected_lines)

def test_get_code_context_end_of_file(tmp_path):
    f = tmp_path / "test.txt"
    lines = [f"line {i}\n" for i in range(1, 6)]
    f.write_text("".join(lines))

    with patch("scanner.CONTEXT_LINES", 2):
        res = _get_code_context(str(f), 5, 5)
        expected_lines = [
            "       3 | line 3",
            "       4 | line 4",
            ">>>    5 | line 5"
        ]
        assert res == "\n".join(expected_lines)

def test_get_code_context_file_not_found():
    res = _get_code_context("nonexistent_file.py", 1, 1)
    assert res == ""

def test_get_code_context_out_of_bounds(tmp_path):
    f = tmp_path / "test.txt"
    lines = [f"line {i}\n" for i in range(1, 3)]
    f.write_text("".join(lines))

    with patch("scanner.CONTEXT_LINES", 2):
        res = _get_code_context(str(f), 10, 12)
        assert res == ""

def test_get_code_context_empty_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("")

    with patch("scanner.CONTEXT_LINES", 2):
        res = _get_code_context(str(f), 1, 1)
        assert res == ""
