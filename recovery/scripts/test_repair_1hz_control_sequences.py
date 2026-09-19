#!/usr/bin/env python3
"""Tests for the audited 1 Hz control-sequence repair."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("repair_1hz_control_sequences.py")
SPEC = importlib.util.spec_from_file_location("repair_1hz_control_sequences", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(timestamp: int, marker: bytes, time_value: bytes, gen2: bytes) -> bytes:
    fields = [
        str(timestamp).encode("ascii"), marker, b"2018-06-09", time_value,
        b"1.5", b"0.0", b"0.5", b"0.2", b"0.0", b"0.0", b"0.2",
        b"0.0", b"0.0", b"0.1", gen2, b"0.4", b"0.1", b"0.1",
        b"0.1", b"0.0", b"0.0", b"0.0", b"0.0",
    ]
    return b",".join(fields) + b"\n"


class RepairTests(unittest.TestCase):
    def make_input(self, directory: Path, marker: bytes) -> Path:
        path = directory / "input.csv"
        path.write_bytes(
            MODULE.EXPECTED_HEADER
            + b"\n"
            + row(MODULE.GEN2_TS, marker, b"03:23:45", MODULE.BAD_GEN2)
            + row(MODULE.TIME_TS, marker, MODULE.BAD_TIME, b"0.0")
        )
        return path

    def test_source_current_restores_missing_cell_and_time(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            source = self.make_input(directory, b"")
            output = directory / "output.csv"
            result = MODULE.repair(source, output, "source-current")
            lines = output.read_bytes().splitlines()
            self.assertEqual(result, {"rows": 2, "gen2_repairs": 1, "time_repairs": 1})
            self.assertEqual(lines[1].split(b",")[14], b"")
            self.assertEqual(lines[2].split(b",")[3], MODULE.GOOD_TIME)

    def test_recovered_current_uses_verified_donor_value(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            source = self.make_input(directory, b"s")
            output = directory / "output.csv"
            MODULE.repair(source, output, "recovered-current")
            lines = output.read_bytes().splitlines()
            self.assertEqual(lines[1].split(b",")[14], b"0.0")
            self.assertEqual(lines[2].split(b",")[3], MODULE.GOOD_TIME)

    def test_voltage_repairs_only_copied_time_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            source = directory / "input.csv"
            source.write_bytes(
                MODULE.EXPECTED_HEADER
                + b"\n"
                + row(MODULE.GEN2_TS, b"s", b"03:23:45", b"118.7")
                + row(MODULE.TIME_TS, b"s", MODULE.BAD_TIME, b"118.7")
            )
            output = directory / "output.csv"
            result = MODULE.repair(source, output, "voltage")
            lines = output.read_bytes().splitlines()
            self.assertEqual(result, {"rows": 2, "gen2_repairs": 0, "time_repairs": 1})
            self.assertEqual(lines[1].split(b",")[14], b"118.7")
            self.assertEqual(lines[2].split(b",")[3], MODULE.GOOD_TIME)

    def test_unexpected_control_byte_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            source = self.make_input(directory, b"s")
            content = source.read_bytes().replace(b"0.4,0.1", b"0.4,\x00.1", 1)
            source.write_bytes(content)
            with self.assertRaisesRegex(ValueError, "unexpected ASCII control byte"):
                MODULE.repair(source, directory / "output.csv", "recovered-current")


if __name__ == "__main__":
    unittest.main()
