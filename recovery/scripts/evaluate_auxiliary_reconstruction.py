#!/usr/bin/env python3
"""Validate short-gap P/Q reconstruction from contemporaneous current and PF."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


CHANNELS = [
    "main",
    "beda",
    "bedp",
    "boil",
    "chrg",
    "cwsh",
    "dryr",
    "dwsh",
    "frdg",
    "gen1",
    "gen2",
    "gen3",
    "gen4",
    "gen5",
    "gen6",
    "kit1",
    "kit2",
    "outp",
    "vacu",
]


def load_measurements(path: Path, suffix: str) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["unix_ts", *CHANNELS])
    return frame.rename(columns={column: f"{column}_{suffix}" for column in CHANNELS})


def regression_metrics(feature: np.ndarray, target: np.ndarray) -> tuple[int, float, float, float]:
    valid = np.isfinite(feature) & np.isfinite(target)
    feature = feature[valid]
    target = target[valid]
    if len(target) < 20:
        return len(target), np.nan, np.nan, np.nan

    sequence = np.arange(len(target))
    train = sequence % 5 != 0
    test = ~train
    design_train = np.column_stack([np.ones(train.sum()), feature[train]])
    coefficients, *_ = np.linalg.lstsq(design_train, target[train], rcond=None)
    predictions = coefficients[0] + coefficients[1] * feature[test]
    errors = predictions - target[test]
    correlation = np.corrcoef(predictions, target[test])[0, 1]
    return int(test.sum()), float(np.mean(np.abs(errors))), float(np.sqrt(np.mean(errors**2))), float(correlation)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    analysis_dir = root / "analysis" / "imputation"

    current = load_measurements(analysis_dir / "current_aux_windows.csv", "current")
    power_factor = load_measurements(analysis_dir / "power_factor_aux_windows.csv", "pf")
    power = load_measurements(analysis_dir / "power_aux_windows.csv", "power")
    reactive = load_measurements(analysis_dir / "reactive_aux_windows.csv", "reactive")

    merged = current.merge(power_factor, on="unix_ts", validate="one_to_one")
    merged = merged.merge(power, on="unix_ts", validate="one_to_one")
    merged = merged.merge(reactive, on="unix_ts", validate="one_to_one")
    merged["window"] = np.where(merged["unix_ts"] < 1540000000, "2018 local window", "2019 local window")

    result_rows: list[dict[str, object]] = []
    for window, window_frame in merged.groupby("window", sort=True):
        for channel in CHANNELS:
            current_values = window_frame[f"{channel}_current"].to_numpy(dtype=float)
            pf_values = np.clip(window_frame[f"{channel}_pf"].to_numpy(dtype=float), -1.0, 1.0)
            power_values = window_frame[f"{channel}_power"].to_numpy(dtype=float)
            reactive_values = window_frame[f"{channel}_reactive"].to_numpy(dtype=float)

            real_power_feature = current_values * pf_values
            reactive_power_feature = current_values * np.sqrt(np.maximum(0.0, 1.0 - pf_values**2))

            p_count, p_mae, p_rmse, p_corr = regression_metrics(real_power_feature, power_values)
            q_count, q_mae, q_rmse, q_corr = regression_metrics(reactive_power_feature, reactive_values)

            result_rows.append(
                {
                    "window": window,
                    "channel": channel,
                    "power_validation_seconds": p_count,
                    "power_mae_w": p_mae,
                    "power_rmse_w": p_rmse,
                    "power_correlation": p_corr,
                    "reactive_validation_seconds": q_count,
                    "reactive_mae_var": q_mae,
                    "reactive_rmse_var": q_rmse,
                    "reactive_correlation": q_corr,
                }
            )

    results = pd.DataFrame(result_rows)
    results.to_csv(analysis_dir / "auxiliary_reconstruction_validation.csv", index=False, float_format="%.6f")

    main_results = results.loc[results["channel"] == "main"]
    print(main_results.to_string(index=False))
    print()
    print(
        "Median across channels:",
        {
            "power_mae_w": float(results["power_mae_w"].median()),
            "power_correlation": float(results["power_correlation"].median()),
            "reactive_mae_var": float(results["reactive_mae_var"].median()),
            "reactive_correlation": float(results["reactive_correlation"].median()),
        },
    )


if __name__ == "__main__":
    main()
