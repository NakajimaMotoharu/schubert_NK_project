"""Fixed synthetic receipts for PT-OPS-G09-JUNIT001..010 and PT-OPS-G08-RAW001..004."""

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
        self.quality = []
        for module in MODULES:
            path = self.repo / module / "target/surefire-reports/TEST-fixture.Unit.xml"
            path.parent.mkdir(parents=True)
            path.write_bytes(REPORT)
            self.paths.append(path)
            target = path.parent.parent
            relatives = ["jacoco.exec", "site/jacoco/jacoco.xml", "site/jacoco/jacoco.csv",
                         "classes/fixture/Unit.class"]
            if module != "program/characterization":
                relatives.append("spotbugsXml.xml")
            for relative in relatives:
                raw = target / relative
                raw.parent.mkdir(parents=True, exist_ok=True)
                raw.write_bytes(("synthetic " + module + "/" + relative).encode())
                self.quality.append(raw)

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

    def test_quality_hashes_include_every_declared_report_and_real_class_path(self):
        self.success()
        decoded = json.loads(self.verify())
        self.assertEqual("pgpt-reactor-junit-v2", decoded["schema"])
        expected = {
            path.relative_to(self.repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.quality
        }
        self.assertEqual(34, len(expected))
        self.assertEqual(expected, decoded["qualityArtifacts"])
        self.assertNotIn("program/characterization/target/spotbugsXml.xml", expected)

    def test_later_jacoco_static_or_class_replacement_cannot_share_the_original_receipt(self):
        self.success()
        names = {"jacoco.exec", "jacoco.xml", "jacoco.csv", "spotbugsXml.xml", "Unit.class"}
        checked = set()
        for original in self.quality:
            if original.name not in names - checked:
                continue
            with self.subTest(name=original.name):
                retained = original.read_bytes()
                original.write_bytes(b"replacement with the same path")
                with self.assertRaisesRegex(ValueError, "differs"):
                    self.verify()
                original.write_bytes(retained)
                checked.add(original.name)
        self.assertEqual(names, checked)

    def test_missing_empty_aliased_quality_and_missing_main_fail_before_success(self):
        compiled = next(p for p in self.quality if p.name == "Unit.class")
        raw_coverage = next(p for p in self.quality if p.name == "jacoco.exec")
        content = compiled.read_bytes()
        compiled.unlink()
        with self.assertRaisesRegex(ValueError, "missing compiled Main"):
            self.capture()
        compiled.write_bytes(content)
        raw_coverage.write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "missing, empty or redirected"):
            self.capture()
        raw_coverage.unlink()
        raw_coverage.symlink_to(self.paths[0])
        with self.assertRaisesRegex(ValueError, "missing, empty or redirected"):
            self.capture()

    def test_original_junit_only_receipt_cannot_be_used_for_a_new_candidate(self):
        self.success()
        receipt = self.marker(".junit.json")
        old = json.loads(receipt.read_bytes())
        old["schema"] = "pgpt-reactor-junit-v1"
        del old["qualityArtifacts"]
        receipt.write_text(json.dumps(old, sort_keys=True, indent=2) + "\n")
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
