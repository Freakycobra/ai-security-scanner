import sys
from unittest.mock import MagicMock, mock_open, patch

# Mock dependencies before importing the module under test
sys.modules['jinja2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['rich.box'] = MagicMock()

import reporter

def test_save_html_report_default_path():
    # Setup
    report_data = {"key1": "value1", "key2": "value2"}
    expected_html = "<html>mocked html</html>"

    mock_template_instance = MagicMock()
    mock_template_instance.render.return_value = expected_html

    with patch("reporter.Template", return_value=mock_template_instance) as mock_template_class, \
         patch("builtins.open", mock_open()) as mock_file:

        # Act
        result = reporter.save_html_report(report_data)

        # Assert
        assert result == "security_report.html"
        mock_template_class.assert_called_once_with(reporter.REPORT_TEMPLATE)
        mock_template_instance.render.assert_called_once_with(**report_data)

        mock_file.assert_called_once_with("security_report.html", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(expected_html)

def test_save_html_report_custom_path():
    # Setup
    report_data = {"test": 123}
    custom_path = "custom/path/report.html"
    expected_html = "<p>custom report</p>"

    mock_template_instance = MagicMock()
    mock_template_instance.render.return_value = expected_html

    with patch("reporter.Template", return_value=mock_template_instance) as mock_template_class, \
         patch("builtins.open", mock_open()) as mock_file:

        # Act
        result = reporter.save_html_report(report_data, custom_path)

        # Assert
        assert result == custom_path
        mock_template_class.assert_called_once_with(reporter.REPORT_TEMPLATE)
        mock_template_instance.render.assert_called_once_with(**report_data)

        mock_file.assert_called_once_with(custom_path, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(expected_html)
