"""Gamification features for Habitt."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from habitt.core.jalali_helper import parse_shamsi_datetime, today_shamsi_str

if TYPE_CHECKING:
    from habitt.tracker.models import Activity


def get_current_streak(activities: list[Activity]) -> int:
    """Calculate the current streak of consecutive days with activity."""
    if not activities:
        return 0

    # Get all dates with activities
    activity_dates = sorted(
        {parse_shamsi_datetime(a.start_time).date() for a in activities}, reverse=True
    )

    if not activity_dates:
        return 0

    today = parse_shamsi_datetime(today_shamsi_str() + " 00:00:00").date()

    # Check if the last activity was today or yesterday
    if activity_dates[0] < today - timedelta(days=1):
        return 0

    streak = 0
    current_date = activity_dates[0]

    for date in activity_dates:
        if date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif date == current_date + timedelta(days=1):
            # This handles cases where multiple activities on the same day
            # are already handled by the set/sorted logic
            pass
        else:
            break

    return streak
