"""Independent three-byte artifact fixtures for PT-OPS-SBOM-014..020."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verify_maven_sbom import verify_model_bom


ROOT = "pkg:maven/local.example/nk@1?type=jar"
DEPENDENCY = "pkg:maven/org.example/model@2.0?type=jar"
CLASSIFIED = "pkg:maven/org.example/model@2.0?classifier=variant&type=jar"
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
SCRIPT = Path(__file__).resolve().parents[1] / "verify_maven_sbom.py"


class VerifyMavenSbomTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        self.repository = self.scratch / "repository"
        self.artifact = self.repository / "org/example/model/2.0/model-2.0.jar"
        self.artifact.parent.mkdir(parents=True)
        self.artifact.write_bytes(b"abc")

    def fixture(self):
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "metadata": {"component": {"bom-ref": ROOT}},
            "components": [{
                "group": "org.example",
                "name": "model",
                "version": "2.0",
                "bom-ref": DEPENDENCY,
                "purl": DEPENDENCY,
                "hashes": [{"alg": "SHA-256", "content": ABC_SHA256}],
                "licenses": [{"license": {"id": "Apache-2.0"}}],
            }],
            "dependencies": [
                {"ref": ROOT, "dependsOn": [DEPENDENCY]},
                {"ref": DEPENDENCY, "dependsOn": []},
            ],
        }

    def test_fixed_hash_and_graph(self):
        self.assertEqual(
            {"rootRef": ROOT, "verifiedJarHashes": 1, "dependencyRows": 2,
             "missingLicenseMetadata": []},
            verify_model_bom(self.fixture(), self.repository),
        )

    def test_classifier_hash_is_distinct_from_the_default_artifact(self):
        data = self.fixture()
        data["components"][0].update({"bom-ref": CLASSIFIED, "purl": CLASSIFIED})
        data["dependencies"] = [
            {"ref": ROOT, "dependsOn": [CLASSIFIED]},
            {"ref": CLASSIFIED, "dependsOn": []},
        ]
        self.artifact.with_name("model-2.0-variant.jar").write_bytes(b"abc")
        self.artifact.write_bytes(b"other bytes")
        self.assertEqual(1, verify_model_bom(data, self.repository)["verifiedJarHashes"])

    def test_absent_license_is_reported_and_invalid_entries_fail(self):
        data = self.fixture()
        data["components"][0].pop("licenses")
        self.assertEqual(
            [DEPENDENCY], verify_model_bom(data, self.repository)["missingLicenseMetadata"]
        )
        for licenses in ("Apache-2.0", [None], [{"license": {"url": "https://example.test"}}],
                         [{"expression": " "}], [{"expression": "MIT", "license": {"id": "MIT"}}]):
            with self.subTest(licenses=licenses):
                data["components"][0]["licenses"] = licenses
                with self.assertRaisesRegex(ValueError, "malformed license"):
                    verify_model_bom(data, self.repository)
        for licenses in ([{"expression": "MIT OR Apache-2.0"}], [{"license": {"name": "Test"}}]):
            with self.subTest(licenses=licenses):
                data["components"][0]["licenses"] = licenses
                self.assertEqual([], verify_model_bom(data, self.repository)["missingLicenseMetadata"])

    def test_wrong_and_ambiguous_artifact_hashes_fail(self):
        data = self.fixture()
        self.artifact.write_bytes(b"def")
        with self.assertRaisesRegex(ValueError, "JAR SHA-256 mismatch"):
            verify_model_bom(data, self.repository)
        data["components"][0]["hashes"] *= 2
        with self.assertRaisesRegex(ValueError, "expected one SHA-256"):
            verify_model_bom(data, self.repository)

    def test_duplicate_unknown_missing_and_unreachable_graph_members_fail(self):
        data = self.fixture()
        root = data["dependencies"][0]
        artifact = data["dependencies"][1]
        variants = (
            ([root, root, artifact], "duplicate, unknown or malformed"),
            ([root, artifact, {"ref": "another", "dependsOn": []}], "duplicate, unknown or malformed"),
            ([{"ref": ROOT, "dependsOn": ["unknown"]}, artifact], "duplicate or unknown dependency target"),
            ([{"ref": ROOT, "dependsOn": [DEPENDENCY, DEPENDENCY]}, artifact], "duplicate or unknown dependency target"),
            ([root], "missing component dependency row"),
            ([{"ref": ROOT, "dependsOn": []}, artifact], "unreachable"),
        )
        for rows, message in variants:
            with self.subTest(rows=rows):
                data["dependencies"] = rows
                with self.assertRaisesRegex(ValueError, message):
                    verify_model_bom(data, self.repository)

    def test_coordinates_reference_and_repository_must_agree(self):
        data = self.fixture()
        for fields, message in (
            ({"name": "../model"}, "invalid Maven coordinates"),
            ({"group": "org..example"}, "invalid Maven coordinates"),
            ({"purl": CLASSIFIED}, "does not match"),
            ({"bom-ref": DEPENDENCY + "&type=jar"}, "duplicate JSON field"),
        ):
            with self.subTest(fields=fields):
                case = copy.deepcopy(data)
                case["components"][0].update(fields)
                with self.assertRaisesRegex(ValueError, message):
                    verify_model_bom(case, self.repository)
        external = self.scratch / "unowned.jar"
        external.write_bytes(b"abc")
        self.artifact.unlink()
        self.artifact.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "outside the selected Maven repository"):
            verify_model_bom(data, self.repository)

    def test_cli_rejects_duplicate_json_and_uses_nonzero_failure_status(self):
        bom = self.scratch / "software-bom.json"
        bom.write_text(json.dumps(self.fixture()), encoding="utf-8")
        command = [sys.executable, str(SCRIPT), str(bom), str(self.repository)]
        valid = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(1, json.loads(valid.stdout)["verifiedJarHashes"])
        bom.write_text('{"bomFormat":"CycloneDX","bomFormat":"CycloneDX"}', encoding="utf-8")
        invalid = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(1, invalid.returncode)
        self.assertEqual("", invalid.stdout)
        self.assertIn("duplicate JSON field", invalid.stderr)
