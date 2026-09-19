#!/usr/bin/env python3
"""Small deterministic tests for the voltage imputation calculations."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from impute_voltage import (ROOT, boundary_overrides, long_estimate,
                            parse_tenths, raw_bank_voltage, short_estimate,
                            wanted_intervals)


def raw_line(timestamp: int, bank: str, l1: int, l2: int) -> bytes:
    fields = [str(timestamp), bank] + ["0"] * 43
    fields[39] = str(l1)
    fields[40] = str(l2)
    return (",".join(fields) + "\n").encode("ascii")


class ImputeVoltageTests(unittest.TestCase):
    def test_native_precision(self) -> None:
        self.assertEqual(parse_tenths("123.1"), 1231)
        self.assertEqual(parse_tenths("123.100"), 1231)  # Legacy input.
        self.assertIsNone(parse_tenths(""))
        with self.assertRaises(ValueError):
            parse_tenths("123.123")

    def test_raw_rescue_and_proxy_marking(self) -> None:
        early = raw_line(1559381553, "A", 1231, 1231)
        rescued = raw_line(1559398793, "A", 1204, 1206)
        self.assertEqual(raw_bank_voltage(early), (1231, 1231))
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "SUB_2019-06-01.csv"
            source.write_bytes(early + b"truncated-G-row" + rescued)
            overrides = boundary_overrides(source, ROOT / "appliances.csv")
        self.assertEqual(overrides[1559381553],
                         ({"chrg": "123.1", "dwsh": "123.1", "gen6": "123.1"}, True))
        self.assertEqual(overrides[1559398793],
                         ({"main": "241.0", "gen1": "120.6"}, False))

    def test_short_interpolation_uses_both_boundaries(self) -> None:
        self.assertEqual(short_estimate((1200, 2400), (1204, 2408), 1, 3), (1201, 2402))
        self.assertEqual(short_estimate((1200, 2400), (1204, 2408), 3, 3), (1203, 2406))

    def test_long_taper_joins_exact_boundary_offset(self) -> None:
        # Median boundary calibration alone would shift the first row by 5 V;
        # the endpoint taper returns it to the neighboring measured level.
        parameters = ((50.0,), (30.0,), (0.0,), (0.0,))
        first = long_estimate((1200,), 1, 10000, parameters)[0]
        middle = long_estimate((1200,), 5000, 10000, parameters)[0]
        last = long_estimate((1200,), 10000, 10000, parameters)[0]
        self.assertLessEqual(abs(first - 1200), 1)
        self.assertEqual(middle, 1240)
        self.assertLessEqual(abs(last - 1200), 1)

    def test_donor_windows_cover_shifted_gaps(self) -> None:
        intervals = wanted_intervals()
        self.assertTrue(any(start <= 1528482113 + 31449600 <= end
                            for start, end in intervals))
        self.assertTrue(any(start <= 1559381554 - 31449600 <= end
                            for start, end in intervals))


if __name__ == "__main__":
    unittest.main()
