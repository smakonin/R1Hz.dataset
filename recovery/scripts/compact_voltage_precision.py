#!/usr/bin/env python3
"""Losslessly rewrite canonical voltage.csv from 3 to 1 decimal place.

Every voltage comes from, or was quantized to, a 0.1 V Modbus register step.
This script accepts only rows whose 19 voltage values end in two redundant
zeroes, verifies the one-second timeline and s markers, and atomically
replaces the CSV only after the complete output is written and synced.
It does not touch date, time, marker, or any numeric voltage value.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from decode_modbus_voltage import BASE_FIELDS, CHANNELS


ROOT = Path(__file__).resolve().parents[2]
FIRST_TS = 1505286000
EXPECTED_ROWS = 65_404_800
EXPECTED_S_MARKERS = 133_326
THREE_DECIMAL_ROW = re.compile(rb"(?:[0-9]+\.[0-9]00,){18}[0-9]+\.[0-9]00\n")


def compact(path: Path) -> dict[str, int | str]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    old_bytes = path.stat().st_size
    if shutil.disk_usage(path.parent).free < old_bytes + 1024**3:
        raise OSError("not enough free space for safe atomic replacement")

    temp_path: Path | None = None
    rows = 0
    synthetic = 0
    try:
        fd, temp_name = tempfile.mkstemp(prefix=".voltage-1dp-", suffix=".tmp", dir=path.parent)
        temp_path = Path(temp_name)
        with path.open("rb", buffering=1024 * 1024) as source, \
                os.fdopen(fd, "wb", buffering=1024 * 1024) as output:
            header = source.readline()
            if header.rstrip(b"\r\n").decode("ascii").split(",") != list(BASE_FIELDS + CHANNELS):
                raise ValueError("unexpected voltage header")
            output.write(header)
            for line in source:
                head = line.split(b",", 4)
                if len(head) != 5:
                    raise ValueError(f"malformed row {rows + 1:,}")
                if int(head[0]) != FIRST_TS + rows:
                    raise ValueError(f"nonconsecutive timestamp at row {rows + 1:,}")
                if head[1] not in (b"", b"s"):
                    raise ValueError(f"unexpected marker at row {rows + 1:,}")
                synthetic += head[1] == b"s"
                if THREE_DECIMAL_ROW.fullmatch(head[4]) is None:
                    raise ValueError(f"voltage missing or not an exact tenth at row {rows + 1:,}")
                # The regex proves each removal is exactly two trailing zeros
                # from a voltage field, never from a timestamp or other field.
                values = head[4].replace(b"00,", b",")[:-3] + b"\n"
                output.write(b",".join(head[:4]) + b"," + values)
                rows += 1
                if rows % 10_000_000 == 0:
                    print(f"converted {rows:,} rows", file=sys.stderr, flush=True)
            if rows != EXPECTED_ROWS or synthetic != EXPECTED_S_MARKERS:
                raise ValueError(f"unexpected row/marker count: {rows=} {synthetic=}")
            output.flush()
            os.fsync(output.fileno())
        new_bytes = temp_path.stat().st_size
        if new_bytes != old_bytes - 2 * len(CHANNELS) * rows:
            raise ValueError(f"unexpected output size: {old_bytes=} {new_bytes=}")
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return {"rows": rows, "s_markers": synthetic, "old_bytes": old_bytes,
            "new_bytes": new_bytes, "output": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("voltage", nargs="?", type=Path, default=ROOT / "voltage.csv")
    args = parser.parse_args()
    print(json.dumps(compact(args.voltage), indent=2))


if __name__ == "__main__":
    main()
