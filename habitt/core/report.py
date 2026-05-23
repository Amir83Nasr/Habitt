"""Report generation for Habitt notifications."""

from __future__ import annotations

from habitt.core.jalali_helper import shamsi_diff_seconds, today_shamsi_str
from habitt.core.notify import send_message
from habitt.tico.todo_manager import TodoManager
from habitt.tracker.tracker_manager import TrackerManager


def _format_tasks(date_str: str, done_filter: bool | None = None) -> str:
    """Return formatted tasks for a date."""
    mgr = TodoManager()
    if done_filter is None:
        tasks = mgr.list_all(date=date_str, include_done=True)
    elif done_filter:
        tasks = [t for t in mgr.list_all(date=date_str, include_done=True) if t.done]
    else:
        tasks = mgr.list_all(date=date_str, include_done=False)

    if not tasks:
        return "No tasks."

    max_title = min(max((len(t.title) for t in tasks), default=15), 30)
    lines = []
    lines.append(f"{'Status':<6} {'Task':<{max_title}}")
    lines.append("-" * (8 + max_title))
    for t in tasks:
        status = "[x]" if t.done else "[ ]"
        lines.append(f"{status:<6} {t.title[:max_title]:<{max_title}}")
    return "\n".join(lines)


def _format_activities(date_str: str) -> str:
    """Return clean activity list using 'h' instead of ':' for times."""
    mgr = TrackerManager()
    acts = [a for a in mgr.list_all() if a.date == date_str]
    if not acts:
        return "No activities."

    total_secs = sum(shamsi_diff_seconds(a.start_time, a.end_time) for a in acts)
    th = int(total_secs // 3600)
    tm = int((total_secs % 3600) // 60)

    lines = []
    # Header
    lines.append(f"Activities for {date_str}")
    lines.append("-" * 60)
    # Each line
    for a in acts:
        # تبدیل HH:MM:SS به HHhMM
        start_time = a.start_time.split()[1]  # "HH:MM:SS"
        start_h, start_m, _ = start_time.split(":")
        start_str = f"{start_h}:{start_m}"
        end_time = a.end_time.split()[1]
        end_h, end_m, _ = end_time.split(":")
        end_str = f"{end_h}:{end_m}"

        secs = shamsi_diff_seconds(a.start_time, a.end_time)
        dur_h = int(secs // 3600)
        dur_m = int((secs % 3600) // 60)
        dur = f"{dur_h}h{dur_m:02d}m"

        lines.append(f"({start_str}) - ({end_str})  ({dur})  {a.title}")

    # Footer
    lines.append("-" * 60)
    lines.append(f"Total time: {th}h{tm:02d}m")
    return "\n".join(lines)


def build_report(report_type: str, date_str: str | None = None) -> str:
    """Build a text report based on type and optional date (default today)."""
    if date_str is None:
        date_str = today_shamsi_str()

    if report_type == "summary":
        todo = TodoManager()
        tasks_today = todo.list_all(date=date_str, include_done=True)
        open_tasks = [t for t in tasks_today if not t.done]
        track = TrackerManager()
        total_secs = sum(
            shamsi_diff_seconds(a.start_time, a.end_time)
            for a in track.list_all()
            if a.date == date_str
        )
        th = int(total_secs // 3600)
        tm = int((total_secs % 3600) // 60)

        lines = [f"Daily Report - {date_str}"]
        lines.append("=" * 30)
        lines.append(f"Tasks: {len(tasks_today)} total, {len(open_tasks)} open")
        lines.append(f"Time tracked: {th}:{tm:02d}")
        if tasks_today:
            lines.append("\nTasks:")
            lines.append(_format_tasks(date_str))
        if total_secs > 0:  # فقط اگر فعالیت وجود دارد
            lines.append("\nActivities:")
            lines.append(_format_activities(date_str))
        return "\n".join(lines)

    elif report_type == "tasks":
        return f"Tasks for {date_str}\n" + _format_tasks(date_str)

    elif report_type == "activities":
        return _format_activities(date_str)  # هدر خودش تاریخ را دارد

    else:
        return "Unknown report type."


def build_and_send_report(
    report_type: str, date_str: str | None = None
) -> tuple[bool, str]:
    """Build report, send it, return (success, text)."""
    text = build_report(report_type, date_str)
    success = send_message(text)
    return success, text
