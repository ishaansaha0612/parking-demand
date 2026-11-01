import sqlite3
import pandas as pd
from src.analysis import clean, load, occupancy, overflow_summary, stagger


def tiny():
    s = pd.DataFrame({
        "session_id": ["a", "b", "c", "d"],
        "lot": ["X", "X", "X", "Y"],
        "permit_type": ["Student commuter"] * 4,
        # Monday 2025-09-01
        "scan_in": ["2025-09-01 08:00", "2025-09-01 08:10", "2025-09-01 09:00", "2025-09-01 08:00"],
        "scan_out": ["2025-09-01 09:30", "2025-09-01 08:20", None, "2025-09-01 08:05"],
    })
    lots = pd.DataFrame({"lot": ["X", "Y"], "capacity": [1, 5]})
    return s, lots


def test_clean_drops_missing_scan_out():
    s, _ = tiny()
    out, report = clean(s)
    assert report["dropped_missing_scan_out"] == 1
    assert len(out) == 3


def test_sql_occupancy_counts_exactly():
    s, lots = tiny()
    s, _ = clean(s)
    con = sqlite3.connect(":memory:")
    load(con, s, lots)
    occ = occupancy(con).set_index(["lot", "minute"])["parked"]
    assert occ[("X", 8 * 60)] == 1          # a parked
    assert occ[("X", 8 * 60 + 15)] == 2     # a + b
    assert occ[("X", 9 * 60 + 30)] == 0     # a left exactly at 9:30
    summary = overflow_summary(con).set_index("lot")
    assert summary.loc["X", "weekdays_over_capacity"] == 1
    assert summary.loc["Y", "weekdays_over_capacity"] == 0


def test_stagger_moves_only_early_commuters():
    s, _ = tiny()
    s, _ = clean(s)
    moved = stagger(s, ["X"], ["Y"], share=1.0)
    assert (moved.lot == "Y").sum() == 3
    assert len(moved) == len(s)
