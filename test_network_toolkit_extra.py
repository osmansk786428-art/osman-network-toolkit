import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).with_name("Network-Toolkit-V21.py")

spec = importlib.util.spec_from_file_location("toolkit_v21_extra", SOURCE)
toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)


class ExtraToolkitTests(unittest.TestCase):

    def test_password_checker_rejects_empty_input(self):
        output = io.StringIO()

        with patch.object(toolkit, "ask", return_value=""):
            with contextlib.redirect_stdout(output):
                toolkit.password_strength_checker()

        self.assertIn("Password cannot be empty.", output.getvalue())

    def test_password_checker_weak_sample(self):
        output = io.StringIO()

        # Sample only; never enter a real password in tests.
        with patch.object(toolkit, "ask", return_value="123"):
            with contextlib.redirect_stdout(output):
                toolkit.password_strength_checker()

        self.assertIn("Estimated strength: Weak", output.getvalue())
        self.assertIn("not transmitted or logged", output.getvalue())

    def test_password_checker_strong_sample(self):
        output = io.StringIO()
        sample = "N3on!River#84X"

        with patch.object(toolkit, "ask", return_value=sample):
            with contextlib.redirect_stdout(output):
                toolkit.password_strength_checker()

        self.assertIn("Estimated strength: Strong", output.getvalue())

    def test_json_report_export_creates_valid_json(self):
        original_log = toolkit.report_log[:]

        sample_entries = [
            {
                "timestamp": "2026-10-27 12:00:00 IST",
                "title": "Automated Test",
                "details": {
                    "network": "192.168.1.0/24",
                    "passed": True
                }
            }
        ]

        output = io.StringIO()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                toolkit.report_log[:] = sample_entries

                old_cwd = os.path.abspath(os.getcwd())
                try:
                    os.chdir(temp_dir)
                    with patch("os.getcwd", return_value=temp_dir):
                        with contextlib.redirect_stdout(output):
                            toolkit.export_json_report()

                    files = list(
                        Path(temp_dir).glob("network_security_report_*.json")
                    )
                    self.assertEqual(len(files), 1)

                    with files[0].open(encoding="utf-8") as file:
                        data = json.load(file)

                    self.assertEqual(
                        data["application"], "OSMAN CYBER LAB"
                    )
                    self.assertEqual(len(data["entries"]), 1)
                    self.assertEqual(
                        data["entries"][0]["title"], "Automated Test"
                    )
                    self.assertTrue(
                        data["entries"][0]["details"]["passed"]
                    )
                finally:
                    os.chdir(old_cwd)
        finally:
            toolkit.report_log[:] = original_log

    def test_json_report_has_required_fields(self):
        original_log = toolkit.report_log[:]

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                toolkit.report_log[:] = []

                old_cwd = os.getcwd()
                os.chdir(temp_dir)
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        toolkit.export_json_report()

                    files = list(
                        Path(temp_dir).glob("network_security_report_*.json")
                    )
                    self.assertEqual(len(files), 1)

                    with files[0].open(encoding="utf-8") as file:
                        data = json.load(file)

                    for key in (
                        "application",
                        "version",
                        "generated_at",
                        "report_type",
                        "entries",
                    ):
                        with self.subTest(field=key):
                            self.assertIn(key, data)

                    self.assertIsInstance(data["entries"], list)
                finally:
                    os.chdir(old_cwd)
        finally:
            toolkit.report_log[:] = original_log


if __name__ == "__main__":
    unittest.main(verbosity=2)
