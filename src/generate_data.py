"""Generate 4 months of synthetic parking-permit gate scans for a campus.

Each row is one parking session: a permit scanned in at a lot and later scanned
out. Two lots (B and D) are built to overflow on weekday mornings because they
sit next to the buildings with the most 8-10 a.m. classes.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

LOTS = {
    # lot: (capacity, weekday daily demand, share of arrivals that are early 8 a.m. classes)
    "A": (420, 380, 0.30),
    "B": (300, 470, 0.62),  # overflows
    "C": (520, 420, 0.35),
    "D": (250, 400, 0.58),  # overflows
    "E": (600, 420, 0.25),
    "F": (350, 260, 0.30),
}
PERMIT_TYPES = ["Student commuter", "Student resident", "Faculty/staff"]
START, END = "2025-08-25", "2025-12-12"


def generate(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    days = pd.date_range(START, END, freq="D")
    rows = []
    sid = 0
    for day in days:
        weekday = day.dayofweek < 5
        if not weekday:
            scale = 0.12
        elif day.dayofweek == 4:
            scale = 0.75  # lighter Fridays
        else:
            scale = 1.0
        for lot, (cap, demand, early_share) in LOTS.items():
            n = rng.poisson(demand * scale)
            early = rng.random(n) < early_share
            # arrival in minutes after midnight
            arrive = np.where(
                early,
                rng.normal(7 * 60 + 40, 18, n),   # rush for 8 a.m. classes
                rng.normal(11 * 60, 110, n),      # spread through the day
            ).clip(6 * 60, 19 * 60)
            stay = rng.gamma(4.0, 75, n).clip(50, 10 * 60)
            depart = (arrive + stay).clip(None, 23 * 60)
            ptype = rng.choice(PERMIT_TYPES, n, p=[0.62, 0.13, 0.25])
            for a, d, p in zip(arrive, depart, ptype):
                rows.append(
                    (
                        f"S{sid:07d}",
                        lot,
                        p,
                        day + pd.Timedelta(minutes=float(a)),
                        day + pd.Timedelta(minutes=float(d)),
                    )
                )
                sid += 1
    df = pd.DataFrame(rows, columns=["session_id", "lot", "permit_type", "scan_in", "scan_out"])
    df["scan_in"] = df["scan_in"].dt.floor("min")
    df["scan_out"] = df["scan_out"].dt.floor("min")
    # Realistic mess: ~0.4% of sessions never scanned out (gate arm left up)
    lost = rng.random(len(df)) < 0.004
    df.loc[lost, "scan_out"] = pd.NaT
    return df


def lots_table() -> pd.DataFrame:
    return pd.DataFrame(
        [(k, v[0]) for k, v in LOTS.items()], columns=["lot", "capacity"]
    )


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    df = generate()
    df.to_csv("data/permit_scans.csv", index=False)
    lots_table().to_csv("data/lots.csv", index=False)
    print(f"Wrote {len(df):,} sessions")
