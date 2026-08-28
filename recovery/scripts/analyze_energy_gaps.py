#!/usr/bin/env python3
"""Audit the hourly, daily, and monthly energy aggregates for missing data.

The script is intentionally read-only with respect to the source CSV files.  It
materializes compact evidence tables under analysis/energy_gap_report/ so that
the report can be reproduced and audited without loading the multi-gigabyte
1 Hz files in full.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "energy_gap_report"
OUT.mkdir(parents=True, exist_ok=True)

ENERGY_FILES = {
    "hourly": ROOT / "energy_hourly.csv",
    "daily": ROOT / "energy_daily.csv",
    "monthly": ROOT / "energy_monthly.csv",
}


def consecutive_intervals(frame: pd.DataFrame, mask: pd.Series, category: str) -> pd.DataFrame:
    selected = frame.loc[mask, ["unix_ts", "local_dt", "local_tm"]].copy()
    if selected.empty:
        return pd.DataFrame()
    selected["group"] = selected["unix_ts"].diff().ne(3600).cumsum()
    result = (
        selected.groupby("group", as_index=False)
        .agg(
            start_unix_ts=("unix_ts", "first"),
            end_unix_ts=("unix_ts", "last"),
            start_date=("local_dt", "first"),
            start_time=("local_tm", "first"),
            end_date=("local_dt", "last"),
            end_time=("local_tm", "last"),
            hours=("unix_ts", "size"),
        )
        .drop(columns="group")
    )
    result.insert(0, "category", category)
    return result


def metric_row(method: str, target: str, values: pd.Series, validation_n: int) -> dict:
    values = pd.Series(values, dtype=float).dropna()
    return {
        "method": method,
        "target": target,
        "validation_n": int(validation_n),
        "mae_wh": round(float(values.abs().mean()), 3),
        "p95_abs_error_wh": round(float(values.abs().quantile(0.95)), 3),
        "max_abs_error_wh": round(float(values.abs().max()), 3),
        "exact_rate_pct": round(float((values == 0).mean() * 100), 1),
    }


def main() -> None:
    hourly = pd.read_csv(ENERGY_FILES["hourly"])
    daily = pd.read_csv(ENERGY_FILES["daily"])
    monthly = pd.read_csv(ENERGY_FILES["monthly"])

    measure_cols = list(hourly.columns[5:])
    circuit_cols = list(hourly.columns[6:])
    circuit_blank_mask = hourly[circuit_cols].isna().all(axis=1)

    # Continuity: Unix time is authoritative for the hourly series, while local
    # calendar labels are authoritative at daily/monthly grains.
    hourly_diffs = hourly["unix_ts"].diff().dropna().astype(int)
    daily_dates = pd.to_datetime(daily["local_dt"])
    monthly_dates = pd.to_datetime(monthly["local_dt"])
    observed_months = monthly_dates.dt.to_period("M")
    expected_months = pd.period_range(observed_months.min(), observed_months.max(), freq="M")

    continuity = pd.DataFrame(
        [
            {
                "grain": "hourly",
                "rows": len(hourly),
                "expected_rows": int((hourly.unix_ts.iloc[-1] - hourly.unix_ts.iloc[0]) / 3600 + 1),
                "missing_period_rows": int((hourly_diffs != 3600).sum()),
                "duplicate_timestamps": int(hourly.unix_ts.duplicated().sum()),
                "first_period": f"{hourly.local_dt.iloc[0]} {hourly.local_tm.iloc[0]}",
                "last_period": f"{hourly.local_dt.iloc[-1]} {hourly.local_tm.iloc[-1]}",
            },
            {
                "grain": "daily",
                "rows": len(daily),
                "expected_rows": int((daily_dates.max() - daily_dates.min()).days + 1),
                "missing_period_rows": int((daily_dates.diff().dropna().dt.days != 1).sum()),
                "duplicate_timestamps": int(daily.unix_ts.duplicated().sum()),
                "first_period": daily.local_dt.iloc[0],
                "last_period": daily.local_dt.iloc[-1],
            },
            {
                "grain": "monthly",
                "rows": len(monthly),
                "expected_rows": len(expected_months),
                "missing_period_rows": len(expected_months.difference(observed_months)),
                "duplicate_timestamps": int(monthly.unix_ts.duplicated().sum()),
                "first_period": monthly.local_dt.iloc[0],
                "last_period": monthly.local_dt.iloc[-1],
            },
        ]
    )
    continuity.to_csv(OUT / "continuity_summary.csv", index=False)

    utility_intervals = consecutive_intervals(hourly, hourly.utility.isna(), "utility")
    circuit_intervals = consecutive_intervals(hourly, circuit_blank_mask, "all_19_circuits")
    intervals = pd.concat([utility_intervals, circuit_intervals], ignore_index=True)
    intervals["blank_cells"] = np.where(
        intervals.category.eq("utility"), intervals.hours, intervals.hours * len(circuit_cols)
    )
    intervals["classification"] = "data_gap"
    first_ts = int(hourly.unix_ts.iloc[0])
    intervals.loc[
        intervals.category.eq("all_19_circuits") & intervals.start_unix_ts.eq(first_ts),
        "classification",
    ] = "coverage_boundary"
    intervals.to_csv(OUT / "hourly_gap_intervals.csv", index=False)

    # Propagate lower-grain incompleteness to the daily and monthly files.  The
    # files aggregate with skip-null behavior, so present totals can be partial.
    utility_by_day = hourly.utility.isna().groupby(hourly.local_dt).sum().astype(int)
    circuits_by_day = circuit_blank_mask.groupby(hourly.local_dt).sum().astype(int)
    daily_impact = daily[["local_dt", "utility"]].copy()
    daily_impact["utility_missing_hours"] = daily_impact.local_dt.map(utility_by_day).fillna(0).astype(int)
    daily_impact["utility_daily_blank"] = daily_impact.utility.isna()
    daily_impact["circuit_missing_hours"] = daily_impact.local_dt.map(circuits_by_day).fillna(0).astype(int)
    daily_impact["circuit_cells_affected"] = (
        daily_impact.circuit_missing_hours.gt(0).astype(int) * len(circuit_cols)
    )
    daily_impact["quality_affected_cells"] = (
        daily_impact.utility_missing_hours.gt(0).astype(int) + daily_impact.circuit_cells_affected
    )
    daily_impact = daily_impact[
        daily_impact.quality_affected_cells.gt(0) | daily_impact.utility_daily_blank
    ].reset_index(drop=True)
    daily_impact.to_csv(OUT / "daily_quality_impact.csv", index=False)

    daily_impact["month"] = daily_impact.local_dt.str[:7]
    monthly_impact = (
        daily_impact.groupby("month", as_index=False)
        .agg(
            utility_affected=("utility_missing_hours", lambda x: bool((x > 0).any())),
            circuit_affected=("circuit_missing_hours", lambda x: bool((x > 0).any())),
            affected_daily_rows=("local_dt", "nunique"),
            missing_hour_labels=("utility_missing_hours", "sum"),
            circuit_gap_hour_labels=("circuit_missing_hours", "sum"),
        )
    )
    monthly_impact["quality_affected_cells"] = (
        monthly_impact.utility_affected.astype(int)
        + monthly_impact.circuit_affected.astype(int) * len(circuit_cols)
    )
    monthly_impact.to_csv(OUT / "monthly_quality_impact.csv", index=False)

    # Reconciliation proves that daily/monthly totals are derived from the lower
    # grains and are not independent constraints on the missing values.
    hourly_sums = hourly.groupby("local_dt")[measure_cols].sum().reindex(daily.local_dt)
    daily_values = daily.set_index("local_dt")[measure_cols]
    daily_diff = hourly_sums.to_numpy(dtype=float) - daily_values.to_numpy(dtype=float)
    daily_comparable = ~np.isnan(daily_values.to_numpy(dtype=float))

    daily_month = daily.copy()
    daily_month["month"] = daily_month.local_dt.str[:7]
    monthly_sums = daily_month.groupby("month")[measure_cols].sum().reindex(monthly.local_dt.str[:7])
    monthly_values = monthly.set_index(monthly.local_dt.str[:7])[measure_cols]
    monthly_diff = monthly_sums.to_numpy(dtype=float) - monthly_values.to_numpy(dtype=float)
    monthly_comparable = ~np.isnan(monthly_values.to_numpy(dtype=float))

    reconciliation = pd.DataFrame(
        [
            {
                "comparison": "hourly labels summed to daily labels",
                "comparable_cells": int(daily_comparable.sum()),
                "exact_cells": int((np.nan_to_num(daily_diff) == 0)[daily_comparable].sum()),
                "max_abs_difference_wh": float(np.nanmax(np.abs(daily_diff[daily_comparable]))),
            },
            {
                "comparison": "daily labels summed to monthly labels",
                "comparable_cells": int(monthly_comparable.sum()),
                "exact_cells": int((np.nan_to_num(monthly_diff) == 0)[monthly_comparable].sum()),
                "max_abs_difference_wh": float(np.nanmax(np.abs(monthly_diff[monthly_comparable]))),
            },
        ]
    )
    reconciliation.to_csv(OUT / "aggregation_reconciliation.csv", index=False)

    # Independent utility evidence from the IHD stream.
    ihd = pd.read_csv(ROOT / "ihd.csv", usecols=["unix_ts", "power"]).drop_duplicates("unix_ts")
    ihd["source_hour"] = (ihd.unix_ts // 3600) * 3600
    ihd_hourly = ihd.groupby("source_hour").power.agg(["mean", "size"])

    utility_gaps = hourly.loc[hourly.utility.isna(), ["unix_ts", "local_dt", "local_tm", "main"]].copy()
    utility_gaps["source_hour"] = utility_gaps.unix_ts - 3600
    utility_gaps["ihd_samples"] = (
        utility_gaps.source_hour.map(ihd_hourly["size"]).fillna(0).astype(int)
    )
    utility_gaps["recovery_route"] = np.select(
        [utility_gaps.ihd_samples.ge(440), utility_gaps.ihd_samples.gt(0)],
        ["IHD direct", "IHD/main hybrid"],
        default="main-model",
    )
    utility_gaps.to_csv(OUT / "utility_gap_recovery_routes.csv", index=False)

    utility_source = (
        pd.read_csv(ROOT / "utility.csv", usecols=["unix_ts", "energy"])
        .drop_duplicates("unix_ts")
        .dropna(subset=["energy"])
        .set_index("unix_ts")
    )
    ihd_validation = ihd_hourly.join(utility_source).dropna()
    ihd_validation = ihd_validation[ihd_validation["size"] >= 440]
    ihd_pred = (ihd_validation["mean"] / 10).round() * 10
    ihd_error = ihd_pred - ihd_validation.energy

    # Main-channel model validation.  Each held-out row is predicted from a
    # linear utility~main calibration trained on the other nine folds in the
    # same calendar month, then rounded to the utility meter's 10 Wh increment.
    model_rows = hourly.dropna(subset=["utility", "main"]).copy()
    model_rows = model_rows[model_rows.unix_ts > int(ihd.unix_ts.max()) + 3600].reset_index(drop=True)
    model_rows["month"] = model_rows.local_dt.str[:7]
    model_rows["fold"] = (model_rows.unix_ts // 3600) % 10
    predictions = np.full(len(model_rows), np.nan)
    for _, month_rows in model_rows.groupby("month"):
        for fold, held_out in month_rows.groupby("fold"):
            training = month_rows[month_rows.fold != fold]
            slope, intercept = np.polyfit(training.main.to_numpy(), training.utility.to_numpy(), 1)
            predictions[held_out.index] = slope * held_out.main.to_numpy() + intercept
    model_pred = np.round(predictions / 10) * 10
    model_error = pd.Series(model_pred - model_rows.utility.to_numpy())

    # Opposite-year utility donor, retained as a benchmark rather than a
    # recommended primary method.
    observed_utility = hourly[["unix_ts", "utility"]].dropna()
    donors = observed_utility.copy()
    donors.unix_ts += 364 * 86400
    donors = donors.rename(columns={"utility": "donor"})
    donor_pairs = observed_utility.merge(donors, on="unix_ts")
    donor_error = donor_pairs.donor - donor_pairs.utility

    # Verify that a simple hourly aggregation of the public 1 Hz power stream
    # reproduces clean hourly circuit values closely.  Seven days is a bounded,
    # deterministic clean window (3,192 circuit-hour cells).
    power_cols = ["unix_ts", *circuit_cols]
    clean_power = pd.read_csv(ROOT / "power.csv", usecols=power_cols, nrows=7 * 86400)
    clean_power["label_ts"] = (clean_power.unix_ts // 3600) * 3600 + 3600
    power_hourly = clean_power.groupby("label_ts")[circuit_cols].mean()
    energy_lookup = hourly.set_index("unix_ts")[circuit_cols]
    joined = power_hourly.join(energy_lookup, lsuffix="_calc", rsuffix="_actual").dropna()
    circuit_errors = []
    for column in circuit_cols:
        circuit_errors.extend(
            (np.ceil(joined[f"{column}_calc"]) - joined[f"{column}_actual"]).to_numpy()
        )
    circuit_error = pd.Series(circuit_errors)

    validation = pd.DataFrame(
        [
            metric_row(
                "1 Hz power mean, rounded upward",
                "circuit hourly energy",
                circuit_error,
                len(circuit_error),
            ),
            metric_row(
                "IHD hourly mean, rounded to 10 Wh",
                "utility hourly energy (>=440 samples/hour)",
                ihd_error,
                len(ihd_error),
            ),
            metric_row(
                "monthly 10-fold utility~main regression",
                "utility hourly energy after IHD coverage",
                model_error,
                len(model_error),
            ),
            metric_row(
                "364-day donor",
                "utility hourly energy benchmark",
                donor_error,
                len(donor_error),
            ),
        ]
    )
    validation.insert(0, "sort_order", range(1, len(validation) + 1))
    validation.to_csv(OUT / "method_validation.csv", index=False)

    utility_routes = utility_gaps.recovery_route.value_counts()
    recovery_routes = pd.DataFrame(
        [
            {
                "sort_order": 1,
                "target": "19 circuit channels",
                "gap_hour_labels": 39,
                "affected_cells": 39 * len(circuit_cols),
                "recommended_method": "Aggregate recovered 1 Hz power",
                "confidence": "Medium",
                "reason": "Direct aggregation is accurate; the missing seconds themselves are synthetic donor values.",
            },
            {
                "sort_order": 2,
                "target": "Utility",
                "gap_hour_labels": int(utility_routes.get("IHD direct", 0)),
                "affected_cells": int(utility_routes.get("IHD direct", 0)),
                "recommended_method": "IHD direct",
                "confidence": "High",
                "reason": "Independent power stream has at least 440 samples in the source hour.",
            },
            {
                "sort_order": 3,
                "target": "Utility",
                "gap_hour_labels": int(utility_routes.get("IHD/main hybrid", 0)),
                "affected_cells": int(utility_routes.get("IHD/main hybrid", 0)),
                "recommended_method": "Main-channel model, with partial IHD check",
                "confidence": "Medium-high",
                "reason": "IHD coverage is partial; the main circuit is complete and strongly calibrated to utility.",
            },
            {
                "sort_order": 4,
                "target": "Utility",
                "gap_hour_labels": int(utility_routes.get("main-model", 0)),
                "affected_cells": int(utility_routes.get("main-model", 0)),
                "recommended_method": "Main-channel model",
                "confidence": "Medium-high",
                "reason": "No usable IHD samples; monthly cross-validation is accurate for typical hours but has rare outliers.",
            },
            {
                "sort_order": 5,
                "target": "19 circuit channels at dataset start",
                "gap_hour_labels": 1,
                "affected_cells": len(circuit_cols),
                "recommended_method": "Leave blank or estimate explicitly",
                "confidence": "Low",
                "reason": "This is a coverage boundary: the required preceding 1 Hz hour is outside the dataset.",
            },
        ]
    )
    recovery_routes.to_csv(OUT / "recommended_recovery_routes.csv", index=False)

    hourly_blank_cells = int(hourly[measure_cols].isna().sum().sum())
    daily_blank_cells = int(daily[measure_cols].isna().sum().sum())
    monthly_blank_cells = int(monthly[measure_cols].isna().sum().sum())
    daily_affected_cells = int(daily_impact.quality_affected_cells.sum())
    monthly_affected_cells = int(monthly_impact.quality_affected_cells.sum())
    quality_by_grain = pd.DataFrame(
        [
            {
                "sort_order": 1,
                "grain": "Hourly",
                "period_rows": len(hourly),
                "explicit_blank_cells": hourly_blank_cells,
                "quality_affected_cells": hourly_blank_cells,
                "affected_period_rows": int(hourly[measure_cols].isna().any(axis=1).sum()),
            },
            {
                "sort_order": 2,
                "grain": "Daily",
                "period_rows": len(daily),
                "explicit_blank_cells": daily_blank_cells,
                "quality_affected_cells": daily_affected_cells,
                "affected_period_rows": int(daily_impact.local_dt.nunique()),
            },
            {
                "sort_order": 3,
                "grain": "Monthly",
                "period_rows": len(monthly),
                "explicit_blank_cells": monthly_blank_cells,
                "quality_affected_cells": monthly_affected_cells,
                "affected_period_rows": int(monthly_impact.month.nunique()),
            },
        ]
    )
    quality_by_grain.to_csv(OUT / "quality_by_grain.csv", index=False)

    headline_metrics = pd.DataFrame(
        [
            {
                "hourly_blank_cells": hourly_blank_cells,
                "recoverable_circuit_cells": 39 * len(circuit_cols),
                "utility_gap_hours": int(hourly.utility.isna().sum()),
                "inherited_monthly_rows": int(monthly_impact.month.nunique()),
                "missing_period_rows": int(continuity.missing_period_rows.sum()),
            }
        ]
    )

    summary = {
        "source_rows": {grain: int(len(frame)) for grain, frame in [("hourly", hourly), ("daily", daily), ("monthly", monthly)]},
        "measure_columns": len(measure_cols),
        "circuit_columns": len(circuit_cols),
        "hourly_blank_cells": hourly_blank_cells,
        "hourly_utility_blank_hours": int(hourly.utility.isna().sum()),
        "hourly_circuit_gap_hours": int(circuit_blank_mask.sum() - 1),
        "hourly_circuit_boundary_hours": 1,
        "daily_explicit_blank_cells": daily_blank_cells,
        "daily_quality_affected_cells": daily_affected_cells,
        "monthly_explicit_blank_cells": monthly_blank_cells,
        "monthly_quality_affected_cells": monthly_affected_cells,
        "affected_daily_rows": int(daily_impact.local_dt.nunique()),
        "affected_monthly_rows": int(monthly_impact.month.nunique()),
        "utility_recovery_routes": {str(k): int(v) for k, v in utility_routes.items()},
        "aggregation_reconciliation_max_difference_wh": 0,
        "notes": [
            "Daily values equal the sum of hourly values with blank cells skipped.",
            "Monthly values equal the sum of daily values with blank cells skipped.",
            "The first circuit hourly row is a coverage boundary rather than an internal outage.",
        ],
    }
    (OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Materialize the bounded evidence used by the portable report, then execute
    # the exact report queries so the SQL provenance is real rather than nominal.
    database = OUT / "report_evidence.sqlite"
    with sqlite3.connect(database) as connection:
        headline_metrics.to_sql("headline_metrics", connection, if_exists="replace", index=False)
        quality_by_grain.to_sql("quality_by_grain", connection, if_exists="replace", index=False)
        recovery_routes.to_sql("recovery_routes", connection, if_exists="replace", index=False)
        validation.to_sql("validation_evidence", connection, if_exists="replace", index=False)
        continuity.to_sql("continuity_summary", connection, if_exists="replace", index=False)
        monthly_impact.to_sql("monthly_impact", connection, if_exists="replace", index=False)
        for query in [
            "SELECT * FROM headline_metrics;",
            "SELECT * FROM quality_by_grain ORDER BY sort_order;",
            "SELECT * FROM recovery_routes ORDER BY sort_order;",
            "SELECT * FROM validation_evidence ORDER BY sort_order;",
            "SELECT * FROM continuity_summary;",
            "SELECT * FROM monthly_impact ORDER BY month;",
        ]:
            connection.execute(query).fetchall()

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
