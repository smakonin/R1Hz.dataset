#!/usr/bin/env python3
"""Complete voltage.csv without changing any already measured voltage.

The 19 voltage columns were decoded from raw PowerScout Modbus registers by
decode_modbus_voltage.py. Two long raw-record outages are filled from the
measured voltage trace 364 days away (same weekday and local clock time).
For each channel, the donor is shifted by the median target-minus-donor
difference in the measured hour before and after the outage. The two median
offsets are blended through the gap. Over the first and last ten minutes,
the offset also tapers to the exact adjacent measured boundary difference;
this avoids an artificial step at either join. Short gaps (1--9 seconds)
are linearly interpolated between adjacent measurements.

Two partly decoded seconds beside the 2019 outage are repaired directly from
the retained raw file. The complete bank-A record embedded in one malformed
line gives two genuine observations; three absent bank-G voltages in the
other second use the same-second mains bank as a proxy. Every row containing
an estimate, including this proxy, receives marker ``s``. Native registers
resolve 0.1 V; estimates are quantized to that resolution and represented
with one decimal place in the canonical CSV.

The original CSV is replaced only after a complete, validated temporary CSV
has been written and synced. The raw Modbus files remain unchanged.

Example:
    python3 recovery/scripts/impute_voltage.py --voltage voltage.csv \\
        --raw-file raw_modbus/SUB_2019-06-01.csv
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from decode_modbus_voltage import BASE_FIELDS, CHANNELS, output_specs, voltage_text


ROOT = Path(__file__).resolve().parents[2]
YEAR_SHIFT = 364 * 86400
HOUR = 3600
TAPER = 600
EXPECTED_ROWS = 65_404_800
EXPECTED_EMPTY_SECONDS = 133_325
EXPECTED_GAPS = 54
EXPECTED_PARTIAL = {1559381553: ("chrg", "dwsh", "gen6"),
                    1559398793: ("main", "gen1")}


@dataclass(frozen=True)
class LongGap:
    start: int
    end: int
    donor_shift: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1


LONG_GAPS = (
    LongGap(1528482113, 1528598134, YEAR_SHIFT),
    LongGap(1559381554, 1559398792, -YEAR_SHIFT),
)


def parse_tenths(value: str) -> int | None:
    if not value:
        return None
    whole, dot, fraction = value.partition(".")
    if not dot or not (len(fraction) == 1 or
                       (len(fraction) == 3 and fraction[1:] == "00")):
        raise ValueError(f"voltage is not a native 0.1 V reading: {value!r}")
    return int(whole) * 10 + int(fraction[0])


def parse_values(line: str) -> tuple[int | None, ...]:
    fields = line.rstrip("\r\n").split(",")
    if len(fields) != len(BASE_FIELDS) + len(CHANNELS):
        raise ValueError(f"voltage row has {len(fields)} fields, expected 23")
    return tuple(parse_tenths(value) for value in fields[4:])


def raw_bank_voltage(line: bytes) -> tuple[int, int]:
    fields = line.rstrip(b"\r\n").split(b",")
    if len(fields) != 45:
        raise ValueError(f"raw bank row has {len(fields)} fields, expected 45")
    return int(fields[39]), int(fields[40])


def boundary_overrides(raw_file: Path, appliances: Path) -> dict[int, tuple[dict[str, str], bool]]:
    """Get both partial-second repairs from the actual malformed raw source."""
    specs = dict(output_specs(appliances))
    first_a: tuple[int, int] | None = None
    rescued_a: tuple[int, int] | None = None
    with raw_file.open("rb", buffering=1024 * 1024) as stream:
        for line in stream:
            if line.startswith(b"1559381553,A,"):
                first_a = raw_bank_voltage(line)
            if b"1559398793,A," in line and not line.startswith(b"1559398793,A,"):
                rescued_a = raw_bank_voltage(line[line.index(b"1559398793,A,"):])
    if first_a is None or rescued_a is None:
        raise ValueError("could not independently verify both raw boundary records")

    # At 02:32:33, the G row is truncated. Use the matching same-second
    # bank-A leg, following the previously agreed mains-bank fallback rule.
    proxy: dict[str, str] = {}
    for channel in EXPECTED_PARTIAL[1559381553]:
        sources = specs[channel]
        if len(sources) != 1 or sources[0][0] != 6:
            raise ValueError(f"unexpected G-bank mapping for {channel}: {sources}")
        proxy[channel] = voltage_text(first_a[sources[0][1] - 1])

    # At 07:19:53, the full A row survives inside a malformed joined line.
    observed: dict[str, str] = {}
    for channel in EXPECTED_PARTIAL[1559398793]:
        sources = specs[channel]
        if any(bank != 0 for bank, _ in sources):
            raise ValueError(f"unexpected A-bank mapping for {channel}: {sources}")
        observed[channel] = voltage_text(sum(rescued_a[leg - 1] for _, leg in sources))
    return {1559381553: (proxy, True), 1559398793: (observed, False)}


def patch_values(values: tuple[int | None, ...], timestamp: int,
                 overrides: dict[int, tuple[dict[str, str], bool]]) -> tuple[int | None, ...]:
    result = list(values)
    if timestamp in overrides:
        replacements, _ = overrides[timestamp]
        for channel, text in replacements.items():
            position = CHANNELS.index(channel)
            if result[position] is not None:
                raise ValueError(f"refusing to overwrite measured {channel} at {timestamp}")
            result[position] = parse_tenths(text)
    return tuple(result)


def wanted_intervals() -> list[tuple[int, int]]:
    intervals: list[tuple[int, int]] = []
    for gap in LONG_GAPS:
        for shift in (0, gap.donor_shift):
            intervals.append((gap.start + shift - HOUR, gap.end + shift + HOUR))
    intervals.sort()
    merged: list[tuple[int, int]] = []
    for start, end in intervals:
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def inspect_source(path: Path) -> tuple[
    dict[int, tuple[int | None, ...]],
    list[tuple[int, int, str, str]],
    dict[int, tuple[int | None, ...]],
    dict[str, int],
]:
    """One streaming pass: collect only needed donor/boundary data and gaps."""
    lookup: dict[int, tuple[int | None, ...]] = {}
    gaps: list[tuple[int, int, str, str]] = []
    partial: dict[int, tuple[int | None, ...]] = {}
    intervals = wanted_intervals()
    interval_index = 0
    prior_line = ""
    open_gap: tuple[int, str] | None = None
    first_ts: int | None = None
    empty_seconds = 0
    rows = 0
    with path.open("r", encoding="ascii", newline="", buffering=1024 * 1024) as stream:
        header = stream.readline().rstrip("\r\n").split(",")
        if header != list(BASE_FIELDS + CHANNELS):
            raise ValueError(f"unexpected voltage header: {header}")
        for line in stream:
            head = line.split(",", 4)
            if len(head) != 5:
                raise ValueError(f"malformed row at line {rows + 2:,}")
            timestamp = int(head[0])
            if first_ts is None:
                first_ts = timestamp
            if timestamp != first_ts + rows:
                raise ValueError(f"timestamp discontinuity at line {rows + 2:,}")
            rows += 1
            if rows % 10_000_000 == 0:
                print(f"inspected {rows:,} rows", file=sys.stderr, flush=True)
            if head[1] not in ("", "s"):
                raise ValueError(f"unexpected voltage marker at {timestamp}: {head[1]!r}")
            payload = head[4]
            empty = payload.rstrip("\r\n") == "," * (len(CHANNELS) - 1)
            if empty:
                empty_seconds += 1
                if open_gap is None:
                    if not prior_line:
                        raise ValueError("gap begins at first record")
                    open_gap = (timestamp, prior_line)
            else:
                if open_gap is not None:
                    gaps.append((open_gap[0], timestamp - 1, open_gap[1], line))
                    open_gap = None
                if payload.startswith(",") or ",," in payload or payload.endswith(",\n"):
                    partial[timestamp] = parse_values(line)

            while interval_index < len(intervals) and timestamp > intervals[interval_index][1]:
                interval_index += 1
            if (interval_index < len(intervals)
                    and intervals[interval_index][0] <= timestamp <= intervals[interval_index][1]):
                lookup[timestamp] = parse_values(line)
            prior_line = line
    if open_gap is not None:
        raise ValueError("gap ends at last record")
    if rows != EXPECTED_ROWS or empty_seconds != EXPECTED_EMPTY_SECONDS or len(gaps) != EXPECTED_GAPS:
        raise ValueError(f"source profile changed: {rows=} {empty_seconds=} gaps={len(gaps)}")
    if {ts: tuple(CHANNELS[i] for i, x in enumerate(values) if x is None)
            for ts, values in partial.items()} != EXPECTED_PARTIAL:
        raise ValueError(f"partial-row profile changed: {partial.keys()}")
    long_seen = {(start, end) for start, end, _, _ in gaps if end - start + 1 > 9}
    if long_seen != {(gap.start, gap.end) for gap in LONG_GAPS}:
        raise ValueError(f"long-gap profile changed: {long_seen}")
    return lookup, gaps, partial, {"rows": rows, "empty_seconds": empty_seconds,
                                    "gaps": len(gaps), "partial_rows": len(partial)}


def complete(values: tuple[int | None, ...], description: str) -> tuple[int, ...]:
    if any(value is None for value in values):
        raise ValueError(f"missing voltage in {description}")
    return tuple(value for value in values if value is not None)


def gap_parameters(gap: LongGap, lookup: dict[int, tuple[int | None, ...]],
                   overrides: dict[int, tuple[dict[str, str], bool]]) -> tuple[
                       tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    """Paired one-hour median offsets and exact endpoint residuals, in 0.1 V."""
    before_samples: list[list[int]] = [[] for _ in CHANNELS]
    after_samples: list[list[int]] = [[] for _ in CHANNELS]
    for target_start, target_end, bucket in (
        (gap.start - HOUR, gap.start - 1, before_samples),
        (gap.end + 1, gap.end + HOUR, after_samples),
    ):
        for timestamp in range(target_start, target_end + 1):
            target = patch_values(lookup[timestamp], timestamp, overrides)
            donor = lookup[timestamp + gap.donor_shift]
            for index, (actual, counterpart) in enumerate(zip(target, donor)):
                if actual is not None and counterpart is not None:
                    bucket[index].append(actual - counterpart)
    if any(len(bucket) < HOUR * 0.9 for bucket in before_samples + after_samples):
        raise ValueError(f"insufficient paired boundary readings for {gap.start}")
    median_before = tuple(statistics.median(bucket) for bucket in before_samples)
    median_after = tuple(statistics.median(bucket) for bucket in after_samples)

    first_target = complete(patch_values(lookup[gap.start - 1], gap.start - 1, overrides),
                            f"target before {gap.start}")
    last_target = complete(patch_values(lookup[gap.end + 1], gap.end + 1, overrides),
                           f"target after {gap.end}")
    first_donor = complete(lookup[gap.start - 1 + gap.donor_shift], "donor before gap")
    last_donor = complete(lookup[gap.end + 1 + gap.donor_shift], "donor after gap")
    exact_before = tuple(a - b for a, b in zip(first_target, first_donor))
    exact_after = tuple(a - b for a, b in zip(last_target, last_donor))
    return median_before, median_after, exact_before, exact_after


def long_estimate(donor: tuple[int, ...], position: int, length: int,
                  parameters: tuple[tuple[float, ...], ...]) -> tuple[int, ...]:
    median_before, median_after, exact_before, exact_after = parameters
    weight = position / (length + 1)
    entry_taper = max(0.0, 1.0 - position / (TAPER + 1))
    exit_taper = max(0.0, 1.0 - (length + 1 - position) / (TAPER + 1))
    result = []
    for index, measured_donor in enumerate(donor):
        offset = median_before[index] + (median_after[index] - median_before[index]) * weight
        offset += (exact_before[index] - median_before[index]) * entry_taper
        offset += (exact_after[index] - median_after[index]) * exit_taper
        result.append(round(measured_donor + offset))
    return tuple(result)


def short_estimate(before: tuple[int, ...], after: tuple[int, ...],
                   position: int, length: int) -> tuple[int, ...]:
    return tuple(round(left + (right - left) * position / (length + 1))
                 for left, right in zip(before, after))


def impute(path: Path, raw_file: Path, appliances: Path) -> dict[str, object]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    overrides = boundary_overrides(raw_file, appliances)
    lookup, gaps, partial, profile = inspect_source(path)
    free_bytes = shutil.disk_usage(path.parent).free
    if free_bytes < path.stat().st_size + 1024**3:
        raise OSError("not enough free space for safe atomic replacement")

    gap_by_start = {start: (end, before, after) for start, end, before, after in gaps}
    params = {gap.start: gap_parameters(gap, lookup, overrides) for gap in LONG_GAPS}
    short_bounds = {}
    for start, end, before, after in gaps:
        if start in params:
            continue
        left = complete(patch_values(parse_values(before), start - 1, overrides),
                        f"before short gap {start}")
        right = complete(patch_values(parse_values(after), end + 1, overrides),
                         f"after short gap {start}")
        short_bounds[start] = (left, right)

    temp_path: Path | None = None
    written = 0
    synthetic_rows = 0
    recovered_observations = 0
    try:
        fd, temp_name = tempfile.mkstemp(prefix=".voltage-imputed-", suffix=".tmp", dir=path.parent)
        temp_path = Path(temp_name)
        with path.open("r", encoding="ascii", newline="", buffering=1024 * 1024) as source, \
                os.fdopen(fd, "w", encoding="ascii", newline="", buffering=1024 * 1024) as output:
            output.write(source.readline())
            active: tuple[int, int, LongGap | None, tuple[int, ...] | None,
                          tuple[int, ...] | None] | None = None
            for line in source:
                timestamp = int(line.partition(",")[0])
                if timestamp in gap_by_start:
                    end, _, _ = gap_by_start[timestamp]
                    long_gap = next((gap for gap in LONG_GAPS if gap.start == timestamp), None)
                    bounds = short_bounds.get(timestamp)
                    active = (timestamp, end, long_gap,
                              bounds[0] if bounds else None, bounds[1] if bounds else None)

                if active is not None and active[0] <= timestamp <= active[1]:
                    start, end, long_gap, before, after = active
                    if long_gap is not None:
                        donor = complete(lookup[timestamp + long_gap.donor_shift],
                                         f"donor {timestamp}")
                        estimate = long_estimate(donor, timestamp - start + 1,
                                                 long_gap.length, params[start])
                    else:
                        if before is None or after is None:
                            raise AssertionError("short gap has no boundaries")
                        estimate = short_estimate(before, after, timestamp - start + 1,
                                                  end - start + 1)
                    base = line.split(",", 4)
                    if base[4].rstrip("\r\n") != "," * (len(CHANNELS) - 1):
                        raise ValueError(f"refusing to overwrite measured row {timestamp}")
                    output.write(",".join((base[0], "s", base[2], base[3],
                                           *(voltage_text(x) for x in estimate))) + "\n")
                    synthetic_rows += 1
                    if timestamp == end:
                        active = None
                elif timestamp in partial:
                    fields = line.rstrip("\r\n").split(",")
                    replacements, mark = overrides[timestamp]
                    for channel, value in replacements.items():
                        column = 4 + CHANNELS.index(channel)
                        if fields[column] != "":
                            raise ValueError(f"refusing to overwrite {channel} at {timestamp}")
                        fields[column] = value
                        recovered_observations += 1
                    if mark:
                        fields[1] = "s"
                        synthetic_rows += 1
                    output.write(",".join(fields) + "\n")
                else:
                    output.write(line)
                written += 1
                if written % 10_000_000 == 0:
                    print(f"wrote {written:,} rows", file=sys.stderr, flush=True)
            if written != EXPECTED_ROWS or synthetic_rows != EXPECTED_EMPTY_SECONDS + 1 \
                    or recovered_observations != 5:
                raise ValueError(f"output counts changed: {written=} {synthetic_rows=} "
                                 f"{recovered_observations=}")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return {**profile, "synthetic_rows": synthetic_rows,
            "observed_cells_salvaged": 2, "proxy_cells": 3,
            "short_gap_seconds": sum(end - start + 1 for start, end, _, _ in gaps
                                     if start not in params),
            "long_gap_seconds": sum(gap.length for gap in LONG_GAPS),
            "output": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voltage", type=Path, default=ROOT / "voltage.csv")
    parser.add_argument("--raw-file", type=Path,
                        default=ROOT / "raw_modbus/SUB_2019-06-01.csv")
    parser.add_argument("--appliances", type=Path, default=ROOT / "appliances.csv")
    args = parser.parse_args()
    print(json.dumps(impute(args.voltage, args.raw_file, args.appliances), indent=2))


if __name__ == "__main__":
    main()
