import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from static_input_scope import ScopeError
from static_report_paths import verify_report_paths


class StaticReportPathsTest(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.base = Path(work.name).resolve()
        self.current = self.base / "current"
        self.previous = self.base / "previous"
        self.current.mkdir()
        self.previous.mkdir()
        self.old_report = self.previous / "checkstyle.xml"
        self.old_report.write_bytes(b"prior independent fixture output\n")
        self.old_hash = sha256(self.old_report.read_bytes()).hexdigest()
        (self.current / "sources.txt").write_text("CurrentFixture.java\n", encoding="utf-8")
        self.stages = {
            "checkstyle": ["checkstyle", "-o", str(self.current / "checkstyle.xml")],
            "pmd": [
                "pmd",
                "--file-list",
                str(self.current / "sources.txt"),
                "--report-file",
                str(self.current / "pmd.xml"),
            ],
            "spotbugs": ["spotbugs", "-output", str(self.current / "spotbugs.xml")],
        }

    def tearDown(self):
        self.assertEqual(self.old_hash, sha256(self.old_report.read_bytes()).hexdigest())

    def test_001_three_fresh_absolute_paths(self):
        expected = {name: str(self.current / f"{name}.xml") for name in self.stages}
        self.assertEqual(expected, verify_report_paths(self.current, self.stages))
        self.assertFalse(any(Path(file).exists() for file in expected.values()))

    def test_002_previous_run_or_relative_output(self):
        for wrong in (str(self.old_report), "checkstyle.xml"):
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ScopeError, "REPORT_OUTSIDE"):
                self.stages["checkstyle"][-1] = wrong
                verify_report_paths(self.current, self.stages)

    def test_003_existing_report_and_dangling_symlink(self):
        target = self.current / "checkstyle.xml"
        target.write_text("owned receipt", encoding="utf-8")
        with self.assertRaisesRegex(ScopeError, "REPORT_PATH_ALREADY_USED"):
            verify_report_paths(self.current, self.stages)
        target.unlink()
        target.symlink_to(self.previous / "nonexistent.xml")
        with self.assertRaisesRegex(ScopeError, "REPORT_PATH_ALREADY_USED"):
            verify_report_paths(self.current, self.stages)

    def test_004_duplicate_output_options(self):
        self.stages["checkstyle"].append(f"--output={self.old_report}")
        with self.assertRaisesRegex(ScopeError, "AMBIGUOUS_PATH_OPTION"):
            verify_report_paths(self.current, self.stages)

    def test_005_previous_file_list_or_symlink(self):
        self.stages["pmd"][2] = str(self.previous / "sources.txt")
        with self.assertRaisesRegex(ScopeError, "FILE_LIST_OUTSIDE"):
            verify_report_paths(self.current, self.stages)
        sources = self.current / "sources.txt"
        self.stages["pmd"][2] = str(sources)
        sources.unlink()
        sources.symlink_to(self.old_report)
        with self.assertRaisesRegex(ScopeError, "FILE_LIST_NOT_LOCAL_FILE"):
            verify_report_paths(self.current, self.stages)

    def test_006_symlink_run_directory(self):
        alias = self.base / "alias"
        alias.symlink_to(self.current, target_is_directory=True)
        with self.assertRaisesRegex(ScopeError, "RUN_DIRECTORY_NOT_CANONICAL"):
            verify_report_paths(alias, self.stages)


if __name__ == "__main__":
    unittest.main()
