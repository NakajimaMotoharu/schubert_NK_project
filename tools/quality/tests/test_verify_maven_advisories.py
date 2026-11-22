"""Fixed Maven input and scanner response fixtures for PT-OPS-OSV-001..009."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verify_maven_advisories import scan_bom


ROOT = "pkg:maven/local.example/nk@1?type=jar"
DEPENDENCY = "pkg:maven/org.example/model@2.0?type=jar"
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


class VerifyMavenAdvisoriesTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.directory = Path(scratch.name)
        self.repository = self.directory / "repository"
        self.artifact = self.repository / "org/example/model/2.0/model-2.0.jar"
        self.scanner = self.directory / "scanner"
        self.cache = self.directory / "cache"
        self.database = self.cache / "osv-scalibr/Maven/all.zip"
        self.bom = self.directory / "model.cdx.json"
        for path in (self.artifact, self.database, self.scanner):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"abc")
        self.document = {
            "bomFormat": "CycloneDX", "specVersion": "1.6",
            "metadata": {"component": {"bom-ref": ROOT}},
            "components": [{
                "group": "org.example", "name": "model", "version": "2.0",
                "purl": DEPENDENCY, "bom-ref": DEPENDENCY,
                "hashes": [{"alg": "SHA-256", "content": ABC_SHA256}],
            }],
            "dependencies": [
                {"ref": ROOT, "dependsOn": [DEPENDENCY]},
                {"ref": DEPENDENCY, "dependsOn": []},
            ],
        }
        self.bom.write_text(json.dumps(self.document), encoding="utf-8")
        self.package = {"package": {"ecosystem": "Maven", "purl": DEPENDENCY}}

    def scan(self):
        return scan_bom(
            self.bom, self.repository, self.scanner, ABC_SHA256, self.cache, ABC_SHA256
        )

    def response(self, code=0, packages=None, source_type="sbom"):
        def respond(command, **options):
            source = Path(command[-1])
            config = Path(command[command.index("--config") + 1])
            self.assertEqual(
                [str(self.scanner), "scan", "source", "--offline", "--all-packages",
                 "--config", str(config), "--format", "json", "-L", str(source)],
                command,
            )
            self.assertEqual(self.bom.read_bytes(), source.read_bytes())
            self.assertEqual("", config.read_text(encoding="utf-8"))
            self.assertEqual(options["cwd"], source.parent)
            self.assertEqual({"PATH", "OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY"}, options["env"].keys())
            self.assertEqual(str(self.cache), options["env"]["OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY"])
            self.assertEqual(120, options["timeout"])
            findings = [self.package] if packages is None else packages
            report = {"results": [{"source": {"path": str(source), "type": source_type},
                                   "packages": findings}]}
            return subprocess.CompletedProcess(command, code, json.dumps(report).encode())

        return respond

    @patch("verify_maven_advisories.subprocess.run")
    def test_001_clean_verified_input_scans_all_packages(self, run):
        run.side_effect = self.response()
        result = self.scan()
        self.assertEqual(1, result["scannedMavenPackages"])
        self.assertEqual([], result["findings"])
        self.assertEqual(ABC_SHA256, result["scannerSha256"])
        self.assertEqual(ABC_SHA256, result["databaseSha256"])
        run.assert_called_once()

    @patch("verify_maven_advisories.subprocess.run")
    def test_002_finding_is_preserved_as_public_coordinate_and_id(self, run):
        packages = [self.package | {
            "vulnerabilities": [{"id": "OSV-TEST-0002", "summary": "omitted details"}]
        }]
        run.side_effect = self.response(code=1, packages=packages)
        self.assertEqual(
            [{"purl": DEPENDENCY, "advisory": "OSV-TEST-0002"}],
            self.scan()["findings"],
        )

    @patch("verify_maven_advisories.subprocess.run")
    def test_003_rejects_changed_executable_before_scanning(self, run):
        self.scanner.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch for scanner"):
            self.scan()
        run.assert_not_called()

    @patch("verify_maven_advisories.subprocess.run")
    def test_004_rejects_absent_or_changed_database_before_scanning(self, run):
        self.database.unlink()
        with self.assertRaisesRegex(ValueError, "regular file"):
            self.scan()
        self.database.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch for all.zip"):
            self.scan()
        run.assert_not_called()

    @patch("verify_maven_advisories.subprocess.run")
    def test_005_rejects_partial_duplicate_foreign_or_wrong_source_reports(self, run):
        for packages, source in (
            ([], "sbom"),
            ([self.package, self.package], "sbom"),
            ([{"package": {"ecosystem": "npm", "purl": DEPENDENCY}}], "sbom"),
            ([self.package], "lockfile"),
        ):
            with self.subTest(packages=packages, source=source):
                run.side_effect = self.response(packages=packages, source_type=source)
                with self.assertRaises(ValueError):
                    self.scan()

    @patch("verify_maven_advisories.subprocess.run")
    def test_006_distinguishes_empty_scan_and_tool_failure(self, run):
        for exit_code in (127, 128):
            with self.subTest(exit_code=exit_code):
                run.side_effect = self.response(code=exit_code)
                with self.assertRaisesRegex(ValueError, f"did not complete, exit {exit_code}"):
                    self.scan()

    @patch("verify_maven_advisories.subprocess.run")
    def test_007_rejects_exit_and_advisory_report_disagreement(self, run):
        run.side_effect = self.response(code=1)
        with self.assertRaisesRegex(ValueError, "report disagree"):
            self.scan()
        packages = [self.package | {"vulnerabilities": [{"id": "OSV-TEST-0007"}]}]
        run.side_effect = self.response(packages=packages)
        with self.assertRaisesRegex(ValueError, "report disagree"):
            self.scan()

    @patch("verify_maven_advisories.subprocess.run")
    def test_008_bad_json_and_jar_mismatch_do_not_pass(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, b"{")
        with self.assertRaises(json.JSONDecodeError):
            self.scan()
        run.reset_mock()
        self.artifact.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "JAR SHA-256 mismatch"):
            self.scan()
        run.assert_not_called()

    @patch("verify_maven_advisories.subprocess.run")
    def test_009_empty_verified_bom_is_not_a_clean_scan(self, run):
        self.document["components"] = []
        self.document["dependencies"] = [{"ref": ROOT, "dependsOn": []}]
        self.bom.write_text(json.dumps(self.document), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "no Maven JARs"):
            self.scan()
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
