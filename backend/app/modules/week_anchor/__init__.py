"""week_anchor snapshot: validation + persistence.

Two sources of anchor exist by design:
- current anchor (settings table): used only when stamping a newly written week;
- historical anchor (weeks.week_anchor): the pinned snapshot for every past week.

Board/swap projection must read the week snapshot, never the current setting.
"""

DEFAULT_ANCHOR = 0


def parse_anchor(value) -> int:
    """Only integers 0-6 are accepted; anything else is rejected."""
    if isinstance(value, bool):
        raise ValueError("anchor_out_of_range")
    try:
        anchor = int(value)
    except (TypeError, ValueError):
        raise ValueError("anchor_out_of_range")
    if anchor < 0 or anchor > 6:
        raise ValueError("anchor_out_of_range")
    return anchor


def current_anchor(c) -> int:
    """Read the live setting; missing or dirty values fall back to 0 (Monday)."""
    row = c.execute("SELECT value FROM settings WHERE key='week_anchor'").fetchone()
    if row is None:
        return DEFAULT_ANCHOR
    try:
        return parse_anchor(row["value"])
    except ValueError:
        return DEFAULT_ANCHOR


def stamp_week(c, week_id: int, anchor: int) -> None:
    """Pin the anchor into a week at write time."""
    c.execute("UPDATE weeks SET week_anchor=? WHERE id=?", (anchor, week_id))


def backfill_week_anchors(c) -> None:
    """Weeks written before this feature existed are pinned to 0."""
    c.execute("UPDATE weeks SET week_anchor=? WHERE week_anchor IS NULL", (DEFAULT_ANCHOR,))
