"""Tests for Activity model."""

from habitt.tracker.models import Activity


def test_create_activity():
    a = Activity(
        title="Run", start_time="1404/08/25 10:00:00", end_time="1404/08/25 10:30:00"
    )
    assert a.title == "Run"
    assert a.date == "1404/08/25"
    assert a.id == ""


def test_to_dict():
    a = Activity(
        title="Run",
        start_time="1404/08/25 10:00:00",
        end_time="1404/08/25 10:30:00",
        id="abc",
    )
    d = a.to_dict()
    assert d["title"] == "Run"
    assert d["id"] == "abc"


def test_from_dict():
    data = {
        "id": "xyz",
        "title": "Walk",
        "start_time": "1404/08/25 11:00:00",
        "end_time": "1404/08/25 11:45:00",
        "date": "1404/08/25",
    }
    a = Activity.from_dict(data)
    assert a.title == "Walk"
    assert a.date == "1404/08/25"
