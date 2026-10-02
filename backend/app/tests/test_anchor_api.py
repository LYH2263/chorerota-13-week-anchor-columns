"""锚日 API 级测试：直接调端点函数（无需 httpx），tmp DATA_DIR 隔离。

三路可测面：设置页（put_settings）、看板回看（week_board）、对调台（swap 流程）。
"""
import sqlite3

import pytest
from fastapi import HTTPException

from app import seed, main
from app.db import db_path


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    seed.init_db()
    yield tmp_path


# ---------- 设置页：锚越界拒写 ----------
def test_put_settings_rejects_out_of_range_anchor(db):
    with pytest.raises(HTTPException) as ei:
        main.put_settings({"week_anchor": 7})
    assert ei.value.status_code == 400
    assert ei.value.detail == "week_anchor_out_of_range"
    assert main.get_settings().get("week_anchor") != "7"  # 拒写不落库


@pytest.mark.parametrize("bad", [-1, 6.5, "abc", None, True])
def test_put_settings_rejects_non_int_anchor(db, bad):
    with pytest.raises(HTTPException):
        main.put_settings({"week_anchor": bad})


def test_put_settings_accepts_valid_anchor(db):
    main.put_settings({"week_anchor": 5, "household": "绿纸之家"})
    s = main.get_settings()
    assert s["week_anchor"] == "5"
    assert s["household"] == "绿纸之家"  # 同包其他键正常落库


# ---------- 看板回看：生成钉锚，改设置不回溯 ----------
def test_generate_pins_current_anchor(db):
    main.put_settings({"week_anchor": 2})
    main.generate(1, main.GenBody())
    b = main.week_board(1)
    assert b["week_anchor"] == 2 and b["anchor_pinned"] is True
    assert b["columns"][0] == {"day": 0, "label": "周三"}
    assert b["columns"][6] == {"day": 6, "label": "周二"}


def test_old_week_keeps_pinned_anchor_after_settings_change(db):
    main.put_settings({"week_anchor": 2})
    main.generate(1, main.GenBody())
    before = main.week_board(1)
    main.put_settings({"week_anchor": 6})  # 只改现行锚
    after = main.week_board(1)
    assert after["week_anchor"] == 2
    assert [c["label"] for c in after["columns"]] == [c["label"] for c in before["columns"]]
    # 格位归属也不动
    key = lambda a: (a["day"], a["task_id"])
    assert {key(a): a["member_id"] for a in after["assignments"]} == \
           {key(a): a["member_id"] for a in before["assignments"]}


def test_draft_week_previews_current_anchor(db):
    main.put_settings({"week_anchor": 3})
    b = main.week_board(1)  # 未生成，钉值为 NULL
    assert b["anchor_pinned"] is False
    assert b["week_anchor"] == 3
    assert b["columns"][0]["label"] == "周四"


# ---------- 对调台：仍写存储 day，格位归属正确 ----------
def test_swap_flow_uses_stored_day_index(db):
    main.put_settings({"week_anchor": 4})
    main.generate(1, main.GenBody())
    before = main.week_board(1)["assignments"]
    at = lambda rows, d, t: next(a["member_id"] for a in rows if a["day"] == d and a["task_id"] == t)
    m_a, m_b = at(before, 0, 1), at(before, 1, 2)
    assert m_a != m_b
    r = main.request_swap(1, main.SwapBody(a_day=0, a_task=1, b_day=1, b_task=2))
    assert r["ok"] is True
    main.confirm_swap(r["id"])
    after_board = main.week_board(1)
    assert at(after_board["assignments"], 0, 1) == m_b
    assert at(after_board["assignments"], 1, 2) == m_a
    # 列标题仍吃钉锚，不随对调或现行设置变
    assert after_board["columns"][0]["label"] == "周五"


# ---------- 既有库迁移：weeks 补列，老行钉值为 NULL ----------
def test_init_db_migrates_old_weeks_table(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    c = sqlite3.connect(db_path())
    c.executescript("""
    CREATE TABLE members(id INTEGER PRIMARY KEY, name TEXT, active INT, data_quality TEXT);
    CREATE TABLE tasks(id INTEGER PRIMARY KEY, title TEXT, weight INT, data_quality TEXT);
    CREATE TABLE weeks(id INTEGER PRIMARY KEY, label TEXT, status TEXT);
    CREATE TABLE assignments(id INTEGER PRIMARY KEY AUTOINCREMENT, week_id INT, day INT, task_id INT, member_id INT);
    CREATE TABLE swap_requests(id INTEGER PRIMARY KEY AUTOINCREMENT, week_id INT, a_day INT, a_task INT, b_day INT, b_task INT, status TEXT, note TEXT);
    CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
    INSERT INTO members(name,active,data_quality) VALUES ('阿明',1,'clean');
    INSERT INTO weeks(label,status) VALUES ('第11周','ready');
    """)
    c.commit(); c.close()
    seed.init_db()  # 幂等：老库补列
    c = sqlite3.connect(db_path()); c.row_factory = sqlite3.Row
    cols = [r["name"] for r in c.execute("PRAGMA table_info(weeks)")]
    assert "week_anchor" in cols
    row = c.execute("SELECT * FROM weeks WHERE label='第11周'").fetchone()
    assert row["week_anchor"] is None  # 老周未钉，回看时回落现行锚
    c.close()
