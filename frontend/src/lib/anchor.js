// Mirror of backend app/engines/anchor.py. Stored day index never changes;
// anchor only projects a stored day onto a weekday label for display.
export const WEEKDAY_LABELS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

export function weekdayOf(day, anchor = 0) {
  return (Number(anchor) + Number(day)) % 7
}

export function labelFor(day, anchor = 0) {
  return WEEKDAY_LABELS[weekdayOf(day, anchor)]
}
