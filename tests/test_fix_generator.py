import sys
import os
from unittest.mock import MagicMock, patch

# Set required environment variables before importing anything
os.environ["OPENAI_API_KEY"] = "dummy_key"

# Mock openai module
mock_openai = MagicMock()
sys.modules["openai"] = mock_openai

from fix_generator import generate_fix

def test_generate_fix_false_positive():
    """Test that false positives return early with fix=None."""
    finding = {"is_false_positive": True, "message": "test", "rule_id": "rule-1"}
    result = generate_fix(finding)
    assert result["fix"] is None
    assert result["is_false_positive"] is True

@patch("fix_generator.client")
def test_generate_fix_success(mock_client):
    """Test normal fix generation without markdown blocks."""
    # Setup mock response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "def fixed_func():\n    pass"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    finding = {
        "rule_id": "test-rule",
        "risk_level": "high",
        "message": "test message",
        "context": "def bad_func():\n    pass"
    }

    result = generate_fix(finding)

    assert result["fix"] == "def fixed_func():\n    pass"
    assert "is_false_positive" not in result
    mock_client.chat.completions.create.assert_called_once()

@patch("fix_generator.client")
def test_generate_fix_strips_markdown_blocks(mock_client):
    """Test that markdown code blocks are properly stripped from the response."""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    # Response contains markdown formatting
    mock_choice.message.content = "```python\ndef fixed_func():\n    pass\n```"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    finding = {
        "rule_id": "test-rule",
        "message": "test message",
        "context": "code"
    }

    result = generate_fix(finding)

    # Assert markdown is stripped
    assert result["fix"] == "def fixed_func():\n    pass"

@patch("fix_generator.client")
def test_generate_fix_strips_markdown_blocks_no_closing(mock_client):
    """Test that markdown code blocks are properly stripped even without closing tags."""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    # Response contains markdown formatting
    mock_choice.message.content = "```python\ndef fixed_func():\n    pass"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    finding = {
        "rule_id": "test-rule",
        "message": "test message",
        "context": "code"
    }

    result = generate_fix(finding)

    # Assert markdown is stripped
    assert result["fix"] == "def fixed_func():\n    pass"

@patch("fix_generator.client")
def test_generate_fix_exception(mock_client):
    """Test exception handling during fix generation."""
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    finding = {
        "rule_id": "test-rule",
        "message": "test message",
        "context": "code"
    }

    result = generate_fix(finding)

    assert result["fix"] == "Fix generation failed: API Error"
