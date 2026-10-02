"""锚快照 / 锚投影模块单测：纯逻辑 + 内存库，不依赖 fastapi。"""
import sqlite3

import pytest

from app.modules.anchor_snapshot import (
    validate_anchor, current_anchor, pin_week_anchor, DEFAULT_ANCHOR,
)
from app.modules.anchor_projection import (
    resolve_anchor, weekday_label, project_columns,
)


# ---------- 锚校验：0–6 之外一律拒 ----------
def test_validate_anchor_accepts_0_to_6():
    assert [validate_anchor(i) for i in range(7)] == [0, 1, 2, 3, 4, 5, 6]
    assert validate_anchor("3") == 3  # 数字字符串归一化


@pytest.mark.parametrize("bad", [-1, 7, 100, "-2", "3.5", "abc", "", None, 1.5, True, False])
def test_validate_anchor_rejects_out_of_range(bad):
    with pytest.raises(ValueError, match="week_anchor_out_of_range"):
        validate_anchor(bad)


# ---------- 投影：存储 day → 星期文案 ----------
def test_weekday_label_anchor_zero():
    assert weekday_label(0, 0) == "周一"
    assert weekday_label(6, 0) == "周日"


def test_weekday_label_wraps_with_anchor():
    assert weekday_label(0, 2) == "周三"
    assert weekday_label(5, 2) == "周一"  # 跨周取模
    assert weekday_label(6, 6) == "周六"


def test_project_columns_keeps_storage_day():
    cols = project_columns(7, 4)
    assert [c["day"] for c in cols] == list(range(7))  # day 仍是存储索引
    assert cols[0]["label"] == "周五"


# ---------- 双源取舍：钉锚优先，未钉回落现行 ----------
def test_resolve_anchor_prefers_pinned():
    assert resolve_anchor(3, 0) == 3


def test_resolve_anchor_falls_back_to_current_when_unpinned():
    assert resolve_anchor(None, 5) == 5


# ---------- 快照：读取与钉入 ----------
def _mem_conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript("""
    CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE weeks(id INTEGER PRIMARY KEY, label TEXT, status TEXT, week_anchor INT);
    INSERT INTO weeks(label,status) VALUES ('第12周','draft');
    """)
    return c


def test_current_anchor_defaults_when_missing_or_dirty():
    c = _mem_conn()
    assert current_anchor(c) == DEFAULT_ANCHOR  # 缺行
    c.execute("INSERT INTO settings VALUES ('week_anchor','9')")  # 脏值
    assert current_anchor(c) == DEFAULT_ANCHOR
    c.close()


def test_pin_week_anchor_freezes_value():
    c = _mem_conn()
    c.execute("INSERT INTO settings VALUES ('week_anchor','4')")
    assert pin_week_anchor(c, 1) == 4
    c.execute("UPDATE settings SET value='1' WHERE key='week_anchor'")  # 改现行锚
    row = c.execute("SELECT week_anchor FROM weeks WHERE id=1").fetchone()
    assert row["week_anchor"] == 4  # 钉值不回溯
    c.close()
