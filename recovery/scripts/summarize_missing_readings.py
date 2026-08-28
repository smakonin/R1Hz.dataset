#!/usr/bin/env python3
"""Consolidate row-level R1Hz missing-reading audit outputs into intervals."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


FILES = ("current", "power_factor", "power", "reactive")
LOCAL_TZ = ZoneInfo("America/Vancouver")


def local_iso(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def read_detail(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def group_detail(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    intervals: list[dict[str, object]] = []
    if not rows:
        return intervals

    start = rows[0]
    previous = rows[0]
    for row in rows[1:]:
        timestamp = int(row["unix_ts"])
        previous_timestamp = int(previous["unix_ts"])
        if timestamp != previous_timestamp + 1 or row["missing_columns"] != previous["missing_columns"]:
            intervals.append(make_interval(start, previous))
            start = row
        previous = row
    intervals.append(make_interval(start, previous))
    return intervals


def make_interval(start: dict[str, str], end: dict[str, str]) -> dict[str, object]:
    start_ts = int(start["unix_ts"])
    end_ts = int(end["unix_ts"])
    return {
        "file": start["file"],
        "start_row_number": start["row_number"],
        "end_row_number": end["row_number"],
        "start_unix_ts": start_ts,
        "end_unix_ts": end_ts,
        "start_local": f'{start["date"]} {start["time"]}',
        "end_local": f'{end["date"]} {end["time"]}',
        "seconds": end_ts - start_ts + 1,
        "missing_columns": start["missing_columns"],
    }


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    audit_dir = root / "analysis" / "missing_readings"

    detail_by_file: dict[str, list[dict[str, str]]] = {}
    intervals_by_file: dict[str, list[dict[str, object]]] = {}
    all_intervals: list[dict[str, object]] = []
    timestamps_by_file: dict[str, set[int]] = {}

    for stem in FILES:
        rows = read_detail(audit_dir / f"{stem}_null_measurement_rows.csv")
        detail_by_file[stem] = rows
        timestamps_by_file[stem] = {int(row["unix_ts"]) for row in rows}
        intervals = group_detail(rows)
        intervals_by_file[stem] = intervals
        all_intervals.extend(intervals)

    interval_fields = [
        "file",
        "start_row_number",
        "end_row_number",
        "start_unix_ts",
        "end_unix_ts",
        "start_local",
        "end_local",
        "seconds",
        "missing_columns",
    ]
    write_rows(audit_dir / "null_measurement_intervals.csv", interval_fields, all_intervals)

    union_timestamps = sorted(set().union(*timestamps_by_file.values()))
    cross_intervals: list[dict[str, object]] = []
    if union_timestamps:
        start_ts = previous_ts = union_timestamps[0]
        file_set = tuple(stem for stem in FILES if start_ts in timestamps_by_file[stem])
        for timestamp in union_timestamps[1:]:
            next_file_set = tuple(stem for stem in FILES if timestamp in timestamps_by_file[stem])
            if timestamp != previous_ts + 1 or next_file_set != file_set:
                cross_intervals.append(
                    {
                        "missing_files": ";".join(f"{stem}.csv" for stem in file_set),
                        "start_unix_ts": start_ts,
                        "end_unix_ts": previous_ts,
                        "start_local": local_iso(start_ts),
                        "end_local": local_iso(previous_ts),
                        "seconds": previous_ts - start_ts + 1,
                    }
                )
                start_ts = timestamp
                file_set = next_file_set
            previous_ts = timestamp
        cross_intervals.append(
            {
                "missing_files": ";".join(f"{stem}.csv" for stem in file_set),
                "start_unix_ts": start_ts,
                "end_unix_ts": previous_ts,
                "start_local": local_iso(start_ts),
                "end_local": local_iso(previous_ts),
                "seconds": previous_ts - start_ts + 1,
            }
        )

    cross_fields = [
        "missing_files",
        "start_unix_ts",
        "end_unix_ts",
        "start_local",
        "end_local",
        "seconds",
    ]
    write_rows(audit_dir / "cross_file_null_intervals.csv", cross_fields, cross_intervals)

    summary_rows: list[dict[str, object]] = []
    for stem in FILES:
        with (audit_dir / f"{stem}_summary.csv").open(newline="") as stream:
            summary = next(csv.DictReader(stream))
        rows = int(summary["rows"])
        null_rows = int(summary["rows_with_null_measurements"])
        summary_rows.append(
            {
                "file": summary["file"],
                "rows": rows,
                "first_unix_ts": summary["first_unix_ts"],
                "last_unix_ts": summary["last_unix_ts"],
                "missing_timestamps": summary["missing_timestamps"],
                "duplicate_or_backwards": summary["duplicate_or_backwards"],
                "malformed_rows": summary["malformed_rows"],
                "rows_with_null_circuit_measurements": null_rows,
                "null_circuit_row_rate": f"{null_rows / rows:.12f}",
                "null_circuit_cells": summary["null_measurement_cells"],
                "null_circuit_intervals": len(intervals_by_file[stem]),
                "ihd_present_rows": summary["ihd_present_rows"],
                "ihd_blank_rows": summary["ihd_blank_rows"],
            }
        )

    summary_fields = [
        "file",
        "rows",
        "first_unix_ts",
        "last_unix_ts",
        "missing_timestamps",
        "duplicate_or_backwards",
        "malformed_rows",
        "rows_with_null_circuit_measurements",
        "null_circuit_row_rate",
        "null_circuit_cells",
        "null_circuit_intervals",
        "ihd_present_rows",
        "ihd_blank_rows",
    ]
    write_rows(audit_dir / "audit_summary.csv", summary_fields, summary_rows)

    by_column_rows: list[dict[str, object]] = []
    for stem in FILES:
        with (audit_dir / f"{stem}_nulls_by_column.csv").open(newline="") as stream:
            by_column_rows.extend(csv.DictReader(stream))
    write_rows(
        audit_dir / "nulls_by_column.csv",
        ["file", "column", "null_cells", "total_rows", "null_rate"],
        by_column_rows,
    )

    presence_counts: defaultdict[str, int] = defaultdict(int)
    for timestamp in union_timestamps:
        key = ";".join(f"{stem}.csv" for stem in FILES if timestamp in timestamps_by_file[stem])
        presence_counts[key] += 1

    print(f"Wrote {len(all_intervals)} per-file null intervals.")
    print(f"Wrote {len(cross_intervals)} cross-file null intervals.")
    for files, count in sorted(presence_counts.items()):
        print(f"{files}: {count} seconds")


if __name__ == "__main__":
    main()
