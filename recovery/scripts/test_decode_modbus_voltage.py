"""Deterministic checks for direct Modbus voltage decoding."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from decode_modbus_voltage import (
    BASE_FIELDS, CHANNELS, DATASET_ROOT, decode_voltage, output_specs, voltage_text,
)


def raw_row(timestamp: int, bank: str, l1: int, l2: int) -> str:
    registers = [0] * 43  # Modbus offsets 4021 through 4063.
    registers[4058 - 4021] = l1
    registers[4059 - 4021] = l2
    return f"{timestamp},{bank}," + ",".join(map(str, registers)) + "\n"


class DecodeModbusVoltageTests(unittest.TestCase):
    def test_panel_mapping_and_precision(self) -> None:
        specs = dict(output_specs(DATASET_ROOT / "appliances.csv"))
        self.assertEqual(len(specs), 19)
        self.assertEqual(specs["main"], ((0, 1), (0, 2)))
        self.assertEqual(specs["dryr"], ((1, 1), (1, 2)))
        self.assertEqual(specs["beda"], ((4, 1),))
        self.assertEqual(specs["gen1"], ((0, 2),))
        self.assertEqual(voltage_text(1209), "120.9")
        self.assertEqual(voltage_text(0), "0.0")

    def test_mains_fallback_and_raw_gap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_dir = root / "raw_modbus"
            raw_dir.mkdir()
            lines = []
            for timestamp in (100, 102):
                for bank in "ABCDEFGH":
                    l1, l2 = (1209, 1211) if timestamp == 100 else (0, 0)
                    if timestamp == 100 and bank == "B":
                        l1, l2 = 1198, 1205
                    if timestamp == 100 and bank == "E":
                        l1 = 0
                    lines.append(raw_row(timestamp, bank, l1, l2))
            (raw_dir / "SUB_2017-09-13.csv").write_text("".join(lines), encoding="ascii")

            timeline = root / "current.csv"
            with timeline.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(BASE_FIELDS + CHANNELS)
                for timestamp in (100, 101, 102):
                    writer.writerow([
                        str(timestamp), "s" if timestamp == 101 else "",
                        "2017-09-13", f"00:00:{timestamp - 100:02d}",
                    ] + ["0.0"] * len(CHANNELS))

            output = root / "voltage.csv"
            stats = decode_voltage(
                raw_dir, timeline, DATASET_ROOT / "appliances.csv", output,
                expected_rows=3, progress_rows=0,
            )
            with output.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(list(rows[0]), list(BASE_FIELDS + CHANNELS))
            self.assertEqual(rows[0]["marker"], "s")
            self.assertEqual(rows[0]["main"], "242.0")
            self.assertEqual(rows[0]["dryr"], "240.3")
            self.assertEqual(rows[0]["beda"], "120.9")
            self.assertEqual(rows[0]["bedp"], "119.8")
            self.assertEqual(rows[1]["marker"], "")
            self.assertTrue(all(rows[1][channel] == "" for channel in CHANNELS))
            self.assertEqual(rows[2]["main"], "0.0")
            self.assertEqual(rows[2]["marker"], "")
            self.assertEqual(stats["mains_fallback_values"], 2)
            self.assertEqual(stats["raw_missing_seconds"], 1)


if __name__ == "__main__":
    unittest.main()
