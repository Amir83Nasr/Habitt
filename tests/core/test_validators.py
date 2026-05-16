"""Tests for input validators."""

from unittest.mock import patch

import pytest

from habitt.core.jalali_helper import today_shamsi_str
from habitt.core.validators import _zero_pad_time, prompt_shamsi_date, prompt_time


def test_zero_pad_time_normal():
    assert _zero_pad_time("7:9") == "07:09"
    assert _zero_pad_time("12:5") == "12:05"
    assert _zero_pad_time("23:59") == "23:59"


def test_zero_pad_time_invalid():
    with pytest.raises(ValueError):
        _zero_pad_time("abc")


def test_prompt_shamsi_date_default_today(monkeypatch):
    # mock Prompt.ask to return empty string (default) then valid
    with patch("habitt.core.validators.Prompt.ask", return_value=""):
        result = prompt_shamsi_date("Date", default_today=True)
    assert result == today_shamsi_str()


def test_prompt_shamsi_date_valid_input(monkeypatch):
    with patch("habitt.core.validators.Prompt.ask", return_value="1404/01/01"):
        result = prompt_shamsi_date("Date")
    assert result == "1404/01/01"


def test_prompt_time_valid_with_default(monkeypatch):
    with patch("habitt.core.validators.Prompt.ask", return_value=""):
        result = prompt_time("Time", default="12:00")
    assert result == "12:00"


def test_prompt_time_valid_input(monkeypatch):
    with patch("habitt.core.validators.Prompt.ask", return_value="7:5"):
        result = prompt_time("Time")
    assert result == "07:05"


def test_prompt_time_invalid_then_valid(monkeypatch):
    inputs = ["25:00", "8:60", "7:9"]
    with patch("habitt.core.validators.Prompt.ask", side_effect=inputs):
        result = prompt_time("Time")
    assert result == "07:09"
