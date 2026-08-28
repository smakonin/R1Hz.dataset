#!/usr/bin/env python3
"""Create estimates for the 13 P/Q-only missing seconds."""

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

TARGET_GROUPS = [
    range(1528598292, 1528598293),
    range(1559399189, 1559399192),
    range(1559399207, 1559399216),
]
TARGET_TIMESTAMPS = [timestamp for group in TARGET_GROUPS for timestamp in group]


def load_measurements(path: Path, suffix: str) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["unix_ts", *CHANNELS])
    return frame.rename(columns={channel: f"{channel}_{suffix}" for channel in CHANNELS})


def nearest_bracket_interpolation(
    timestamps: np.ndarray,
    values: np.ndarray,
    target_timestamp: int,
) -> float:
    valid = np.isfinite(values)
    before = np.flatnonzero(valid & (timestamps < target_timestamp))
    after = np.flatnonzero(valid & (timestamps > target_timestamp))
    if len(before) == 0 or len(after) == 0:
        raise ValueError(f"No valid interpolation bracket for {target_timestamp}")

    left = before[-1]
    right = after[0]
    fraction = (target_timestamp - timestamps[left]) / (timestamps[right] - timestamps[left])
    return float(values[left] + fraction * (values[right] - values[left]))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    analysis_dir = root / "analysis" / "imputation"
    output_dir = root / "recovered" / "method_inputs"

    current = load_measurements(analysis_dir / "current_aux_windows.csv", "current")
    power_factor = load_measurements(analysis_dir / "power_factor_aux_windows.csv", "pf")
    power = load_measurements(analysis_dir / "power_aux_windows.csv", "power")
    reactive = load_measurements(analysis_dir / "reactive_aux_windows.csv", "reactive")

    merged = current.merge(power_factor, on="unix_ts", validate="one_to_one")
    merged = merged.merge(power, on="unix_ts", validate="one_to_one")
    merged = merged.merge(reactive, on="unix_ts", validate="one_to_one")

    power_estimates: list[dict[str, int]] = []
    reactive_estimates: list[dict[str, int]] = []
    provenance: list[dict[str, object]] = []

    for target_timestamp in TARGET_TIMESTAMPS:
        window_2018 = target_timestamp < 1540000000
        local_window = merged.loc[
            (merged["unix_ts"] < 1540000000) if window_2018 else (merged["unix_ts"] >= 1540000000)
        ]
        target_row = local_window.loc[local_window["unix_ts"] == target_timestamp]
        if len(target_row) != 1:
            raise ValueError(f"Target timestamp not found exactly once: {target_timestamp}")

        power_output: dict[str, int] = {"unix_ts": target_timestamp}
        reactive_output: dict[str, int] = {"unix_ts": target_timestamp}
        timestamps = local_window["unix_ts"].to_numpy(dtype=np.int64)

        for channel in CHANNELS:
            current_values = local_window[f"{channel}_current"].to_numpy(dtype=float)
            pf_values = np.clip(local_window[f"{channel}_pf"].to_numpy(dtype=float), -1.0, 1.0)
            observed_power = local_window[f"{channel}_power"].to_numpy(dtype=float)
            observed_reactive = local_window[f"{channel}_reactive"].to_numpy(dtype=float)

            feature = current_values * pf_values
            train = np.isfinite(feature) & np.isfinite(observed_power)
            design = np.column_stack([np.ones(train.sum()), feature[train]])
            coefficients, *_ = np.linalg.lstsq(design, observed_power[train], rcond=None)

            target_current = float(target_row.iloc[0][f"{channel}_current"])
            target_pf = float(np.clip(target_row.iloc[0][f"{channel}_pf"], -1.0, 1.0))
            power_prediction = coefficients[0] + coefficients[1] * target_current * target_pf
            power_output[channel] = max(0, int(np.rint(power_prediction)))

            reactive_prediction = nearest_bracket_interpolation(
                timestamps,
                observed_reactive,
                target_timestamp,
            )
            reactive_output[channel] = max(0, int(np.rint(reactive_prediction)))

        power_estimates.append(power_output)
        reactive_estimates.append(reactive_output)
        provenance.extend(
            [
                {
                    "unix_ts": target_timestamp,
                    "file": "power.csv",
                    "method": "local channel regression: P = intercept + slope * current * power_factor",
                },
                {
                    "unix_ts": target_timestamp,
                    "file": "reactive.csv",
                    "method": "linear interpolation between nearest valid bracketing seconds",
                },
            ]
        )

    pd.DataFrame(power_estimates).to_csv(
        output_dir / "isolated_power_estimates.csv",
        index=False,
    )
    pd.DataFrame(reactive_estimates).to_csv(
        output_dir / "isolated_reactive_estimates.csv",
        index=False,
    )
    pd.DataFrame(provenance).to_csv(
        output_dir / "isolated_estimate_provenance.csv",
        index=False,
    )

    print(f"Created estimates for {len(TARGET_TIMESTAMPS)} timestamps.")


if __name__ == "__main__":
    main()
