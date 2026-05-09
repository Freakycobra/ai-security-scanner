import sys
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Mock dependencies before importing reporter
jinja2_mock = MagicMock()
sys.modules['jinja2'] = jinja2_mock

rich_mock = MagicMock()
sys.modules['rich'] = rich_mock
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.table'] = MagicMock()
sys.modules['rich.box'] = MagicMock()

import reporter

class TestReporter(unittest.TestCase):

    @patch('reporter.Template')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_html_report_custom_path(self, mock_file, mock_template_class):
        # Setup mocks
        mock_template_instance = MagicMock()
        mock_template_class.return_value = mock_template_instance
        mock_template_instance.render.return_value = "<html>Mocked Report</html>"

        report_data = {"total": 5, "confirmed": 2}
        custom_path = "custom_report.html"

        # Execute
        result_path = reporter.save_html_report(report_data, path=custom_path)

        # Assertions
        mock_template_class.assert_called_once_with(reporter.REPORT_TEMPLATE)
        mock_template_instance.render.assert_called_once_with(**report_data)
        mock_file.assert_called_once_with(custom_path, "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("<html>Mocked Report</html>")
        self.assertEqual(result_path, custom_path)

    @patch('reporter.Template')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_html_report_default_path(self, mock_file, mock_template_class):
        # Setup mocks
        mock_template_instance = MagicMock()
        mock_template_class.return_value = mock_template_instance
        mock_template_instance.render.return_value = "<html>Mocked Report</html>"

        report_data = {"total": 5, "confirmed": 2}

        # Execute
        result_path = reporter.save_html_report(report_data)

        # Assertions
        mock_template_class.assert_called_once_with(reporter.REPORT_TEMPLATE)
        mock_template_instance.render.assert_called_once_with(**report_data)
        mock_file.assert_called_once_with("security_report.html", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("<html>Mocked Report</html>")
        self.assertEqual(result_path, "security_report.html")

if __name__ == '__main__':
    unittest.main()
