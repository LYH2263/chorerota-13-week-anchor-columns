# Chorerota · 家庭值日轮转

底座：成员+任务 → round-robin 生成周表 → 申请对调 → 确认改表。

| 服务 | 端口 |
| --- | --- |
| 前端 | 5100 |
| API | 10100 |

```bash
docker compose up --build
pytest backend/app/tests
```

种子含 clean/dirty。0-1 空桩：`streak_badge` / `skip_week` / `chore_photo`。

周锚日：设置页登记 `week_anchor`（0–6，越界拒写）；生成周表时钉入 `weeks.week_anchor`，看板列标题按钉锚映射星期文案，改现行锚不回溯旧周。存储与对调仍用 day 索引，锚只决定列标题。快照见 `modules/anchor_snapshot`，投影见 `modules/anchor_projection`。
