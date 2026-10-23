"""Regressionstests: Bug nachweisen und Fehlerbehebung prüfen."""

import random
import tempfile
import unittest
from pathlib import Path

from mini_fuzz.engine import minimize, mutate, run_fuzzer
from mini_fuzz.protocol import InvalidMessage, Message, parse_buggy, parse_fixed


class ProtocolTests(unittest.TestCase):
    def test_valid_message(self):
        expected = Message(sender="alice", body="Hallo")
        self.assertEqual(parse_buggy(b"MSG|alice|Hallo"), expected)
        self.assertEqual(parse_fixed(b"MSG|alice|Hallo"), expected)

    def test_known_bug_causes_index_error(self):
        with self.assertRaises(IndexError):
            parse_buggy(b"MSG|alice")

    def test_fix_rejects_incomplete_message_safely(self):
        for payload in (b"MSG", b"MSG|alice", b"MSG||Hallo", b"MSG|alice|"):
            with self.subTest(payload=payload):
                with self.assertRaises(InvalidMessage):
                    parse_fixed(payload)

    def test_fixed_handles_invalid_utf8_and_oversize(self):
        for payload in (b"MSG|a|\xff", b"MSG|a|" + b"x" * 500):
            with self.subTest(payload=payload[:20]):
                with self.assertRaises(InvalidMessage):
                    parse_fixed(payload)

    def test_minimized_crash_is_short_and_reproducible(self):
        minimized = minimize(b"MSG|alice", parse_buggy, "IndexError")
        self.assertEqual(minimized, b"MSG")
        with self.assertRaises(IndexError):
            parse_buggy(minimized)

    def test_mutation_is_deterministic(self):
        self.assertEqual(mutate(b"MSG|a|x", random.Random(12)),
                         mutate(b"MSG|a|x", random.Random(12)))

    def test_fuzzer_finds_bug_and_fixed_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_buggy = run_fuzzer(
                parse_buggy, iterations=2000, seed=42, out_dir=Path(tmp) / "buggy"
            )
            self.assertGreaterEqual(len(report_buggy.crashes), 1)
            crash = report_buggy.crashes[0]
            self.assertEqual(crash.exception_name, "IndexError")
            self.assertEqual(crash.path.read_bytes(), crash.data)

            report_fixed = run_fuzzer(
                parse_fixed, iterations=2000, seed=42, out_dir=Path(tmp) / "fixed"
            )
            self.assertEqual(report_fixed.crashes, ())
            self.assertEqual(report_fixed.iterations, 2000)


if __name__ == "__main__":
    unittest.main()
