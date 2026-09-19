#!/usr/bin/env python3
"""Repair two audited ANSI escape-sequence corruptions in R1Hz CSV files.

The original ``current.csv`` contains two terminal escape sequences introduced
before the missing-data recovery was run:

* ``unix_ts=1528539825`` has ``ESC[O`` in ``gen2``. In an unrecovered source
  file this is restored to a blank missing value; in a recovered file it is
  replaced by the verified 364-day donor value ``0.0``.
* ``unix_ts=1528571381`` has ``ESC[I`` embedded in the local time. Removing
  the three control bytes restores ``12:09:41``.

The bad time metadata was copied into ``voltage.csv``, so the voltage mode
repairs that field as well. The program streams to a temporary file, checks
that the expected anomalies occur exactly once, and rejects every other ASCII
control byte before atomically replacing an input requested with ``--replace``.
"""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path


GEN2_TS = 1_528_539_825
TIME_TS = 1_528_571_381
BAD_GEN2 = b"\x1b[O"
BAD_TIME = b"12:09:4\x1b[I1"
GOOD_TIME = b"12:09:41"
EXPECTED_HEADER = (
    b"unix_ts,marker,date,time,main,beda,bedp,boil,chrg,cwsh,dryr,dwsh,frdg,"
    b"gen1,gen2,gen3,gen4,gen5,gen6,kit1,kit2,outp,vacu"
)
CONTROL_PATTERN = re.compile(rb"[\x00-\x1f\x7f]")


def repair(input_path: Path, output_path: Path, kind: str) -> dict[str, int]:
    """Write one strictly checked corrected copy and return repair counts."""
    if input_path.resolve() == output_path.resolve():
        raise ValueError("input and output paths must differ")

    expected_gen2_repairs = 0 if kind == "voltage" else 1
    gen2_replacement = b"" if kind == "source-current" else b"0.0"
    rows = 0
    gen2_repairs = 0
    time_repairs = 0

    with input_path.open("rb", buffering=1024 * 1024) as source, output_path.open(
        "xb", buffering=1024 * 1024
    ) as destination:
        header = source.readline().rstrip(b"\r\n")
        if header != EXPECTED_HEADER:
            raise ValueError(f"unexpected schema in {input_path}")
        destination.write(header + b"\n")

        for raw_line in source:
            rows += 1
            fields = raw_line.rstrip(b"\r\n").split(b",")
            if len(fields) != 23:
                raise ValueError(f"wrong field count at data row {rows:,}")
            try:
                timestamp = int(fields[0])
            except ValueError as exc:
                raise ValueError(f"invalid timestamp at data row {rows:,}") from exc

            if timestamp == GEN2_TS and kind != "voltage":
                if fields[14] != BAD_GEN2:
                    raise ValueError(
                        f"unexpected gen2 repair source at {timestamp}: {fields[14]!r}"
                    )
                fields[14] = gen2_replacement
                gen2_repairs += 1

            if timestamp == TIME_TS:
                if fields[3] != BAD_TIME:
                    raise ValueError(
                        f"unexpected time repair source at {timestamp}: {fields[3]!r}"
                    )
                fields[3] = GOOD_TIME
                time_repairs += 1

            corrected_line = b",".join(fields)
            if CONTROL_PATTERN.search(corrected_line) is not None:
                for index, field in enumerate(fields):
                    if CONTROL_PATTERN.search(field) is not None:
                        raise ValueError(
                            f"unexpected ASCII control byte at {timestamp}, field {index + 1}"
                        )
            destination.write(corrected_line + b"\n")

        destination.flush()
        os.fsync(destination.fileno())

    if gen2_repairs != expected_gen2_repairs or time_repairs != 1:
        output_path.unlink(missing_ok=True)
        raise ValueError(
            "repair totals changed: "
            f"gen2={gen2_repairs}/{expected_gen2_repairs}, time={time_repairs}/1"
        )

    return {"rows": rows, "gen2_repairs": gen2_repairs, "time_repairs": time_repairs}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("source-current", "recovered-current", "voltage"))
    parser.add_argument("input", type=Path)
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("--output", type=Path)
    output_group.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    if args.replace:
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{args.input.name}.", suffix=".repair", dir=args.input.parent
        )
        os.close(fd)
        temporary = Path(temporary_name)
        temporary.unlink()
        try:
            result = repair(args.input, temporary, args.kind)
            os.replace(temporary, args.input)
        finally:
            temporary.unlink(missing_ok=True)
    else:
        result = repair(args.input, args.output, args.kind)

    print(
        f"{args.kind}: rows={result['rows']:,}, "
        f"gen2_repairs={result['gen2_repairs']}, time_repairs={result['time_repairs']}"
    )


if __name__ == "__main__":
    main()
