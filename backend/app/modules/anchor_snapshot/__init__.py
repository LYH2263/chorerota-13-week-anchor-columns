"""锚快照：week_anchor 的校验、读取与钉入。

周生成时把现行锚钉进 weeks.week_anchor，之后改设置不回溯旧周。
投影（day 索引 → 星期文案）在 anchor_projection 模块，两边职责分开。
"""

MIN_ANCHOR = 0
MAX_ANCHOR = 6
DEFAULT_ANCHOR = 0
SETTING_KEY = "week_anchor"


def validate_anchor(value) -> int:
    """归一化锚日；越界或非整数一律 ValueError('week_anchor_out_of_range')。"""
    if isinstance(value, bool):  # bool 是 int 子类，先挡掉
        raise ValueError("week_anchor_out_of_range")
    if isinstance(value, int):
        anchor = value
    elif isinstance(value, str) and value.lstrip("-").isdigit():
        anchor = int(value)
    else:
        raise ValueError("week_anchor_out_of_range")
    if not MIN_ANCHOR <= anchor <= MAX_ANCHOR:
        raise ValueError("week_anchor_out_of_range")
    return anchor


def current_anchor(conn) -> int:
    """现行锚：settings 里的 week_anchor；缺行或脏值回落默认锚。"""
    row = conn.execute("SELECT value FROM settings WHERE key=?", (SETTING_KEY,)).fetchone()
    if row is None:
        return DEFAULT_ANCHOR
    try:
        return validate_anchor(row["value"])
    except ValueError:
        return DEFAULT_ANCHOR


def pin_week_anchor(conn, week_id: int) -> int:
    """生成周时调用：把现行锚钉入 weeks.week_anchor，返回钉入值。"""
    anchor = current_anchor(conn)
    conn.execute("UPDATE weeks SET week_anchor=? WHERE id=?", (anchor, week_id))
    return anchor
