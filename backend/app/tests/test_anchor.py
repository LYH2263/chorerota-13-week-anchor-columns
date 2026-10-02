import pytest

from app.engines.anchor import WEEKDAY_LABELS, weekday_of, project_columns


def test_anchor_zero_maps_in_order():
    cols = project_columns(7, 0)
    assert [c["weekday"] for c in cols] == [0, 1, 2, 3, 4, 5, 6]
    assert [c["label"] for c in cols] == WEEKDAY_LABELS
    assert weekday_of(3, 0) == 3


def test_anchor_six_wraps():
    assert weekday_of(0, 6) == 6
    assert weekday_of(1, 6) == 0
    cols = project_columns(7, 6)
    assert [c["label"] for c in cols] == ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]


def test_projection_keeps_stored_day_order_and_cells():
    cols = project_columns(7, 3)
    assert [c["day"] for c in cols] == [0, 1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("value", [0, 6, "0", "6", 3.0])
def test_parse_anchor_accepts(value):
    from app.modules.week_anchor import parse_anchor
    assert parse_anchor(value) == int(value)


@pytest.mark.parametrize("value", [-1, 7, 100, "x", None, True, False])
def test_parse_anchor_rejects(value):
    from app.modules.week_anchor import parse_anchor
    with pytest.raises(ValueError):
        parse_anchor(value)
