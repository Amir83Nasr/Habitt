"""Tests for notify module."""

from unittest.mock import MagicMock, patch

from habitt.core.notify import send_message


@patch("habitt.core.notify.load_notify_config")
def test_send_message_disabled(mock_config):
    mock_config.return_value = {"enabled": False}
    assert send_message("test") is False


@patch("habitt.core.notify.load_notify_config")
def test_send_message_missing_token(mock_config):
    mock_config.return_value = {"enabled": True, "bot_token": "", "chat_id": ""}
    assert send_message("test") is False


@patch("habitt.core.notify.load_notify_config")
@patch("habitt.core.notify.requests.post")  # اکنون requests در سطح ماژول وجود دارد
def test_send_message_success(mock_post, mock_config):
    mock_config.return_value = {
        "enabled": True,
        "bot_token": "test_token",
        "chat_id": "@test",
        "api_url": "https://uniom.ir/bot{token}/sendMessage",
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    assert send_message("Hello") is True
