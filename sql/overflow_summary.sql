-- Which lots run over capacity, how often, and when?
-- Input: the occupancy table produced by occupancy.sql.

SELECT
    lot,
    capacity,
    COUNT(DISTINCT day)                                            AS weekdays_observed,
    COUNT(DISTINCT CASE WHEN parked > capacity THEN day END)       AS weekdays_over_capacity,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN parked > capacity THEN day END)
          / COUNT(DISTINCT day), 1)                                AS pct_days_over,
    COUNT(DISTINCT CASE WHEN parked > capacity AND minute < 600 THEN day END)
                                                                   AS days_over_before_10am,
    MAX(parked)                                                    AS peak_parked,
    ROUND(100.0 * MAX(parked) / capacity, 0)                       AS peak_pct_of_capacity
FROM occupancy
GROUP BY lot, capacity
ORDER BY pct_days_over DESC, peak_pct_of_capacity DESC;
