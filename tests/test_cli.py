"""Tests für den manuellen CLI-Testmodus."""
import contextlib
import io
import unittest
from unittest.mock import patch

from mini_fuzz.__main__ import main


class ManualCliTests(unittest.TestCase):
    def capture(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(args)
        return status, output.getvalue()

    def test_manual_bug_is_visible(self):
        status, output = self.capture(["test", "MSG|alice"])
        self.assertEqual(status, 0)
        self.assertIn("buggy: CRASH -> IndexError", output)
        self.assertIn("fixed: kontrolliert abgelehnt", output)

    def test_manual_valid_message(self):
        status, output = self.capture(["test", "MSG|alice|Hallo"])
        self.assertEqual(status, 0)
        self.assertIn("buggy: OK", output)
        self.assertIn("fixed: OK", output)

    def test_interactive_mode_until_exit(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["MSG|alice", "exit"]):
            with contextlib.redirect_stdout(output):
                status = main(["test"])
        self.assertEqual(status, 0)
        self.assertIn("CRASH -> IndexError", output.getvalue())
        self.assertIn("Testmodus beendet", output.getvalue())


if __name__ == "__main__":
    unittest.main()
