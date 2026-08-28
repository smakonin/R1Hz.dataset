#!/usr/bin/env python3
"""Recover hourly energy gaps and rebuild the daily/monthly aggregates.

Source CSVs are read-only.  This script writes intermediate CSVs plus an audit
log; the spreadsheet artifact finalizer imports and emits the delivered CSVs.
"""

from __future__ import annotations

import csv
import json
import math
import mmap
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "energy_recovery"
OUT.mkdir(parents=True, exist_ok=True)

SOURCE_HOURLY = ROOT / "energy_hourly.csv"
SOURCE_DAILY = ROOT / "energy_daily.csv"
SOURCE_MONTHLY = ROOT / "energy_monthly.csv"
RECOVERED_POWER = ROOT / "recovered" / "power.csv"


def mmap_lower_bound(mm: mmap.mmap, target_ts: int, data_start: int) -> int:
    """Return the byte offset of the first CSV row whose unix_ts >= target_ts."""
    low = data_start
    high = len(mm) - 1
    while high - low > 4096:
        midpoint = (low + high) // 2
        row_start = mm.rfind(b"\n", data_start - 1, midpoint) + 1
        if row_start <= low:
            next_newline = mm.find(b"\n", midpoint)
            if next_newline < 0:
                high = midpoint
                continue
            row_start = next_newline + 1
        comma = mm.find(b",", row_start)
        if comma < 0:
            high = midpoint
            continue
        timestamp = int(mm[row_start:comma])
        if timestamp < target_ts:
            newline = mm.find(b"\n", comma)
            if newline < 0:
                return len(mm)
            low = newline + 1
        else:
            high = row_start

    row_start = mm.rfind(b"\n", data_start - 1, low) + 1
    if row_start < data_start:
        row_start = data_start
    while row_start < len(mm):
        comma = mm.find(b",", row_start)
        if comma < 0:
            return len(mm)
        timestamp = int(mm[row_start:comma])
        if timestamp >= target_ts:
            return row_start
        newline = mm.find(b"\n", comma)
        if newline < 0:
            return len(mm)
        row_start = newline + 1
    return len(mm)


