"""Projection from stored day index (0-6) to weekday labels via week anchor.

Pure functions only: the anchor never rewrites or reorders stored days, it only
maps a stored day onto a weekday for column titles.
"""

WEEKDAY_LABELS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def weekday_of(day: int, anchor: int) -> int:
    """Stored `day` (0-based within the week grid) falls on weekday (anchor+day)%7."""
    return (anchor + day) % 7


def project_columns(days: int = 7, anchor: int = 0) -> list[dict]:
    """Return columns in stored-day order, each annotated with projected weekday."""
    return [
        {"day": d, "weekday": weekday_of(d, anchor), "label": WEEKDAY_LABELS[weekday_of(d, anchor)]}
        for d in range(days)
    ]
