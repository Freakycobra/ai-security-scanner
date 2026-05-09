import sys
from unittest.mock import MagicMock, mock_open, patch

# Mock dependencies before importing the module
sys.modules['jinja2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['rich.box'] = MagicMock()

import reporter

def test_save_json_report_default_path():
    report_data = {"key": "value"}

    with patch("builtins.open", mock_open()) as mocked_open:
        with patch("json.dump") as mocked_json_dump:
            result_path = reporter.save_json_report(report_data)

            mocked_open.assert_called_once_with("security_report.json", "w")
            mocked_json_dump.assert_called_once_with(report_data, mocked_open.return_value, indent=2)
            assert result_path == "security_report.json"

def test_save_json_report_custom_path():
    report_data = {"key": "value"}
    custom_path = "custom_report.json"

    with patch("builtins.open", mock_open()) as mocked_open:
        with patch("json.dump") as mocked_json_dump:
            result_path = reporter.save_json_report(report_data, custom_path)

            mocked_open.assert_called_once_with(custom_path, "w")
            mocked_json_dump.assert_called_once_with(report_data, mocked_open.return_value, indent=2)
            assert result_path == custom_path
