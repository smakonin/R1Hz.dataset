#!/usr/bin/env python3
"""Independently check the completed 1 Hz voltage CSV and its s markers."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from decode_modbus_voltage import BASE_FIELDS, CHANNELS


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_ROWS = 65_404_800
EXPECTED_SYNTHETIC = 133_326
FIRST_TS = 1505286000
SPECIAL = {1559381553: ("s", {"chrg": "123.1", "dwsh": "123.1", "gen6": "123.1"}),
           1559398793: ("", {"main": "241.0", "gen1": "120.6"})}
ONE_DECIMAL_ROW = re.compile(rb"(?:[0-9]+\.[0-9],){18}[0-9]+\.[0-9]")
DATE_FIELD = re.compile(rb"[0-9]{4}-[0-9]{2}-[0-9]{2}")
TIME_FIELD = re.compile(rb"[0-9]{2}:[0-9]{2}:[0-9]{2}")
LOCAL_TZ = ZoneInfo("America/Vancouver")
TIME_TEXT = tuple(
    f"{second // 3600:02d}:{(second % 3600) // 60:02d}:{second % 60:02d}".encode("ascii")
    for second in range(86_400)
)


def validate(path: Path) -> dict[str, object]:
    rows = 0
    synthetic = 0
    minimum = [float("inf")] * len(CHANNELS)
    maximum = [float("-inf")] * len(CHANNELS)
    specials_seen: set[int] = set()
    expected_date = b""
    expected_second_of_day = 0
    with path.open("rb", buffering=1024 * 1024) as stream:
        header = stream.readline().rstrip(b"\r\n").decode("ascii").split(",")
        if header != list(BASE_FIELDS + CHANNELS):
            raise ValueError("unexpected voltage header")
        for line in stream:
            fields = line.rstrip(b"\r\n").split(b",")
            if len(fields) != 23:
                raise ValueError(f"wrong field count at data row {rows + 1:,}")
            timestamp = int(fields[0])
            if timestamp != FIRST_TS + rows:
                raise ValueError(f"nonconsecutive timestamp at data row {rows + 1:,}")
            marker = fields[1].decode("ascii")
            if marker not in ("", "s"):
                raise ValueError(f"unexpected marker at {timestamp}")
            if DATE_FIELD.fullmatch(fields[2]) is None or TIME_FIELD.fullmatch(fields[3]) is None:
                raise ValueError(f"invalid local date/time syntax at {timestamp}")
            if timestamp % 3600 == 0:
                expected_local = datetime.fromtimestamp(timestamp, LOCAL_TZ)
                expected_date = expected_local.strftime("%Y-%m-%d").encode("ascii")
                expected_second_of_day = (
                    expected_local.hour * 3600 + expected_local.minute * 60 + expected_local.second
                )
            if fields[2] != expected_date or fields[3] != TIME_TEXT[expected_second_of_day]:
                raise ValueError(f"local date/time does not match unix_ts at {timestamp}")
            expected_second_of_day += 1
            if not all(fields[4:]):
                raise ValueError(f"blank voltage at {timestamp}")
            if ONE_DECIMAL_ROW.fullmatch(b",".join(fields[4:])) is None:
                raise ValueError(f"voltage does not have one decimal place at {timestamp}")
            if timestamp in SPECIAL:
                expected_marker, expected_cells = SPECIAL[timestamp]
                if marker != expected_marker:
                    raise ValueError(f"wrong marker at {timestamp}")
                for channel, expected in expected_cells.items():
                    if fields[4 + CHANNELS.index(channel)] != expected.encode("ascii"):
                        raise ValueError(f"wrong {channel} at {timestamp}")
                specials_seen.add(timestamp)
            if marker == "s":
                synthetic += 1
                for index, raw in enumerate(fields[4:]):
                    value = float(raw)
                    minimum[index] = min(minimum[index], value)
                    maximum[index] = max(maximum[index], value)
                    lower, upper = (200, 270) if CHANNELS[index] in ("main", "dryr") else (95, 140)
                    if not lower <= value <= upper:
                        raise ValueError(f"implausible {CHANNELS[index]}={value} at {timestamp}")
            rows += 1
            if rows % 10_000_000 == 0:
                print(f"validated {rows:,} rows", file=sys.stderr, flush=True)
    if rows != EXPECTED_ROWS or synthetic != EXPECTED_SYNTHETIC or specials_seen != set(SPECIAL):
        raise ValueError(f"validation totals changed: {rows=} {synthetic=} {specials_seen=}")
    return {"rows": rows, "synthetic_rows": synthetic, "blank_cells": 0,
            "special_rows_verified": len(specials_seen),
            "synthetic_min_v": dict(zip(CHANNELS, minimum)),
            "synthetic_max_v": dict(zip(CHANNELS, maximum))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("voltage", type=Path, nargs="?", default=ROOT / "voltage.csv")
    args = parser.parse_args()
    print(json.dumps(validate(args.voltage), indent=2))


if __name__ == "__main__":
    main()
