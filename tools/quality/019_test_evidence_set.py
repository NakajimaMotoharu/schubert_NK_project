#!/usr/bin/env python3
"""PT-QA-TRACE-002/003 independent inventory/run/failure canaries; no production secrets."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


media = module("media_collector", "009_collect_media_evidence.py")
gate = module("set_collector", "018_collect_verified_evidence_set.py")
batch = module("batch_collector", "020_collect_batch_evidence.py")
inspection = module("inspection_collector", "016_collect_inbox_inspection_evidence.py")


class EvidenceSetTest(unittest.TestCase):
    def test_question_query_inventory_rejects_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.QuestionQueryInboxCleanupTest"
        names = ["queryProfilesAndFrozenSnapshots", "goldenBoundsAndSemanticDamage",
                 "canonicalIdentityReferencesAndNulls", "validRowsDeleteAndRetainExactMetadata",
                 "retentionBackupAndSqlAuthority", "failuresRollbackAndResume",
                 "concurrentAndDurableMixedRuns", "appendOnlyInventoryAndClosedRoutes"]
        self.assertEqual(cls, inspection.QUESTION_CLASS)
        self.assertEqual(names, inspection.QUESTION_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual(8, len(inspection.validate_suite(suite, cls, names)))
        for position in range(8):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("tests", "7"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("classname", "Wrong"), ("name", "unknown"), ("name", names[1])):
            wrong = copy.deepcopy(suite)
            wrong[0].set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)

    def test_log_service_class_and_pt_ids_are_mandatory(self):
        cls = "dev.codex.schubert.nk.batch.cleanup.LogCleanupServiceTest"
        names = ["emptyAndCompletedRuns", "heldPrefixAndLargeChunks", "resumedAttemptCounts", "sessionLockOwnership",
                 "backupAndRowLockStop", "timeBoundaryAndClockWrap", "interruptsRemainSet", "rollbackAndUncertainCommit",
                 "restorationAndUnlockFailures", "invalidInputsAndProjections", "summaryInvariants", "failuresLeaveNoFalseSuccess"]
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        expected = {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 18)}
        self.assertEqual(expected, batch.validate_log_suite(suite))
        for position in range(12):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                batch.validate_log_suite(wrong)
        for kind in ("failure", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                batch.validate_log_suite(wrong)
        # Repository method ownership is independently checked by the next test.
        repository = ET.Element("testsuite", name=batch.CLASS, tests="17", failures="0", errors="0", skipped="0")
        for name in batch.METHODS:
            ET.SubElement(repository, "testcase", classname=batch.CLASS, name=name)
        accepted = batch.validate_reports([suite, repository])
        self.assertEqual(29, len(accepted))
        self.assertEqual(expected, {k: v for k, v in accepted.items() if k in expected})
        for reports in ([], [suite], [repository], [suite, suite], [repository, repository], [suite, repository, suite]):
            with self.assertRaises(ValueError):
                batch.validate_reports(reports)

    def test_batch_inventory_rejects_unrun_and_changed_tests(self):
        names = ["runIdentityBoundaries", "countInvariants", "cleanupAllowlist", "rejectionAndProgressContracts",
                 "emptyCleanupAndExplicitTransaction", "heldLogsAndDurableRead", "rollbackSavepointAndResume",
                 "backupAndAdvisoryRejection", "exactLimitsAndNullInputs", "rowProjectionFailures",
                 "progressProjectionFailures", "jdbcFailuresRemainRedacted", "roleIsolationAndNoInboxBypass",
                 "timezoneAndCutoffIdentity", "lockedLogsDoNotAdvance", "retentionAndResourceOwnership",
                 "moduleDependencyBoundary"]
        cls = "dev.codex.schubert.nk.batch.repository.CleanupRepositoryTest"
        suite = ET.Element("testsuite", name=cls, tests="17", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 1)}, batch.validate_suite(suite))
        for key, value in (("name", "Wrong"), ("tests", "16"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                batch.validate_suite(wrong)
        for kind in ("missing", "duplicate", "unknown", "wrong-class", "failure", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            if kind == "missing":
                wrong.remove(wrong[0])
            elif kind == "duplicate":
                wrong.append(copy.deepcopy(wrong[0]))
            elif kind == "unknown":
                wrong[0].set("name", "newUnmappedTest")
            elif kind == "wrong-class":
                wrong[0].set("classname", "Other")
            else:
                ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                batch.validate_suite(wrong)

    def test_shared_package_and_exact_method_ownership(self):
        prefix = "dev.codex.schubert.nk.api.file."
        for name in ("AssetChecksumManifestTest", "AssetManifestLoaderTest", "HeldMediaFileInspectorTest"):
            self.assertEqual("NK-MED-001", media.shared_file_program(prefix + name))
        self.assertEqual("NK-DAT-001", media.shared_file_program(prefix + "InspectorCredentialLoaderTest"))
        for name in ("NewMediaTest", "", "InspectorCredentialLoaderTest"):
            with self.assertRaisesRegex(ValueError, "unmapped"):
                media.shared_file_program(name)
        expected = {"PT-MED-X": "A#one", "PT-MED-Y": "B#two"}
        media.validate_method_inventory(["B#two", "A#one"], expected)
        for methods in (["A#one"], ["A#one", "B#two", "A#new"],
                        ["A#one", "A#one"], ["A#one", "C#two"]):
            with self.assertRaisesRegex(ValueError, "Test IDs"):
                media.validate_method_inventory(methods, expected)

    def test_every_scope_run_source_and_integrity(self):
        # Independently enumerated mandatory inventory, not generated from gate.SCOPES.
        expected_scopes = ["008_NK-SCN-001", "007_NK-AUT-001", "003_NK-PRO-003",
                           "006_NK-MSG-002", "009_NK-MED-001", "010_NK-ADM-001", "015_NK-WEB-001", "017_NK-BAT-001"]
        expected_scopes = [p + "/evidence" for p in expected_scopes] + [
            "004_NK-DAT-001/evidence/" + p for p in (
                "inbox-inspection", "authentication-inspection", "inspection-sql", "deletion-sql",
                "authentication-cleanup", "non-authentication-inspection", "full-inbox-sql",
                "full-inbox-cleanup", "outbox-only-cleanup", "inbox-progress-sql",
                "inbox-progress-service", "cleanup-safety", "inbox-run-executor",
                "inbox-aes-credential", "credential-access", "inode-security", "credential-loader",
                "inspector-process", "log-cleanup-progress", "question-query")]
        self.assertEqual(expected_scopes, list(gate.SCOPES))
        with tempfile.TemporaryDirectory(prefix="nk-evidence-set-") as temporary:
            root = Path(temporary)
            for scope in expected_scopes:
                self.write_scope(root, scope)
            accepted = gate.validate_all(root, "PT-WEB-TEST", "a" * 40, "dev-foundation")
            self.assertEqual(expected_scopes, [item["scope"] for item in accepted])
            # Each scope must reject each wrong binding, even with a consistent checksum file.
            for scope in expected_scopes:
                for field, wrong in (("runId", "PT-WEB-OLD"), ("targetCommit", "b" * 40),
                                     ("branch", "main"), ("exitCode", 1)):
                    self.write_scope(root, scope, {field: wrong})
                    with self.assertRaisesRegex(ValueError, "mixed"):
                        gate.validate_scope(root, scope, "PT-WEB-TEST", "a" * 40, "dev-foundation")
                self.write_scope(root, scope)
            chosen = expected_scopes[-1]
            directory = root / chosen
            check = lambda: gate.validate_all(root, "PT-WEB-TEST", "a" * 40, "dev-foundation")
            baseline = (directory / "manifest.json").read_bytes()
            for wrong in ("missing.xml", "../results.xml", "/tmp/outside"):
                m = json.loads(baseline)
                m["files"][0]["path"] = wrong
                self.write_scope(root, chosen, m)
                with self.assertRaises(ValueError):
                    check()
            self.write_scope(root, chosen)
            for name in ("manifest.json", "results.xml", "checksums.sha256"):
                path = directory / name
                original = path.read_bytes()
                path.unlink()
                with self.assertRaises((ValueError, FileNotFoundError)):
                    check()
                path.write_bytes(original)
            (directory / "results.xml").write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "hash"):
                check()
            self.write_scope(root, chosen)
            for values in (
                {"files": []},
                {"files": json.loads(baseline)["files"] * 2},
                {"fullReactorManifest": "manifest.json"},
                {"fullReactorManifestSha256": "0" * 64},
            ):
                self.write_scope(root, chosen, values)
                with self.assertRaises(ValueError):
                    check()
            self.write_scope(root, chosen)
            original = (directory / "checksums.sha256").read_text()
            for wrong in ("bad\n", "", original + original, original.replace("  results.xml", "  unknown.xml")):
                (directory / "checksums.sha256").write_text(wrong)
                with self.assertRaises(ValueError):
                    check()
            self.write_scope(root, chosen)
            self.assertEqual(28, len(check()))
            outside = root / "outside.xml"
            outside.write_bytes(b"fixture")
            link = directory / "escape.xml"
            link.symlink_to(outside)
            for relative in ("", "../results.xml", str(outside), "missing.xml", "escape.xml"):
                with self.assertRaises(ValueError):
                    gate.local_file(directory, relative)

    def test_collection_stops_at_each_failure(self):
        for failed_at in range(28):
            calls = []
            def fail(command, *, cwd, check):
                self.assertEqual(Path("/safe/repo"), cwd)
                self.assertTrue(check)
                calls.append(command)
                if len(calls) == failed_at + 1:
                    raise subprocess.CalledProcessError(1, command)
            with self.assertRaises(subprocess.CalledProcessError):
                gate.collect(Path("/safe/repo"), "PT-WEB-TEST", fail)
            self.assertEqual(failed_at + 1, len(calls))
        calls = []
        gate.collect(Path("/safe/repo"), "PT-WEB-TEST", lambda cmd, **kwargs: calls.append(cmd))
        self.assertEqual(28, len(calls))
        self.assertTrue(calls[0][2].endswith("/006_collect_scenario_evidence.py"))
        self.assertEqual("--question-query", calls[-1][-1])

    @staticmethod
    def write_scope(root, scope, changes=None):
        directory = root / scope
        directory.mkdir(parents=True, exist_ok=True)
        payload = b"<testsuite/>\n"
        (directory / "results.xml").write_bytes(payload)
        manifest = {
            "runId": "PT-WEB-TEST", "targetCommit": "a" * 40,
            "branch": "dev-foundation", "exitCode": 0,
            "files": [{"path": "results.xml", "sha256": hashlib.sha256(payload).hexdigest()}],
        }
        if scope.startswith(("004_", "017_")):
            manifest.update({
                "fullReactorManifest": ("../../../" if scope.startswith("004_") else "../../") + "008_NK-SCN-001/evidence/manifest.json",
                "fullReactorManifestSha256": hashlib.sha256(
                    (root / "008_NK-SCN-001/evidence/manifest.json").read_bytes()).hexdigest(),
            })
        manifest.update(copy.deepcopy(changes or {}))
        (directory / "manifest.json").write_text(json.dumps(manifest))
        (directory / "checksums.sha256").write_text("".join(
            hashlib.sha256((directory / name).read_bytes()).hexdigest() + "  " + name + "\n"
            for name in ("manifest.json", "results.xml")))


if __name__ == "__main__":
    unittest.main()
