#!/usr/bin/env python3
"""Validate delivered recovered energy CSVs against the raw sources."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "energy_recovery"


def main() -> None:
    raw_hourly = pd.read_csv(ROOT / "energy_hourly.csv")
    raw_daily = pd.read_csv(ROOT / "energy_daily.csv")
    raw_monthly = pd.read_csv(ROOT / "energy_monthly.csv")
    hourly = pd.read_csv(ROOT / "recovered" / "energy_hourly.csv")
    daily = pd.read_csv(ROOT / "recovered" / "energy_daily.csv")
    monthly = pd.read_csv(ROOT / "recovered" / "energy_monthly.csv")
    audit = pd.read_csv(OUT / "cell_recovery_log.csv")

    measure_cols = list(hourly.columns[5:])
    full_ihd = audit[audit.method.eq("ihd_hourly_mean_round10")]
    ihd_model_deltas = []
    for note in full_ihd.notes:
        match = re.search(r"delta=(-?\d+) Wh", note)
        if match:
            ihd_model_deltas.append(int(match.group(1)))

    hourly_sums = hourly.groupby("local_dt")[measure_cols].sum().reindex(daily.local_dt)
    daily_for_month = daily.copy()
    daily_for_month["month"] = daily_for_month.local_dt.str[:7]
    monthly_sums = daily_for_month.groupby("month")[measure_cols].sum().reindex(
        monthly.local_dt.str[:7]
    )

    observed_changed = int(
        (
            raw_hourly[measure_cols].notna()
            & raw_hourly[measure_cols].ne(hourly[measure_cols])
        )
        .sum()
        .sum()
    )
    remaining_blank_rows = hourly.loc[
        hourly[measure_cols].isna().any(axis=1), ["unix_ts", "local_dt", "local_tm"]
    ]

    checks = {
        "schemas_equal": bool(
            list(hourly.columns)
            == list(raw_hourly.columns)
            == list(daily.columns)
            == list(raw_daily.columns)
            == list(monthly.columns)
            == list(raw_monthly.columns)
        ),
        "row_counts": {"hourly": len(hourly), "daily": len(daily), "monthly": len(monthly)},
        "timestamps_unchanged": bool(
            hourly.unix_ts.equals(raw_hourly.unix_ts)
            and daily.unix_ts.equals(raw_daily.unix_ts)
            and monthly.unix_ts.equals(raw_monthly.unix_ts)
        ),
        "duplicate_timestamps": {
            "hourly": int(hourly.unix_ts.duplicated().sum()),
            "daily": int(daily.unix_ts.duplicated().sum()),
            "monthly": int(monthly.unix_ts.duplicated().sum()),
        },
        "observed_hourly_energy_cells_changed": observed_changed,
        "recovered_hourly_cells": len(audit),
        "recovery_methods": {str(k): int(v) for k, v in audit.method.value_counts().items()},
        "marker_s_rows": {
            "hourly": int(hourly.marker.eq("s").sum()),
            "daily": int(daily.marker.eq("s").sum()),
            "monthly": int(monthly.marker.eq("s").sum()),
        },
        "remaining_blank_energy_cells": {
            "hourly": int(hourly[measure_cols].isna().sum().sum()),
            "daily": int(daily[measure_cols].isna().sum().sum()),
            "monthly": int(monthly[measure_cols].isna().sum().sum()),
        },
        "remaining_blank_rows": remaining_blank_rows.to_dict("records"),
        "hourly_to_daily_max_abs_difference_wh": float(
            np.nanmax(
                np.abs(
                    hourly_sums.to_numpy(dtype=float)
                    - daily[measure_cols].to_numpy(dtype=float)
                )
            )
        ),
        "daily_to_monthly_max_abs_difference_wh": float(
            np.nanmax(
                np.abs(
                    monthly_sums.to_numpy(dtype=float)
                    - monthly[measure_cols].to_numpy(dtype=float)
                )
            )
        ),
        "daily_marker_propagation_exact": bool(
            set(daily.loc[daily.marker.eq("s"), "local_dt"])
            == set(hourly.loc[hourly.marker.eq("s"), "local_dt"])
        ),
        "monthly_marker_propagation_exact": bool(
            set(monthly.loc[monthly.marker.eq("s"), "local_dt"].str[:7])
            == set(daily.loc[daily.marker.eq("s"), "local_dt"].str[:7])
        ),
        "ihd_vs_main_crosscheck": {
            "hours": len(ihd_model_deltas),
            "median_abs_difference_wh": float(np.median(np.abs(ihd_model_deltas))),
            "p95_abs_difference_wh": float(np.quantile(np.abs(ihd_model_deltas), 0.95)),
            "max_abs_difference_wh": int(np.max(np.abs(ihd_model_deltas))),
        },
    }

    failures = []
    if not checks["schemas_equal"]:
        failures.append("schema mismatch")
    if checks["row_counts"] != {"hourly": 18168, "daily": 757, "monthly": 26}:
        failures.append("row-count mismatch")
    if not checks["timestamps_unchanged"]:
        failures.append("timestamps changed")
    if any(checks["duplicate_timestamps"].values()):
        failures.append("duplicate timestamps")
    if observed_changed:
        failures.append("observed hourly energy changed")
    if len(audit) != 876:
        failures.append("unexpected recovery-log size")
    if checks["remaining_blank_energy_cells"] != {"hourly": 19, "daily": 0, "monthly": 0}:
        failures.append("unexpected remaining blanks")
    if checks["hourly_to_daily_max_abs_difference_wh"] != 0:
        failures.append("hourly/daily reconciliation failed")
    if checks["daily_to_monthly_max_abs_difference_wh"] != 0:
        failures.append("daily/monthly reconciliation failed")
    if not checks["daily_marker_propagation_exact"] or not checks["monthly_marker_propagation_exact"]:
        failures.append("marker propagation failed")

    checks["status"] = "passed" if not failures else "failed"
    checks["failures"] = failures
    (OUT / "validation_summary.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
