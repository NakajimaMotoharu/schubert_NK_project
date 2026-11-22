"""Fixed synthetic reactor receipts for PT-OPS-G09-JUNIT001..010."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from pgpt_reactor_junit import capture_reactor_junit, verify_reactor_junit


RUN = "PT-WEB-SYNTHETIC-01"
SOURCE = "a" * 40
MODULES = (
    "program/characterization",
    "src/schubert-nk-api",
    "src/schubert-nk-batch",
    "src/schubert-nk-bootstrap",
    "src/schubert-nk-protocol",
    "src/schubert-nk-storage",
    "src/schubert-nk-web",
)
REPORT = b"""
<testsuite name="fixture.Unit" tests="1" failures="0" errors="0" skipped="0">
    <properties><property name="dummy" value="fixture-omitted-property"/></properties>
    <testcase classname="fixture.Unit" name="emptyList()"><system-out>fixture-omitted-stdout</system-out></testcase>
</testsuite>
"""


class ReactorJunitTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name)
        self.repo = root / "repo"
        self.runs = root / "runs"
        self.runs.mkdir()
        for suffix, value in (
            (".commit", SOURCE),
            (".started", "2026-11-23T00:00:00+09:00"),
            (".completed", "2026-11-23T00:01:00+09:00"),
            (".log", "synthetic terminal log"),
        ):
            self.marker(suffix).write_text(value + "\n")
        self.paths = []
        for module in MODULES:
            path = self.repo / module / "target/surefire-reports/TEST-fixture.Unit.xml"
            path.parent.mkdir(parents=True)
            path.write_bytes(REPORT)
            self.paths.append(path)

    def marker(self, suffix):
        return self.runs / (RUN + suffix)

    def capture(self):
        return capture_reactor_junit(self.repo, RUN, SOURCE, self.runs)

    def verify(self):
        return verify_reactor_junit(self.repo, RUN, SOURCE, self.runs)

    def success(self):
        self.capture()
        self.marker(".exit").write_text("0\n")

    def test_terminal_binds_all_original_paths_and_counts(self):
        self.success()
        content = self.verify()
        output = json.loads(content)
        self.assertEqual((RUN, SOURCE), (output["runId"], output["targetCommit"]))
        self.assertEqual(
            {
                path.relative_to(self.repo).as_posix(): {
                    "tests": 1,
                    "sha256": hashlib.sha256(REPORT).hexdigest(),
                }
                for path in self.paths
            },
            output["reports"],
        )
        self.assertEqual("2026-11-23T00:01:00+09:00", output["completedAt"])
        self.assertEqual(
            hashlib.sha256(b"synthetic terminal log\n").hexdigest(), output["buildLogSha256"]
        )
        self.assertNotIn(b"fixture-omitted", content)
        self.assertNotIn(b"synthetic terminal log", content)

    def test_same_source_passing_replacement_after_terminal_is_rejected(self):
        self.success()
        self.paths[0].write_bytes(REPORT.replace(b"emptyList()", b"singleValue()"))
        with self.assertRaisesRegex(ValueError, "differs"):
            self.verify()

    def test_missing_module_is_rejected(self):
        self.paths[0].unlink()
        with self.assertRaisesRegex(ValueError, "missing original"):
            self.capture()
        self.assertFalse(self.marker(".junit.json").exists())

    def test_unexpected_extra_passing_suite_after_terminal_is_rejected(self):
        self.success()
        extra = self.paths[0].with_name("TEST-fixture.Second.xml")
        extra.write_bytes(REPORT)
        with self.assertRaisesRegex(ValueError, "differs"):
            self.verify()

    def test_any_nonpass_child_is_rejected_even_when_suite_counters_are_zero(self):
        good = b"<system-out>fixture-omitted-stdout</system-out>"
        for tag in (b"failure", b"error", b"skipped", b"flakyFailure", b"flakyError", b"rerunFailure", b"rerunError"):
            with self.subTest(tag=tag):
                self.paths[1].write_bytes(REPORT.replace(good, b"<" + tag + b"/>"))
                with self.assertRaisesRegex(ValueError, "nonpassing"):
                    self.capture()
                self.assertFalse(self.marker(".junit.json").exists())

    def test_invalid_counters_or_absent_case_cannot_pass(self):
        for content in (
            REPORT.replace(b'tests="1"', b'tests="2"'),
            REPORT.replace(b'failures="0"', b'failures="1"'),
            REPORT.replace(b' skipped="0"', b""),
            b'<testsuite tests="0" failures="0" errors="0" skipped="0"/>',
        ):
            with self.subTest(content=content[:50]):
                self.paths[1].write_bytes(content)
                with self.assertRaisesRegex(ValueError, "nonpassing"):
                    self.capture()

    def test_even_well_named_report_from_an_alias_is_rejected(self):
        before = self.runs / "outside.xml"
        before.write_bytes(REPORT)
        self.paths[1].unlink()
        self.paths[1].symlink_to(before)
        with self.assertRaisesRegex(ValueError, "regular file"):
            self.capture()

    def test_terminal_is_single_write_and_missing_failed_exit_refused(self):
        self.capture()
        sealed = self.marker(".junit.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.capture()
        self.assertEqual(sealed, self.marker(".junit.json").read_bytes())
        with self.assertRaises(FileNotFoundError):
            self.verify()
        self.marker(".exit").write_text("143\n")
        with self.assertRaisesRegex(ValueError, "not successful"):
            self.verify()

    def test_commit_mismatch_and_different_build_log_are_rejected(self):
        self.success()
        with self.assertRaisesRegex(ValueError, "commit does not match"):
            verify_reactor_junit(self.repo, RUN, "b" * 40, self.runs)
        self.marker(".log").write_text("different synthetic log\n")
        with self.assertRaisesRegex(ValueError, "differs"):
            self.verify()

    def test_unparseable_or_missing_receipt_is_rejected(self):
        self.paths[2].write_text("<unclosed")
        with self.assertRaises(ET.ParseError):
            self.capture()
        self.marker(".exit").write_text("0\n")
        with self.assertRaises(FileNotFoundError):
            self.verify()


if __name__ == "__main__":
    unittest.main()
