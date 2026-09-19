# Missing-data recovery package

This directory preserves the code and compact evidence used to create the canonical recovered R1Hz files. The multi-gigabyte CSV outputs themselves are distributed through Harvard Dataverse under their root-level canonical names.

## Method summary

Two long circuit-data outages were filled by same-channel substitution from a 364-day offset, preserving weekday and local clock time. Thirteen isolated real-power seconds were estimated with channel-local regression on `current * power_factor`; the matching reactive-power seconds were interpolated between their nearest valid temporal neighbours. Blank or nonnumeric target circuit cells were populated. Valid observed values, timestamps, and the sparse IHD field were preserved.

Two ANSI escape sequences were found in the original current stream. A nonnumeric `gen2` token at Unix timestamp 1528539825 was treated as missing and replaced by the verified donor value `0.0`. Three control bytes embedded in the local time at timestamp 1528571381 were removed, restoring `12:09:41`; the same copied metadata was repaired in `voltage.csv`. These exact corrections are implemented by [`repair_1hz_control_sequences.py`](scripts/repair_1hz_control_sequences.py), and neither changes the affected rows' `s` status.

Voltage is a separate directly measured stream decoded from PowerScout Modbus registers 4058 and 4059 at their native 0.1 V resolution. Single-leg channels use the voltage measured on their actual panel leg; `main` and `dryr` sum their two leg-to-neutral values. The 133,261 long-gap seconds use a 364-day measured voltage donor, calibrated per channel with the one-hour median target-minus-donor offsets before and after each gap. The offsets are blended across the gap and tapered to the exact adjacent residual during the first and last 10 minutes. Fifty-two short gaps totalling 64 seconds use bracketing linear interpolation. All estimates are quantized to 0.1 V.

Three missing bank-G cells at 2019-06-01 02:32:33 use the same-second mains-bank voltage and make that row synthetic. Two cells at 07:19:53 were salvaged as measured values from a complete bank-A record embedded in a malformed raw line. Every voltage row containing an estimate is marked `s`; the directly salvaged observations are not synthetic.

Hourly circuit gaps were rebuilt from recovered 1 Hz real power. Utility gaps used an hourly Eagle 200 mean where at least 440 samples were available, otherwise a month-local utility-to-main calibration with partial IHD observations used as a check when present. Daily and monthly products were rebuilt from the recovered hourly file.

Every affected row is marked `s`. For daily and monthly rows, the marker propagates when at least one lower-grain input is synthetic.

The `climate.csv` correction is a separate format repair, not missing-data imputation. In 402 rows, a compound `weather` description contained one or two unquoted commas, which made those records parse as 16 or 17 columns. [`repair_climate_csv.py`](scripts/repair_climate_csv.py) quotes only the complete final field on those rows. All 18,984 semantic records are preserved, so these rows are not marked `s`.

## Contents

| Path | Contents |
|---|---|
| `scripts/` | C full-file scanners/recovery programs and Python analysis/aggregate scripts |
| `method_inputs/` | Exact estimates and provenance for the 13 isolated seconds |
| `recovery_summary.csv` | Final counts for the original four 1 Hz files |
| `energy/cell_recovery_log.csv` | One row per reconstructed hourly energy cell |
| `energy/recovery_summary.json` | Energy recovery counts |
| `energy/validation_summary.json` | Reconciliation and validation receipt |
| `scripts/repair_climate_csv.py` | Minimal, byte-preserving climate CSV format repair |
| `scripts/repair_1hz_control_sequences.py` | Exact current/voltage control-sequence repair with atomic replacement |
| `control_sequence_repair.json` | Exact anomaly locations, corrections, final checksums, and validation receipt |
| `climate_format_repair.json` | Input/output checksums and climate repair validation receipt |
| `voltage_validation_summary.json` | Final voltage counts, checksum, recovery scope, and validation receipt |

## Verified results

The four recovered 1 Hz files each contain 65,404,800 consecutive timestamp rows. No blank or nonnumeric circuit measurements remain, and no valid originally observed circuit values changed. Filled-cell counts were 2,531,959 (`current.csv`), 2,531,959 (`power_factor.csv`), and 2,532,206 each (`power.csv` and `reactive.csv`).

The completed `voltage.csv` also contains 65,404,800 consecutive timestamp rows. It has no blank voltage cells, 133,326 rows marked `s`, and 2,533,178 imputed cells: 133,325 fully blank seconds across 54 gaps plus three same-second mains-proxy cells. Two additional cells were recovered as direct raw observations. The final file has 23 fields per row, one decimal place for every voltage, and 9,549,234,246 bytes (8.893 GiB). Its SHA-256 checksum is `7512563edccf8cd47ac244646f2f2a15c5b9ff72e6c8bb4d8a999649d7be103a`. The 0.1 V formatting reflects register resolution, not the accuracy of imputed values.

The recovered hourly product contains 876 reconstructed cells: 741 circuit cells, 90 utility cells from native IHD hourly means, 14 utility cells from the month-local model with a partial-IHD check, and 31 utility cells from that model without IHD coverage. Nineteen boundary circuit blanks remain intentionally on the first hourly row. Daily and monthly energy files contain no blanks, and their reconciliations have a maximum absolute difference of 0 Wh.

The repaired climate file has 18,984 data rows and exactly 15 columns under a strict CSV parser. Only 402 physical lines changed, by adding 804 quote characters around compound weather values. Its SHA-256 checksum is `87bcf8ee1167b9799188229c68a79597c2092d662107218018a0df83c725fa10`; the parsed values before and after repair are identical.

## Reproduction notes

The recovery programs were designed to preserve unrecovered source CSVs as read-only inputs and write derived copies under a separate `recovered/` directory. Re-running the complete pipeline therefore requires an unrecovered source snapshot in the repository root plus the intermediate evidence generated by the audit/extraction steps. The public canonical files are already recovered and must not be used as if they were the unrecovered inputs.

Python scripts require Python 3, NumPy, and pandas for the original recovery analyses; the voltage scripts use only the Python standard library. The C utilities use only the standard C/POSIX library and can be compiled with a C11 compiler, for example `cc -O2 -std=c11 source.c -o program`. Each command-line C utility prints its usage when invoked without the required arguments. The scripts include explicit count and schema assertions and should stop if their expected source layout is not present.

Run `repair_1hz_control_sequences.py` on the unrecovered current source before the circuit recovery, then run `decode_modbus_voltage.py` against the retained `raw_modbus/` files and the corrected canonical 1 Hz timeline. Finish with `impute_voltage.py` and `validate_imputed_voltage.py`. `compact_voltage_precision.py` is the audited one-time migration from the earlier redundant three-decimal representation to the canonical one-decimal representation; it changes formatting only. The unit tests cover the control-sequence repair, panel mapping, native resolution, raw-record salvage, interpolation, and the donor-boundary taper.
