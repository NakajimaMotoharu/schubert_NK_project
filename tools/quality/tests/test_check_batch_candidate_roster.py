"""Independent, small JUnit fixtures for PT-OPS-G08-RST001..008."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_batch_candidate_roster import verify_roster


SCRIPT = Path(__file__).resolve().parents[1] / "check_batch_candidate_roster.py"
OWNERSHIP = b"""<testsuite name="fixture.BatchOwnership" tests="2" failures="0"
                           errors="0" skipped="0">
  <testcase classname="fixture.BatchOwnership" name="closesOnce()"/>
  <testcase classname="fixture.BatchOwnership$Parameterized" name="value [1]"/>
</testsuite>"""
TERMINAL = b"""<testsuite name="fixture.BatchTerminal" tests="1" failures="0"
                          errors="0" skipped="0">
  <testcase classname="fixture.BatchTerminal" name="finalWarning()"/>
</testsuite>"""


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BatchCandidateRosterTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        path = Path(scratch.name)
        self.profile = path / "profile.json"
        self.receipt = path / "receipt.json"
        self.reports = path / "reports"
        self.reports.mkdir()
        self.ownership = self.reports / "TEST-fixture.BatchOwnership.xml"
        self.terminal = self.reports / "TEST-fixture.BatchTerminal.xml"
        self.ownership.write_bytes(OWNERSHIP)
        self.terminal.write_bytes(TERMINAL)
        self.plan = {
            "schema": "pgpt-batch-roster-v1",
            "targetCommit": "a" * 40,
            "suites": {
                "fixture.BatchTerminal": [["fixture.BatchTerminal", "finalWarning()"]],
                "fixture.BatchOwnership": [
                    ["fixture.BatchOwnership$Parameterized", "value [1]"],
                    ["fixture.BatchOwnership", "closesOnce()"],
                ],
            },
        }
        self.execution = {
            "schema": "pgpt-batch-junit-receipt-v1",
            "targetCommit": "a" * 40,
            "runId": "PT-WEB-SYNTHETIC-01",
            "exitCode": 0,
            "reports": self.report_pins(),
        }
        self.save_inputs()

    def report_pins(self):
        return {path.name: checksum(path) for path in (self.ownership, self.terminal)}

    def save_inputs(self):
        for path, value in ((self.profile, self.plan), (self.receipt, self.execution)):
            path.write_text(json.dumps(value), encoding="utf-8")

    def verify(self, profile_pin=None, receipt_pin=None):
        return verify_roster(self.profile, profile_pin or checksum(self.profile),
                             self.receipt, receipt_pin or checksum(self.receipt), self.reports)

    def update_report(self, value):
        self.ownership.write_bytes(value)
        self.execution["reports"] = self.report_pins()
        self.save_inputs()

    def test_001_exact_members_independent_of_order(self):
        result = self.verify()
        self.assertEqual((2, 3), (result["suites"], result["testCases"]))
        self.assertEqual("PT-WEB-SYNTHETIC-01", result["runId"])
        self.assertEqual("a" * 40, result["targetCommit"])
        self.assertEqual("BATCH_ROSTER_MATCH", result["result"])
        self.assertFalse(result["formalAcceptance"])

    def test_002_source_run_and_numeric_success_must_match(self):
        for field, invalid in (("targetCommit", "b" * 40), ("exitCode", False),
                               ("exitCode", 143), ("runId", "PT-WEB-x/y")):
            with self.subTest(field=field, input=invalid):
                original = self.execution[field]
                self.execution[field] = invalid
                self.save_inputs()
                with self.assertRaisesRegex(ValueError, "successful run"):
                    self.verify()
                self.execution[field] = original

    def test_003_profile_receipt_and_raw_reports_are_pinned(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.verify(profile_pin="b" * 64)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.verify(receipt_pin="b" * 64)
        self.ownership.write_bytes(OWNERSHIP + b"\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.verify()

    def test_004_missing_and_unlisted_reports_fail(self):
        self.terminal.unlink()
        with self.assertRaisesRegex(ValueError, "report inventory"):
            self.verify()
        self.terminal.write_bytes(TERMINAL)
        (self.reports / "TEST-fixture.Unplanned.xml").write_bytes(TERMINAL)
        with self.assertRaisesRegex(ValueError, "report inventory"):
            self.verify()

    def test_005_same_count_with_renamed_wrong_owner_or_duplicate_case_fails(self):
        for expected, changed in (
            (b'value [1]', b'value [2]'),
            (b'fixture.BatchOwnership$Parameterized', b'fixture.BatchForeign'),
            (b'fixture.BatchOwnership$Parameterized" name="value [1]',
             b'fixture.BatchOwnership" name="closesOnce()'),
        ):
            with self.subTest(changed=changed):
                self.update_report(OWNERSHIP.replace(expected, changed))
                with self.assertRaisesRegex(ValueError, "case"):
                    self.verify()

    def test_006_zero_aggregate_does_not_hide_rerun_or_skipped_cases(self):
        for node in ("rerunFailure", "flakyError", "failure", "skipped"):
            with self.subTest(node=node):
                self.update_report(OWNERSHIP.replace(
                    b'name="closesOnce()"/>',
                    f'name="closesOnce()"><{node}/></testcase>'.encode(),
                ))
                with self.assertRaisesRegex(ValueError, "nonpassing"):
                    self.verify()

    def test_007_rejects_duplicate_expectations_and_symbolic_reports(self):
        row = self.plan["suites"]["fixture.BatchOwnership"]
        row.append(row[0])
        self.save_inputs()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.verify()
        row.pop()
        self.save_inputs()
        original = self.ownership.with_name("prior.xml")
        self.ownership.rename(original)
        self.ownership.symlink_to(original)
        with self.assertRaisesRegex(ValueError, "regular file"):
            self.verify()

    def test_008_cli_output_and_failure_exit(self):
        command = [sys.executable, "-B", str(SCRIPT), str(self.profile),
                   checksum(self.profile), str(self.receipt), checksum(self.receipt), str(self.reports)]
        good = subprocess.run(command, capture_output=True, timeout=15, check=False)
        self.assertEqual(0, good.returncode, good.stderr)
        self.assertEqual(3, json.loads(good.stdout)["testCases"])
        self.terminal.write_bytes(TERMINAL + b"\n")
        bad = subprocess.run(command, capture_output=True, timeout=15, check=False)
        self.assertEqual(1, bad.returncode)
        self.assertFalse(bad.stdout)
        self.assertIn(b"SHA-256 mismatch", bad.stderr)


if __name__ == "__main__":
    unittest.main()