def aggregate_recovered_power(
    circuit_labels: set[int], circuit_cols: list[str]
) -> tuple[dict[int, dict[str, int]], dict[int, int]]:
    """Aggregate only the source hours needed by blank hourly circuit labels."""
    source_ranges = []
    sorted_labels = sorted(circuit_labels)
    range_start = sorted_labels[0]
    previous = range_start
    for label in sorted_labels[1:]:
        if label != previous + 3600:
            source_ranges.append((range_start - 3600, previous))
            range_start = label
        previous = label
    source_ranges.append((range_start - 3600, previous))

    sums = {label: {column: 0.0 for column in circuit_cols} for label in circuit_labels}
    counts = {label: 0 for label in circuit_labels}

    with RECOVERED_POWER.open("rb") as handle:
        mm = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
        header_end = mm.find(b"\n")
        header = mm[:header_end].decode("utf-8").rstrip("\r").split(",")
        column_indexes = {column: header.index(column) for column in circuit_cols}
        data_start = header_end + 1

        for source_start, source_end_exclusive in source_ranges:
            position = mmap_lower_bound(mm, source_start, data_start)
            while position < len(mm):
                newline = mm.find(b"\n", position)
                if newline < 0:
                    newline = len(mm)
                row = mm[position:newline].decode("utf-8").rstrip("\r").split(",")
                timestamp = int(row[0])
                if timestamp >= source_end_exclusive:
                    break
                label = (timestamp // 3600) * 3600 + 3600
                if label in circuit_labels:
                    counts[label] += 1
                    for column in circuit_cols:
                        value = row[column_indexes[column]]
                        if value == "":
                            raise ValueError(f"Recovered power is still blank at {timestamp}, column {column}")
                        sums[label][column] += float(value)
                position = newline + 1
        mm.close()

    incomplete = {label: count for label, count in counts.items() if count != 3600}
    if incomplete:
        raise ValueError(f"Recovered power source hours are incomplete: {incomplete}")

    recovered = {
        label: {
            column: int(math.ceil(total / counts[label] - 1e-12))
            for column, total in column_sums.items()
        }
        for label, column_sums in sums.items()
    }
    return recovered, counts


def round_to_10(value: float) -> int:
    return int(np.rint(value / 10.0) * 10)


def main() -> None:
    hourly = pd.read_csv(SOURCE_HOURLY)
    daily = pd.read_csv(SOURCE_DAILY)
    monthly = pd.read_csv(SOURCE_MONTHLY)
    raw_hourly = hourly.copy(deep=True)
    raw_daily = daily.copy(deep=True)
    raw_monthly = monthly.copy(deep=True)

    # Empty marker columns are inferred as float by pandas; make them explicit
    # strings before assigning the synthetic-data marker.
    for frame in [hourly, daily, monthly]:
        frame["marker"] = frame["marker"].astype("string")

    measure_cols = list(hourly.columns[5:])
    circuit_cols = list(hourly.columns[6:])
    if len(circuit_cols) != 19:
        raise ValueError(f"Expected 19 circuit columns, found {len(circuit_cols)}")

    first_ts = int(hourly.unix_ts.iloc[0])
    circuit_blank_mask = hourly[circuit_cols].isna().all(axis=1)
    internal_circuit_mask = circuit_blank_mask & hourly.unix_ts.ne(first_ts)
    internal_circuit_labels = set(hourly.loc[internal_circuit_mask, "unix_ts"].astype(int))
    if len(internal_circuit_labels) != 39:
        raise ValueError(f"Expected 39 internal circuit gap hours, found {len(internal_circuit_labels)}")

    recovered_circuits, power_counts = aggregate_recovered_power(
        internal_circuit_labels, circuit_cols
    )

    audit_rows: list[dict] = []
    for label in sorted(internal_circuit_labels):
        row_index = hourly.index[hourly.unix_ts.eq(label)][0]
        for column in circuit_cols:
            recovered_value = recovered_circuits[label][column]
            hourly.at[row_index, column] = recovered_value
            audit_rows.append(
                {
                    "file": "energy_hourly.csv",
                    "unix_ts": label,
                    "local_dt": hourly.at[row_index, "local_dt"],
                    "local_tm": hourly.at[row_index, "local_tm"],
                    "column": column,
                    "original_value": "",
                    "recovered_value": recovered_value,
                    "method": "recovered_1hz_power_mean_ceil",
                    "source_hour_unix_ts": label - 3600,
                    "source_samples": power_counts[label],
                    "confidence": "medium",
                    "notes": "Hourly aggregation is direct; missing 1 Hz seconds are synthetic donor values.",
                }
            )

    ihd = pd.read_csv(ROOT / "ihd.csv", usecols=["unix_ts", "power"]).drop_duplicates(
        "unix_ts"
    )
    ihd["source_hour"] = (ihd.unix_ts // 3600) * 3600
    ihd_hourly = ihd.groupby("source_hour").power.agg(["mean", "size"])

    # Fit a separate relationship within each target month.  This leaves the
    # calibration local while using only observed utility rows.
    observed_utility = raw_hourly.dropna(subset=["utility", "main"]).copy()
    observed_utility["month"] = observed_utility.local_dt.str[:7]
    month_models: dict[str, tuple[float, float, int]] = {}
    for month, rows in observed_utility.groupby("month"):
        slope, intercept = np.polyfit(rows.main.to_numpy(), rows.utility.to_numpy(), 1)
        month_models[month] = (float(slope), float(intercept), len(rows))

    utility_gap_indexes = list(hourly.index[hourly.utility.isna()])
    utility_method_counts: dict[str, int] = {}
    for row_index in utility_gap_indexes:
        label = int(hourly.at[row_index, "unix_ts"])
        source_hour = label - 3600
        month = str(hourly.at[row_index, "local_dt"])[:7]
        slope, intercept, training_rows = month_models[month]
        main_value = float(hourly.at[row_index, "main"])
        model_raw = slope * main_value + intercept
        model_value = max(0, round_to_10(model_raw))

        if source_hour in ihd_hourly.index:
            ihd_mean = float(ihd_hourly.at[source_hour, "mean"])
            ihd_samples = int(ihd_hourly.at[source_hour, "size"])
            ihd_value = max(0, round_to_10(ihd_mean))
        else:
            ihd_mean = np.nan
            ihd_samples = 0
            ihd_value = None

        if ihd_samples >= 440:
            recovered_value = int(ihd_value)
            method = "ihd_hourly_mean_round10"
            confidence = "high"
            note = f"Main-model cross-check={model_value} Wh; delta={recovered_value - model_value} Wh."
        elif ihd_samples > 0:
            recovered_value = model_value
            method = "utility_main_model_partial_ihd_check"
            confidence = "medium-high"
            note = f"Partial-IHD cross-check={ihd_value} Wh from {ihd_samples} samples."
        else:
            recovered_value = model_value
            method = "utility_main_model"
            confidence = "medium-high"
            note = "No usable IHD samples; month-local utility~main calibration used."

        hourly.at[row_index, "utility"] = recovered_value
        utility_method_counts[method] = utility_method_counts.get(method, 0) + 1
        audit_rows.append(
            {
                "file": "energy_hourly.csv",
                "unix_ts": label,
                "local_dt": hourly.at[row_index, "local_dt"],
                "local_tm": hourly.at[row_index, "local_tm"],
                "column": "utility",
                "original_value": "",
                "recovered_value": recovered_value,
                "method": method,
                "source_hour_unix_ts": source_hour,
                "source_samples": ihd_samples,
                "confidence": confidence,
                "notes": f"{note} Model trained on {training_rows} observed rows in {month}.",
            }
        )

    # Mark every hourly row that contains at least one reconstructed value.
    recovered_hourly_mask = internal_circuit_mask | raw_hourly.utility.isna()
    hourly.loc[recovered_hourly_mask, "marker"] = "s"

    # Rebuild all aggregate values from the repaired hourly labels.  This is
    # necessary because existing nonblank totals skipped lower-grain blanks.
    daily_sums = hourly.groupby("local_dt")[measure_cols].sum()
    for column in measure_cols:
        daily[column] = daily.local_dt.map(daily_sums[column])

    synthetic_dates = set(hourly.loc[hourly.marker.eq("s"), "local_dt"])
    daily.loc[daily.local_dt.isin(synthetic_dates), "marker"] = "s"

    daily_for_month = daily.copy()
    daily_for_month["month"] = daily_for_month.local_dt.str[:7]
    monthly_sums = daily_for_month.groupby("month")[measure_cols].sum()
    monthly_keys = monthly.local_dt.str[:7]
    for column in measure_cols:
        monthly[column] = monthly_keys.map(monthly_sums[column])

    synthetic_months = {date[:7] for date in synthetic_dates}
    monthly.loc[monthly_keys.isin(synthetic_months), "marker"] = "s"

    # Preserve integer energy fields and the original column order in the
    # intermediate CSVs that the artifact-tool finalizer will import.
    for frame in [hourly, daily, monthly]:
        for column in measure_cols:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").round().astype("Int64")

    intermediate_paths = {
        "hourly": OUT / "intermediate_energy_hourly.csv",
        "daily": OUT / "intermediate_energy_daily.csv",
        "monthly": OUT / "intermediate_energy_monthly.csv",
    }
    hourly.to_csv(intermediate_paths["hourly"], index=False, na_rep="", quoting=csv.QUOTE_MINIMAL)
    daily.to_csv(intermediate_paths["daily"], index=False, na_rep="", quoting=csv.QUOTE_MINIMAL)
    monthly.to_csv(intermediate_paths["monthly"], index=False, na_rep="", quoting=csv.QUOTE_MINIMAL)

    audit = pd.DataFrame(audit_rows).sort_values(["unix_ts", "column"]).reset_index(drop=True)
    audit.to_csv(OUT / "cell_recovery_log.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    # Quantify exactly what changed before the artifact-tool serialization step.
    def changed_energy_cells(before: pd.DataFrame, after: pd.DataFrame) -> int:
        left = before[measure_cols].to_numpy(dtype=float, na_value=np.nan)
        right = after[measure_cols].to_numpy(dtype=float, na_value=np.nan)
        return int((~np.isclose(left, right, equal_nan=True)).sum())

    summary = {
        "hourly_rows": len(hourly),
        "daily_rows": len(daily),
        "monthly_rows": len(monthly),
        "hourly_recovered_cells": len(audit),
        "circuit_recovered_cells": int((audit.column != "utility").sum()),
        "utility_recovered_cells": int((audit.column == "utility").sum()),
        "hourly_marker_s_rows": int(hourly.marker.eq("s").sum()),
        "daily_marker_s_rows": int(daily.marker.eq("s").sum()),
        "monthly_marker_s_rows": int(monthly.marker.eq("s").sum()),
        "remaining_hourly_blank_energy_cells": int(hourly[measure_cols].isna().sum().sum()),
        "remaining_daily_blank_energy_cells": int(daily[measure_cols].isna().sum().sum()),
        "remaining_monthly_blank_energy_cells": int(monthly[measure_cols].isna().sum().sum()),
        "hourly_changed_energy_cells": changed_energy_cells(raw_hourly, hourly),
        "daily_changed_energy_cells": changed_energy_cells(raw_daily, daily),
        "monthly_changed_energy_cells": changed_energy_cells(raw_monthly, monthly),
        "utility_method_counts": utility_method_counts,
        "opening_boundary": {
            "unix_ts": first_ts,
            "blank_circuit_cells_left_unchanged": int(hourly.loc[hourly.unix_ts.eq(first_ts), circuit_cols].isna().sum().sum()),
        },
    }
    (OUT / "recovery_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
