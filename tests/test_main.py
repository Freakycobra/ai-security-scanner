import pytest
import sys
from unittest.mock import patch, MagicMock
from main import main, parse_args

# Dummy tests will be added in subsequent steps

@patch('main.OPENAI_API_KEY', None)
@patch('sys.argv', ['main.py', '--target', 'test_target'])
def test_main_missing_api_key(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error: OPENAI_API_KEY environment variable is not set." in captured.err

@patch('sys.argv', ['main.py', '--target', 'test_target'])
@patch('main.run_semgrep')
@patch('main.OPENAI_API_KEY', 'dummy')
def test_main_run_semgrep_error(mock_run_semgrep, capsys):
    mock_run_semgrep.side_effect = FileNotFoundError("Semgrep not found")
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Semgrep not found" in captured.err

@patch('sys.argv', ['main.py', '--target', 'test_target'])
@patch('main.run_semgrep')
@patch('main.OPENAI_API_KEY', 'dummy')
def test_main_no_findings(mock_run_semgrep, capsys):
    mock_run_semgrep.return_value = []
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Semgrep found no issues. All clear." in captured.out

@patch('sys.argv', ['main.py', '--target', 'test_target'])
@patch('main.run_semgrep')
@patch('main.triage_all')
@patch('main.generate_fixes')
@patch('main.build_report')
@patch('main.save_json_report')
@patch('main.save_html_report')
@patch('main.print_summary')
@patch('main.has_high_or_critical')
@patch('main.OPENAI_API_KEY', 'dummy')
def test_main_happy_path(mock_has_high_or_critical, mock_print_summary, mock_save_html_report,
                         mock_save_json_report, mock_build_report, mock_generate_fixes,
                         mock_triage_all, mock_run_semgrep, capsys):
    mock_run_semgrep.return_value = [{"id": "vuln1"}]
    mock_triage_all.return_value = [{"id": "vuln1", "is_false_positive": False}]
    mock_generate_fixes.return_value = [{"id": "vuln1", "is_false_positive": False, "fix": "fixed"}]
    mock_build_report.return_value = {"summary": "test_report"}
    mock_save_json_report.return_value = "report.json"
    mock_save_html_report.return_value = "report.html"
    mock_has_high_or_critical.return_value = False

    main()

    mock_run_semgrep.assert_called_once_with('test_target', config='auto')
    mock_triage_all.assert_called_once_with([{"id": "vuln1"}], verbose=False)
    mock_generate_fixes.assert_called_once_with([{"id": "vuln1", "is_false_positive": False}], verbose=False)
    mock_build_report.assert_called_once_with([{"id": "vuln1", "is_false_positive": False, "fix": "fixed"}], target='test_target')
    mock_save_json_report.assert_called_once_with({"summary": "test_report"}, "security_report.json")
    mock_save_html_report.assert_called_once_with({"summary": "test_report"}, "security_report.html")
    mock_print_summary.assert_called_once_with({"summary": "test_report"})

@patch('sys.argv', ['main.py', '--target', 'test_target', '--no-fix'])
@patch('main.run_semgrep')
@patch('main.triage_all')
@patch('main.generate_fixes')
@patch('main.build_report')
@patch('main.save_json_report')
@patch('main.save_html_report')
@patch('main.print_summary')
@patch('main.has_high_or_critical')
@patch('main.OPENAI_API_KEY', 'dummy')
def test_main_no_fix(mock_has_high_or_critical, mock_print_summary, mock_save_html_report,
                     mock_save_json_report, mock_build_report, mock_generate_fixes,
                     mock_triage_all, mock_run_semgrep, capsys):
    mock_run_semgrep.return_value = [{"id": "vuln1"}]
    mock_triage_all.return_value = [{"id": "vuln1", "is_false_positive": False}]
    mock_build_report.return_value = {"summary": "test_report"}

    main()

    mock_generate_fixes.assert_not_called()
    mock_build_report.assert_called_once_with([{"id": "vuln1", "is_false_positive": False}], target='test_target')

@patch('sys.argv', ['main.py', '--target', 'test_target', '--fail-on-findings'])
@patch('main.run_semgrep')
@patch('main.triage_all')
@patch('main.generate_fixes')
@patch('main.build_report')
@patch('main.save_json_report')
@patch('main.save_html_report')
@patch('main.print_summary')
@patch('main.has_high_or_critical')
@patch('main.OPENAI_API_KEY', 'dummy')
def test_main_fail_on_findings(mock_has_high_or_critical, mock_print_summary, mock_save_html_report,
                               mock_save_json_report, mock_build_report, mock_generate_fixes,
                               mock_triage_all, mock_run_semgrep, capsys):
    mock_run_semgrep.return_value = [{"id": "vuln1"}]
    mock_triage_all.return_value = [{"id": "vuln1", "is_false_positive": False}]
    mock_has_high_or_critical.return_value = True

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    mock_has_high_or_critical.assert_called_once()
