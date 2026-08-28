#!/usr/bin/env python3
"""Repair unquoted commas in the final weather field of climate.csv.

The historical source values are preserved exactly.  This script changes only
CSV serialization: a final weather field containing a comma is enclosed in
double quotes.  It deliberately preserves LF line endings and every byte on
unaffected rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


EXPECTED_HEADER = (
    "unix_ts,marker,local_dt,local_tm,temp,dew_point,rel_hum,precip_amt,"
    "wind_dir,wind_spd,visibility,stn_press,hmdx,wind_chill,weather"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_record(line: str) -> list[str]:
    return next(csv.reader([line], strict=True))


def repair(source: bytes) -> tuple[bytes, dict[str, object]]:
    if b"\r" in source:
        raise ValueError("expected LF-only climate.csv input")
    if not source.endswith(b"\n"):
        raise ValueError("expected a final LF")

    text = source.decode("utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != EXPECTED_HEADER:
        raise ValueError("unexpected climate.csv header")

    output = [lines[0]]
    repaired_lines: list[int] = []
    width_counts: dict[int, int] = {}

    for line_number, line in enumerate(lines[1:], start=2):
        parsed = parse_record(line)
        width_counts[len(parsed)] = width_counts.get(len(parsed), 0) + 1
        if len(parsed) == 15:
            semantic = parsed
            repaired = line
        elif len(parsed) > 15:
            semantic = line.split(",", 14)
            if len(semantic) != 15:
                raise ValueError(f"line {line_number}: fewer than 15 semantic fields")
            weather = semantic[14]
            repaired = ",".join(semantic[:14]) + "," + '"' + weather.replace('"', '""') + '"'
            repaired_lines.append(line_number)
        else:
            raise ValueError(f"line {line_number}: unexpected parsed width {len(parsed)}")

        if parse_record(repaired) != semantic:
            raise ValueError(f"line {line_number}: semantic value changed during repair")
        output.append(repaired)

    repaired_bytes = ("\n".join(output) + "\n").encode("utf-8")
    strict_rows = list(csv.reader(io.StringIO(repaired_bytes.decode("utf-8")), strict=True))
    if any(len(row) != 15 for row in strict_rows):
        raise ValueError("repaired output is not rectangular with 15 columns")

    report: dict[str, object] = {
        "operation": "CSV serialization repair; no values were imputed",
        "input_sha256": sha256(source),
        "output_sha256": sha256(repaired_bytes),
        "data_rows": len(lines) - 1,
        "columns": 15,
        "input_parsed_width_counts": {str(k): v for k, v in sorted(width_counts.items())},
        "repaired_rows": len(repaired_lines),
        "first_repaired_line": repaired_lines[0] if repaired_lines else None,
        "last_repaired_line": repaired_lines[-1] if repaired_lines else None,
        "input_bytes": len(source),
        "output_bytes": len(repaired_bytes),
    }
    return repaired_bytes, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="unrepaired climate.csv")
    parser.add_argument("output", type=Path, help="repaired climate.csv")
    parser.add_argument("--report", type=Path, help="optional JSON validation report")
    args = parser.parse_args()

    repaired, report = repair(args.input.read_bytes())
    args.output.write_bytes(repaired)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
