"""锚投影：存储 day 索引 → 星期文案。纯函数，不碰库。

存储层永远用 day 索引（0–6）；锚只决定列标题文案。
双源取舍：历史钉锚优先，未钉（草稿周）回落现行锚。
"""

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def resolve_anchor(pinned, current: int) -> int:
    """钉值非空吃钉值；否则吃现行锚（草稿周预览）。"""
    return current if pinned is None else pinned


def weekday_label(day: int, anchor: int) -> str:
    """存储 day 在锚日 anchor 下的星期文案，跨周取模。"""
    return WEEKDAYS[(anchor + day) % 7]


def project_columns(days: int, anchor: int) -> list[dict]:
    """看板列投影：[{day, label}]，day 为存储索引，label 为星期文案。"""
    return [{"day": d, "label": weekday_label(d, anchor)} for d in range(days)]
