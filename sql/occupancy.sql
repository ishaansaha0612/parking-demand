-- Occupancy of every lot in 15-minute slots, weekdays only.
-- A car counts as parked in a slot if it scanned in at or before the slot
-- and scanned out after it. Sessions with no scan-out are excluded upstream.
--
-- Uses sessions(day, in_min, out_min) columns added at load time and an
-- index on (lot, day) so the join stays fast on ~200k sessions.

WITH RECURSIVE slots(minute) AS (
    SELECT 6 * 60
    UNION ALL
    SELECT minute + 15 FROM slots WHERE minute < 20 * 60
),
days AS (
    SELECT DISTINCT day FROM sessions WHERE weekday BETWEEN 1 AND 5
),
grid AS (
    SELECT d.day, s.minute, l.lot, l.capacity
    FROM days d CROSS JOIN slots s CROSS JOIN lots l
)
SELECT
    g.day,
    CAST(strftime('%w', g.day) AS INTEGER) AS weekday,  -- 1 = Monday
    g.minute,
    g.lot,
    g.capacity,
    COUNT(x.session_id) AS parked
FROM grid g
LEFT JOIN sessions x
    ON x.lot = g.lot
   AND x.day = g.day
   AND x.in_min <= g.minute
   AND x.out_min > g.minute
GROUP BY g.day, g.minute, g.lot
ORDER BY g.day, g.lot, g.minute;
