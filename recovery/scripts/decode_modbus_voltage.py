#!/usr/bin/env python3
"""Decode measured PowerScout voltage from the retained Modbus records.

Raw records contain eight bank rows per observed second. Registers 4058 and
4059 (CSV fields 40 and 41, counting from one) are L1-neutral and L2-neutral
voltage, respectively. This installation uses a 0.1 V register scalar. The
third voltage register is not used because the panel has two supply legs.

The circuit-to-leg assignment comes from R1Hz-PowerPanel.pdf, not from the
``meter_l1`` and ``meter_l2`` names in appliances.csv: those names do not
consistently identify the wired electrical leg. Each single-leg circuit gets
its own bank's measured leg voltage. ``main`` and ``dryr`` each combine a
meter on L1 with a meter on L2; their single CSV value is the sum of those
two measured leg-to-neutral voltages (an approximate line-to-line voltage
for this split-phase panel), not a directly read line-to-line register.

If a circuit's own voltage register is zero and the matching register in
bank A (mains) is nonzero, the mains measurement is substituted and the row
is marked ``s``. An absent bank or entirely absent raw second is left blank;
the marker is not copied from the timeline file because that marker describes
different measurements. Output uses one decimal place, matching the native
0.1 V voltage resolution.

Source: DENT PowerScout 24 Operator's Guide, Table 7 and Modbus offsets
4058-4060: https://www.dentinstruments.com/wp-content/uploads/2022/09/PS24_Manual.pdf

Example:
    python3 recovery/scripts/decode_modbus_voltage.py \\
        --raw-dir /path/to/raw_modbus \\
        --timeline current.csv --output voltage.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Iterator


DATASET_ROOT = Path(__file__).resolve().parents[2]
BASE_FIELDS = ("unix_ts", "marker", "date", "time")
CHANNELS = (
    "main", "beda", "bedp", "boil", "chrg", "cwsh", "dryr", "dwsh", "frdg",
    "gen1", "gen2", "gen3", "gen4", "gen5", "gen6", "kit1", "kit2", "outp", "vacu",
)

# CT number -> actual panel phase leg, transcribed from R1Hz-PowerPanel.pdf.
PANEL_LEG = {
    1: 2, 2: 1, 3: 2, 4: 2, 5: 1, 6: 1, 7: 2, 8: 2,
    9: 1, 10: 1, 11: 2, 12: 2, 13: 1, 14: 1, 15: 2, 16: 2,
    17: 1, 18: 1, 19: 2, 20: 2, 21: 1, 22: 1, 23: 2, 24: 2,
}
BANKS = frozenset(b"ABCDEFGH")


def output_specs(
    appliances_path: Path,
) -> tuple[tuple[str, tuple[tuple[int, int], ...]], ...]:
    """Return (field, ((bank, leg), ...)) in circuit order."""
    with appliances_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"appliance_id", "meter_l1", "meter_l2"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"unexpected appliances schema: {appliances_path}")
        meters = {
            row["appliance_id"].strip().lower(): tuple(
                int(row[field]) for field in ("meter_l1", "meter_l2") if row[field].strip()
            )
            for row in reader
        }
    if set(meters) != set(CHANNELS):
        raise ValueError("appliances IDs differ from circuit columns")

    specs: list[tuple[str, tuple[tuple[int, int], ...]]] = []
    for channel in CHANNELS:
        channel_meters = meters[channel]
        if channel in {"main", "dryr"}:
            if len(channel_meters) != 2 or {PANEL_LEG[m] for m in channel_meters} != {1, 2}:
                raise ValueError(f"{channel} must have one CT on each leg")
            legs = []
            for leg in (1, 2):
                meter = next(m for m in channel_meters if PANEL_LEG[m] == leg)
                legs.append(((meter - 1) // 3, leg))
            specs.append((channel, tuple(legs)))
        else:
            if len(channel_meters) != 1:
                raise ValueError(f"{channel} must have one CT")
            meter = channel_meters[0]
            specs.append((channel, (((meter - 1) // 3, PANEL_LEG[meter]),)))
    return tuple(specs)


def raw_seconds(
    raw_dir: Path, stats: dict[str, int]
) -> Iterator[tuple[int, dict[int, tuple[int, int]]]]:
    """Stream grouped bank voltages, tolerating and counting malformed records."""
    files = sorted(raw_dir.glob("SUB_????-??-??.csv"))
    if not files:
        raise FileNotFoundError(f"no SUB_YYYY-MM-DD.csv files in {raw_dir}")
    stats["raw_files"] = len(files)
    previous_ts_bytes: bytes | None = None
    bank_values: dict[int, tuple[int, int]] = {}
    for path in files:
        with path.open("rb", buffering=1024 * 1024) as stream:
            for line_number, line in enumerate(stream, 1):
                if line.count(b",") != 44:
                    stats["malformed_raw_rows"] += 1
                    if stats["malformed_raw_rows"] <= 5:
                        print(f"skipping malformed raw row {path}:{line_number}", file=sys.stderr)
                    continue
                ts_bytes, sep, remainder = line.partition(b",")
                bank_bytes, sep2, register_bytes = remainder.partition(b",")
                if not sep or not sep2 or len(bank_bytes) != 1 or bank_bytes[0] not in BANKS:
                    stats["malformed_raw_rows"] += 1
                    continue
                if ts_bytes != previous_ts_bytes:
                    if previous_ts_bytes is not None:
                        yield int(previous_ts_bytes), bank_values
                    if previous_ts_bytes is not None and int(ts_bytes) <= int(previous_ts_bytes):
                        raise ValueError(f"raw timestamps not increasing at {path}:{line_number}")
                    previous_ts_bytes = ts_bytes
                    bank_values = {}
                last_registers = register_bytes.rstrip(b"\r\n").rsplit(b",", 6)
                try:
                    voltage = (int(last_registers[1]), int(last_registers[2]))
                except (IndexError, ValueError) as exc:
                    stats["malformed_raw_rows"] += 1
                    if stats["malformed_raw_rows"] <= 5:
                        print(f"skipping unparseable raw row {path}:{line_number}: {exc}", file=sys.stderr)
                    continue
                if voltage[0] == 0:
                    stats["raw_zero_l1_rows"] += 1
                if voltage[1] == 0:
                    stats["raw_zero_l2_rows"] += 1
                bank_number = bank_bytes[0] - ord("A")
                prior = bank_values.get(bank_number)
                if prior is not None:
                    stats["duplicate_bank_rows"] += 1
                    if prior != voltage:
                        stats["conflicting_bank_rows"] += 1
                    continue
                bank_values[bank_number] = voltage
    if previous_ts_bytes is not None:
        yield int(previous_ts_bytes), bank_values


def voltage_text(raw_tenths: int) -> str:
    """Express a 0.1 V native register value with one decimal place."""
    if raw_tenths < 0:
        raise ValueError("negative voltage register")
    return f"{raw_tenths // 10}.{raw_tenths % 10}"


def decode_voltage(
    raw_dir: Path,
    timeline: Path,
    appliances: Path,
    output: Path,
    *,
    expected_rows: int | None = None,
    overwrite: bool = False,
    progress_rows: int = 1_000_000,
) -> dict[str, int | str]:
    raw_dir, timeline, appliances, output = (
        raw_dir.resolve(), timeline.resolve(), appliances.resolve(), output.resolve()
    )
    if output.exists() and not overwrite:
        raise FileExistsError(f"output exists (pass --overwrite to replace): {output}")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"output directory does not exist: {output.parent}")
    specs = output_specs(appliances)
    header = BASE_FIELDS + tuple(field for field, _ in specs)
    stats = {
        "rows": 0,
        "raw_files": 0,
        "observed_raw_seconds": 0,
        "raw_missing_seconds": 0,
        "malformed_raw_rows": 0,
        "raw_zero_l1_rows": 0,
        "raw_zero_l2_rows": 0,
        "duplicate_bank_rows": 0,
        "conflicting_bank_rows": 0,
        "missing_bank_values": 0,
        "mains_fallback_values": 0,
        "mains_fallback_rows": 0,
        "decoded_values": 0,
    }
    temp_path: Path | None = None
    try:
        with timeline.open("r", encoding="utf-8", newline="") as timeline_stream:
            timeline_header = tuple(timeline_stream.readline().rstrip("\r\n").split(","))
            if timeline_header != BASE_FIELDS + CHANNELS:
                raise ValueError(f"unexpected timeline schema: {timeline_header!r}")
            raw_iterator = raw_seconds(raw_dir, stats)
            raw_item = next(raw_iterator, None)
            handle, name = tempfile.mkstemp(prefix=".voltage-", suffix=".csv.tmp", dir=output.parent)
            temp_path = Path(name)
            with os.fdopen(handle, "w", encoding="utf-8", newline="", buffering=1024 * 1024) as output_stream:
                writer = csv.writer(output_stream, lineterminator="\n")
                writer.writerow(header)
                previous_ts: int | None = None
                for line in timeline_stream:
                    base = line.split(",", 4)
                    if len(base) != 5:
                        raise ValueError(f"malformed timeline row {stats['rows'] + 1:,}")
                    timestamp = int(base[0])
                    if previous_ts is not None and timestamp != previous_ts + 1:
                        raise ValueError(f"nonconsecutive timeline timestamp at row {stats['rows'] + 1:,}")
                    previous_ts = timestamp
                    while raw_item is not None and raw_item[0] < timestamp:
                        raw_item = next(raw_iterator, None)

                    output_row = [base[0], "", base[2], base[3]]
                    if raw_item is None or raw_item[0] != timestamp:
                        output_row.extend([""] * len(specs))
                        stats["raw_missing_seconds"] += 1
                    else:
                        banks = raw_item[1]
                        mains = banks.get(0)
                        fallback_row = False
                        for _, leg_sources in specs:
                            raw_total = 0
                            missing = False
                            for bank, leg in leg_sources:
                                own = banks.get(bank)
                                if own is None:
                                    missing = True
                                    stats["missing_bank_values"] += 1
                                    continue
                                raw_voltage = own[leg - 1]
                                if raw_voltage == 0 and mains is not None and mains[leg - 1] != 0:
                                    raw_voltage = mains[leg - 1]
                                    stats["mains_fallback_values"] += 1
                                    fallback_row = True
                                raw_total += raw_voltage
                            if missing:
                                output_row.append("")
                            else:
                                output_row.append(voltage_text(raw_total))
                                stats["decoded_values"] += 1
                        if fallback_row:
                            output_row[1] = "s"
                            stats["mains_fallback_rows"] += 1
                        stats["observed_raw_seconds"] += 1
                        raw_item = next(raw_iterator, None)
                    writer.writerow(output_row)
                    stats["rows"] += 1
                    if progress_rows and stats["rows"] % progress_rows == 0:
                        print(f"decoded {stats['rows']:,} seconds", file=sys.stderr, flush=True)

                if expected_rows is not None and stats["rows"] != expected_rows:
                    raise ValueError(f"expected {expected_rows:,} rows, found {stats['rows']:,}")
                output_stream.flush()
                os.fsync(output_stream.fileno())
        if output.exists() and not overwrite:
            raise FileExistsError(f"output appeared during processing: {output}")
        os.replace(temp_path, output)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return {**stats, "output": str(output), "raw_dir": str(raw_dir)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DATASET_ROOT / "raw_modbus")
    parser.add_argument("--timeline", type=Path, default=DATASET_ROOT / "current.csv")
    parser.add_argument("--appliances", type=Path, default=DATASET_ROOT / "appliances.csv")
    parser.add_argument("--output", type=Path, default=DATASET_ROOT / "voltage.csv")
    parser.add_argument("--expected-rows", type=int, default=None)
    parser.add_argument("--progress-rows", type=int, default=1_000_000)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = decode_voltage(
        args.raw_dir, args.timeline, args.appliances, args.output,
        expected_rows=args.expected_rows, overwrite=args.overwrite,
        progress_rows=args.progress_rows,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
