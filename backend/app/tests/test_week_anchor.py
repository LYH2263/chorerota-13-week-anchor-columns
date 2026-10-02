import pytest
from fastapi import HTTPException

from app import seed
from app.db import connect
from app import main
from app.main import GenBody, SwapBody
from app.modules.week_anchor import current_anchor
from app.engines.anchor import project_columns


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    seed.init_db()
    return connect


def _board_week1(c):
    return c.execute("SELECT week_anchor FROM weeks WHERE id=1").fetchone()["week_anchor"]


def _grid(c):
    return [
        (r["day"], r["task_id"], r["member_id"])
        for r in c.execute("SELECT day,task_id,member_id FROM assignments ORDER BY day,task_id")
    ]


def test_legacy_week_backfilled_to_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    c = connect()
    c.execute("CREATE TABLE weeks(id INTEGER PRIMARY KEY, label TEXT, status TEXT)")
    c.execute("INSERT INTO weeks(label,status) VALUES ('旧周','ready')")
    c.commit(); c.close()

    seed.init_db()

    c = connect()
    rows = c.execute("SELECT week_anchor FROM weeks").fetchall()
    assert all(r["week_anchor"] == 0 for r in rows)
    c.close()


def test_current_anchor_defaults_and_setting(db):
    c = db()
    assert current_anchor(c) == 0
    main.put_settings({"week_anchor": 6})
    assert current_anchor(c) == 6
    c.close()


def test_generate_stamps_current_anchor_and_board_keeps_it(db):
    main.generate(1, GenBody())
    c = db()
    assert _board_week1(c) == 0
    labels0 = [col["label"] for col in project_columns(7, 0)]
    c.close()

    # changing the current anchor must not move an already pinned week
    main.put_settings({"week_anchor": 6})
    c = db()
    assert _board_week1(c) == 0
    assert [col["label"] for col in project_columns(7, _board_week1(c))] == labels0
    c.close()


def test_regenerate_restamps_but_stored_day_cells_unchanged(db):
    main.generate(1, GenBody())
    c = db(); before = _grid(c); c.close()

    main.put_settings({"week_anchor": 6})
    main.generate(1, GenBody())  # rewrites assignments and re-stamps

    c = db()
    assert _board_week1(c) == 6
    assert _grid(c) == before  # same members on the same stored days; only titles shift
    c.close()


def test_out_of_range_anchor_rejected(db):
    for bad in (-1, 7, "x"):
        with pytest.raises(HTTPException) as ei:
            main.put_settings({"week_anchor": bad})
        assert ei.value.status_code == 400
        assert ei.value.detail == "anchor_out_of_range"
    c = db()
    assert c.execute("SELECT value FROM settings WHERE key='week_anchor'").fetchone()["value"] == "0"
    c.close()


def test_swap_uses_stored_days_and_cells_keep_day_membership(db):
    main.generate(1, GenBody())
    c = db()
    tids = [r["id"] for r in c.execute("SELECT id FROM tasks WHERE data_quality='clean' ORDER BY id")]
    c.close()
    tid1, tid2 = tids[0], tids[1]

    sid = main.request_swap(1, SwapBody(a_day=0, a_task=tid1, b_day=0, b_task=tid2))["id"]
    main.confirm_swap(sid)

    c = db()
    cells = {(r["day"], r["task_id"]): r["member_id"] for r in
             c.execute("SELECT day,task_id,member_id FROM assignments")}
    assert set(cells) == {(d, t) for d in range(7) for t in tids}  # days untouched
    sw = c.execute("SELECT a_day,b_day,a_task,b_task FROM swap_requests WHERE id=?", (sid,)).fetchone()
    assert (sw["a_day"], sw["b_day"], sw["a_task"], sw["b_task"]) == (0, 0, tid1, tid2)
    c.close()
