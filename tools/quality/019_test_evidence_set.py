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
database = module("inspector_database_collector", "021_collect_inspector_database_evidence.py")
launch = module("inspector_launch_collector", "022_collect_inspector_launch_evidence.py")
backup = module("backup_rerun_collector", "023_collect_backup_rerun_evidence.py")
scenario = module("scenario_collector", "006_collect_scenario_evidence.py")


class EvidenceSetTest(unittest.TestCase):
    @staticmethod
    def record_fixture():
        cls = "dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest"
        names = ("literalRecords", "identityTemporalBoundaries", "malformedSources", "scalarAliases",
                 "completionInvariants", "nullContracts", "ownershipAndRedaction", "concurrentUse")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 38)}

    def test_run_record_inventory_and_nonpassing_cases(self):
        suite, expected = self.record_fixture()
        self.assertEqual(suite.get("name"), batch.RECORD_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.RECORD_METHODS)
        self.assertEqual(expected, batch.validate_record_suite(suite))
        prefix = "12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\n"
        activation = "fedcba98-7654-3210-8fed-cba987654321\n"
        end = "2026-09-12T05:06:07.234567Z\n"
        traces = {"PT-BAT-038-anchor.txt": ("NKRUN1\n" + prefix).encode("ascii"),
                  "PT-BAT-038-activation.txt": ("NKACT1\n" + prefix + activation).encode("ascii"),
                  "PT-BAT-038-completion-0.txt": ("NKDONE1\n" + prefix + activation + end + "0\n").encode("ascii"),
                  "PT-BAT-038-completion-10.txt": ("NKDONE1\n" + prefix + activation + end + "10\n").encode("ascii")}
        self.assertEqual(traces, batch.RECORD_TRACES)
        self.assertIsNone(batch.validate_record_traces(traces))
        for name in traces:
            wrong = dict(traces); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_record_traces(wrong)
            wrong = dict(traces); wrong[name] = b"unknown"
            with self.assertRaises(ValueError): batch.validate_record_traces(wrong)
        with self.assertRaises(ValueError): batch.validate_record_traces(dict(traces, unknown=b""))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)
        for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_record_suite(wrong)

    @staticmethod
    def handoff_fixture():
        cls = "dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoffTest"
        names = ("actualTransactionHandoff", "preconditionsAndReentrantLock", "callbackFailuresAndNull",
                 "reacquisitionConflict", "jdbcFailureMatrix", "invalidResultMatrix",
                 "stateChangesAndInterrupts", "concurrentGapCompetition")
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 30)}

    def test_handoff_inventory_and_nonpassing_cases(self):
        suite, expected = self.handoff_fixture()
        self.assertEqual(suite.get("name"), batch.HANDOFF_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.HANDOFF_METHODS)
        self.assertEqual(expected, batch.validate_handoff_suite(suite))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)
        for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_handoff_suite(wrong)

    def test_shared_batch_program_ownership(self):
        names = ("dev.codex.schubert.nk.batch.repository.CleanupRepositoryTest",
                 "dev.codex.schubert.nk.batch.cleanup.LogCleanupServiceTest",
                 "dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoffTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest",
                 "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest",
                 "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest",
                 "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest",
                 "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest",
                 "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest",
                 "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest",
                 "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest",
                 "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest")
        suites = [ET.Element("testsuite", name=n) for n in names]
        self.assertEqual(suites[:4], batch.select_program_suites(suites))
        for bad in ([], suites[:-1], suites + [suites[0]], [suites[0], suites[0], suites[2]]):
            with self.assertRaises(ValueError): batch.select_program_suites(bad)
        # BUG-150/YKT-116: visit every independently specified class after inventory growth.
        for position in range(len(suites)):
            bad = copy.deepcopy(suites); bad[position].set("name", "unknown")
            with self.assertRaises(ValueError): batch.select_program_suites(bad)
            bad = copy.deepcopy(suites); del bad[position]
            with self.assertRaises(ValueError): batch.select_program_suites(bad)
            bad = copy.deepcopy(suites); bad[position] = copy.deepcopy(suites[(position + 1) % len(suites)])
            with self.assertRaises(ValueError): batch.select_program_suites(bad)

    def test_shared_storage_program_ownership(self):
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage.LinuxFileLockTest"))
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest"))
        self.assertFalse(scenario.scenario_storage_suite("dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest"))
        for name in ("LinuxDirectoryCallsTest", "OwnedTransferDirectoryTest", "LinuxInodeSecurityTest"):
            self.assertTrue(scenario.scenario_storage_suite("dev.codex.schubert.nk.storage." + name))

    def test_current_ownership_and_scope_descriptions(self):
        suffix = ("Full module coverage includes both; OPS IDs are certified separately by022/018_NK-OPS-001. "
                  "No duplicate PT credit.")
        self.assertEqual("Batch module65 PT = NK-BAT-00137 + NK-OPS-00128. " + suffix,
                         batch.ownership_description(65, 37))
        self.assertEqual("Batch module91 PT = NK-BAT-00137 + NK-OPS-00154. " + suffix,
                         batch.ownership_description(91, 37))
        self.assertEqual("Batch module107 PT = NK-BAT-00137 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(107, 37))
        self.assertEqual("Batch module115 PT = NK-BAT-00145 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(115, 45))
        self.assertEqual(("OS lock continuity and child termination",
                          "durable authoritative run and parent lifecycle", "real backup artifact and full cleanup callers",
                          "actual root systemd credential deployment", "actual NK characterization and IT/ST"),
                         launch.UNVERIFIED_PARENT_GATES)
        self.assertIn("borrowed-root admission/read/publish", launch.DEPLOYMENT_LIMITATIONS)
        self.assertIn("Root UID/GID/tmpfs admission is synthetic", launch.DEPLOYMENT_LIMITATIONS)
        for gate_name in launch.UNVERIFIED_PARENT_GATES:
            self.assertIn(gate_name, launch.DEPLOYMENT_LIMITATIONS)
        self.assertEqual((
            {"method": "MaintenanceFileLock.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS341/343 require fixed Linux /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-LOCK-007", "coverageExcluded": False},
            {"method": "InspectorEnvironmentFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /etc and /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-NS-008", "coverageExcluded": False}),
            launch.REVIEWED_STATIC_DIAGNOSTICS)

    def test_backup_rerun_inventory_and_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.BackupRerunBoundaryTest"
        names = ("sameDayBackupReruns", "ordinarySuccessStillUnique", "attemptAndDateBoundaries",
                 "failureAndLatestSuccessHistory", "transactionRollbackAndMigration",
                 "concurrentSuccessAndAttemptConflicts", "cleanupGatesWithRepeatedBackups", "catalogAndPrivileges")
        self.assertEqual(cls, backup.CLASS)
        self.assertEqual(names, backup.METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual({f"PT-DB-INBOX-{i:03}": cls + "#" + name for i, name in enumerate(names, 233)}, backup.validate_suite(suite))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): backup.validate_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): backup.validate_suite(wrong)
        for key, value in (("tests", "7"), ("name", "other"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): backup.validate_suite(wrong)
        for key, value in (("name", "other"), ("name", names[1]), ("classname", "other")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): backup.validate_suite(wrong)

    def test_launch_inventory_and_nonpassing_cases(self):
        prefix = "dev.codex.schubert.nk.api.maintenance."
        groups = [(prefix + "InspectorLaunchConfigurationTest", 221,
                   ("validConfiguration", "missingUnknownAndArguments", "scalarBoundaries", "versionAndSnapshotContracts")),
                  (prefix + "InspectorLauncherTest", 225,
                   ("successWarningAndFailureStatus", "expectedFailuresAndRedaction", "nativeFactoryFailure", "receiptAndOutputFailure",
                    "nullContracts", "mainAndFatalHandler", "concurrentInvocations", "actualJvmEntry"))]
        self.assertEqual(groups, list(launch.GROUPS))
        self.check_launch_inventory(groups, False)

    def test_deployment_inventory_and_nonpassing_cases(self):
        groups = [("dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest", 1,
                   ("renderedShellCheck", "statusMapping", "malformedReceipts", "argumentsAndPlaceholders",
                    "realMainBridge", "baseUnitAndSyntax", "previousProfiles", "releaseClasspathAndIsolation")),
                  ("dev.codex.schubert.nk.storage.LinuxFileLockTest", 1,
                   ("nativeRoundTrip", "externalFlockInteroperability", "fcntlIsNotFlock", "callbackFailureAndClose",
                    "nativeErrorsAndFlags", "inputAndPlatformContracts", "concurrentSingleWinner", "retainedInodeAndDescriptorLifetime")),
                  ("dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest", 1,
                   ("admittedRealLock", "contentionAndIndependentInvocations", "rootAndFilesystemPolicy", "inodeAndAttributePolicy",
                    "replacementAndPostconditions", "ioAndCloseFailures", "constructorAndNativeBoundary", "fixedProvisioningContract")),
                  ("dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest", 1,
                   ("literalAndOrder", "nonStoppedStates", "malformedFields", "byteAndNullContracts",
                    "gateOrderAndFreshReads", "interruptAndFailure", "concurrentChecks", "factoryAndContracts")),
                  ("dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest", 9,
                   ("fixedCommandAndSuccess", "commandFailure", "timeoutAndTermination", "interruptedWait",
                    "outputBoundaries", "closeFailures", "nativeEnvironmentAndRead", "nullAndRuntimeContracts")),
                  ("dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest", 1,
                   ("independentGolden", "mutationAndRunBinding", "boundariesNullAndOwnership", "concurrentUse")),
                  ("dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest", 1,
                   ("canonicalFixtures", "sourceAndSyntaxRejection", "urlBoundaries", "versionBoundaries", "sizeNullAndRedaction", "concurrentValidation")),
                  ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest", 1,
                   ("staticReadAndBoundaries", "runReadAndBinding", "permissionAndFilesystem", "metadataAndNull",
                    "boundedReadsAndMutation", "inodeReplacementAndOwnership", "ioFaultsAndRedaction", "concurrentAndConstructor")),
                  ("dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest", 1,
                   ("nativePrivateCreation", "atomicNoReplace", "scopedOwnership", "nameAndNullContracts",
                    "faultAndUncertainOutcomes", "retainedNamespace", "concurrentSinglePublication", "unsupportedAndNativeArguments")),
                  ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest", 1,
                   ("createAndRetire", "sameRunAndDifferentRun", "privatePartCollisions", "permissionsAndNull",
                    "boundedWrites", "replacementsAndRetention", "createFailureMatrix", "reuseFailureMatrix",
                    "retireFailureMatrix", "interruptionAndRuntime", "concurrentInvocations", "nativeAndConstructor")),
                  ("dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest", 1,
                   ("canonicalByteBoundaries", "malformedAndNull", "ownedCommandAndExit", "timeoutInterruptAndTermination",
                    "stdioFailureMatrix", "sourceBufferAndNoLeak", "concurrentLookup", "nativeFactory")),
                  ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest", 1,
                   ("prepareCallbackRetire", "callbackFailureRetention", "namespaceAndStaticIdentity", "permissionsAndAccounts",
                    "allOpenCloseFailures", "lateFailureAndInterruption", "concurrentScopes", "constructorAndFactory"))]
        self.assertEqual(groups, list(launch.DEPLOYMENT_GROUPS))
        self.check_launch_inventory(groups, True)

    def check_launch_inventory(self, groups, deployment):
        suites, expected = [], {}
        for cls, start, names in groups:
            prefix = ({"dev.codex.schubert.nk.storage.LinuxFileLockTest": "PT-OPS-FLOCK",
                       "dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest": "PT-OPS-LOCK",
                       "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest": "PT-OPS-STOP",
                       "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest": "PT-OPS-STOP",
                       "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest": "PT-OPS-ENV",
                       "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest": "PT-OPS-CFG",
                       "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest": "PT-OPS-EFILE",
                       "dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest": "PT-OPS-PFILE",
                       "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest": "PT-OPS-PUB",
                       "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest": "PT-OPS-GID",
                       "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest": "PT-OPS-NS"}.get(cls, "PT-OPS-INBOX")
                      if deployment else "PT-DB-INBOX")
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for i, name in enumerate(names, start):
                ET.SubElement(suite, "testcase", classname=cls, name=name)
                expected[f"{prefix}-{i:03}"] = cls + "#" + name
            suites.append(suite)
        self.assertEqual(expected, launch.validate_reports(suites, deployment))
        with self.assertRaises(ValueError): launch.validate_reports(suites, not deployment)
        for index, suite in enumerate(suites):
            for position in range(len(suite)):
                wrong = copy.deepcopy(suites); wrong[index].remove(wrong[index][position])
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suites); ET.SubElement(wrong[index][0], tag)
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suites); wrong[index].set(key, value)
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
            for key, value in (("classname", "unknown"), ("name", "unknown"), ("name", suite[1].get("name"))):
                wrong = copy.deepcopy(suites); wrong[index][0].set(key, value)
                with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)
        for wrong in ([], suites[:-1], suites + [suites[0]]):
            with self.assertRaises(ValueError): launch.validate_reports(wrong, deployment)

    def test_application_inventory_and_nonpassing_cases(self):
        prefix = "dev.codex.schubert.nk.api."
        groups = [
            (prefix + "maintenance.InspectorSettingsTest", 209,
             ("validSnapshot", "invalidSettings", "sharedValidation")),
            (prefix + "file.InspectorApplicationTest", 212,
             ("successAndResume", "protectedResult", "databaseFailure", "credentialFailures", "rootFailures",
              "nativeAdmission", "nullContracts", "interruptedExecution", "concurrentLifetimes"))]
        self.assertEqual(groups, list(database.APPLICATION_GROUPS))
        suites = []
        expected = {}
        for cls, start, names in groups:
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for i, name in enumerate(names, start):
                ET.SubElement(suite, "testcase", classname=cls, name=name)
                expected[f"PT-DB-INBOX-{i:03}"] = cls + "#" + name
            suites.append(suite)
        self.assertEqual(expected, database.validate_reports(suites, True))
        with self.assertRaises(ValueError): database.validate_reports(suites)
        for index, suite in enumerate(suites):
            for position in range(len(suite)):
                wrong = copy.deepcopy(suites); wrong[index].remove(wrong[index][position])
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
                wrong = copy.deepcopy(suites); ET.SubElement(wrong[index][0], tag)
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suites); wrong[index].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
            for key, value in (("classname", "unknown"), ("name", "unknown"), ("name", suite[1].get("name"))):
                wrong = copy.deepcopy(suites); wrong[index][0].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong, True)
        for wrong in ([], suites[:-1], suites + [suites[0]], [suites[0]] * 2):
            with self.assertRaises(ValueError): database.validate_reports(wrong, True)

    def test_database_credential_inventory_and_nonpassing_cases(self):
        prefix = "dev.codex.schubert.nk.api."
        groups = [
            (prefix + "maintenance.InspectorDbCredentialTest", 193,
             ("validUtf8AndNewlines", "invalidEncodingAndBounds", "ownedCopiesAndClose", "concurrentOwnership")),
            (prefix + "file.InspectorDatabaseCredentialLoaderTest", 197,
             ("validBoundedFile", "missingAndInvalidContent", "permissionsAndMetadata", "ioFailuresAndCleanup", "concurrentFilesAndAesRegression")),
            (prefix + "maintenance.InspectorDatabaseConnectionsTest", 202,
             ("fixedConnectionProperties", "urlAndNullContracts", "connectionAdmission", "sqlFailuresRemainRedacted",
              "closeAndConcurrentOpen", "realScramRoleAndPassword", "ownedInspectionConnection"))]
        self.assertEqual(groups, list(database.GROUPS))
        suites = []
        expected = {}
        for cls, start, names in groups:
            suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
            for i, name in enumerate(names, start):
                ET.SubElement(suite, "testcase", classname=cls, name=name)
                expected[f"PT-DB-INBOX-{i:03}"] = cls + "#" + name
            suites.append(suite)
        self.assertEqual(expected, database.validate_reports(suites))
        for index, suite in enumerate(suites):
            for position in range(len(suite)):
                wrong = copy.deepcopy(suites); wrong[index].remove(wrong[index][position])
                with self.assertRaises(ValueError): database.validate_reports(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
                wrong = copy.deepcopy(suites); ET.SubElement(wrong[index][0], tag)
                with self.assertRaises(ValueError): database.validate_reports(wrong)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suites); wrong[index].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong)
            for key, value in (("classname", "unknown"), ("name", "unknown"), ("name", suite[1].get("name"))):
                wrong = copy.deepcopy(suites); wrong[index][0].set(key, value)
                with self.assertRaises(ValueError): database.validate_reports(wrong)
        for wrong in ([], suites[:-1], suites + [suites[0]], [suites[0]] * 3):
            with self.assertRaises(ValueError): database.validate_reports(wrong)

    def test_mutation_inventory_rejects_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.QuestionMutationInboxInspectorTest"
        names = ["validMutationReferences", "submitReferencesAndWork", "cancellationHistory",
                 "deletionHistoryAndAnswers", "exactStoredProfiles", "wireAndMetadataDamage",
                 "nullAndJdbcFailures", "equalTimeTargetsRemainDistinct", "leastPrivilegeCatalog",
                 "uniqueWorkProjection", "referencesAndPhantomsStayLocked", "canonicalRoutesAndRetention",
                 "ownedAtomicFailures", "durableMixedResume", "concurrentReferencesStayIndependent", "appendOnlyInventory"]
        self.assertEqual(cls, inspection.MUTATION_CLASS)
        self.assertEqual(names, inspection.MUTATION_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="16", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual(16, len(inspection.validate_suite(suite, cls, names)))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite)
            wrong.remove(wrong[position])
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for kind in ("failure", "error", "skipped", "flakyFailure", "rerunFailure"):
            wrong = copy.deepcopy(suite)
            ET.SubElement(wrong[0], kind)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("tests", "15"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite)
            wrong.set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)
        for key, value in (("classname", "Wrong"), ("name", "unknown"), ("name", names[1])):
            wrong = copy.deepcopy(suite)
            wrong[0].set(key, value)
            with self.assertRaises(ValueError):
                inspection.validate_suite(wrong, cls, names)

    def test_result_binding_inventory_rejects_nonpassing_cases(self):
        cls = "dev.codex.schubert.nk.api.maintenance.ResultBoundResponseSnapshotCodecTest"
        names = ["independentWriteAndReadAllRoutes", "nullIdentityAndReferenceContracts",
                 "everyMetadataByteIsAuthenticated", "exactLengthAndLegacyRejection",
                 "keysAadAndCipherDamage", "borrowedOwnershipAndRedaction",
                 "concurrentBindingsNeverCross", "equalBusinessTimesDoNotAuthorizeAnotherTarget"]
        self.assertEqual(cls, inspection.BINDING_CLASS)
        self.assertEqual(names, inspection.BINDING_METHODS)
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names:
            ET.SubElement(suite, "testcase", classname=cls, name=name)
        self.assertEqual(8, len(inspection.validate_suite(suite, cls, names)))
        for position in range(len(suite)):
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
        for position in range(len(suite)):
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
        for position in range(len(suite)):
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
        handoff, expected_handoff = self.handoff_fixture()
        records, expected_records = self.record_fixture()
        reports = [suite, repository, handoff, records]
        accepted = batch.validate_reports(reports)
        self.assertEqual(45, len(accepted))
        self.assertEqual(expected_records, {k: v for k, v in accepted.items() if k in expected_records})
        self.assertEqual(expected_handoff, {k: v for k, v in accepted.items() if k in expected_handoff})
        self.assertEqual(expected, {k: v for k, v in accepted.items() if k in expected})
        for position in range(len(reports)):
            wrong = copy.deepcopy(reports); del wrong[position]
            with self.assertRaises(ValueError): batch.validate_reports(wrong)
            wrong = copy.deepcopy(reports); wrong[position].set("name", "unknown")
            with self.assertRaises(ValueError): batch.validate_reports(wrong)
            wrong = copy.deepcopy(reports); wrong[position] = copy.deepcopy(reports[(position + 1) % len(reports)])
            with self.assertRaises(ValueError): batch.validate_reports(wrong)
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
        self.assertEqual("NK-DAT-001", media.shared_file_program(prefix + "InspectorDatabaseCredentialLoaderTest"))
        self.assertEqual("NK-DAT-001", media.shared_file_program(prefix + "InspectorApplicationTest"))
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
                "inspector-process", "log-cleanup-progress", "question-query", "result-binding", "question-mutation", "inspector-database", "inspector-application", "inspector-launch")] + ["018_NK-OPS-001/evidence", "004_NK-DAT-001/evidence/backup-rerun"]
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
            self.assertEqual(35, len(check()))
            outside = root / "outside.xml"
            outside.write_bytes(b"fixture")
            link = directory / "escape.xml"
            link.symlink_to(outside)
            for relative in ("", "../results.xml", str(outside), "missing.xml", "escape.xml"):
                with self.assertRaises(ValueError):
                    gate.local_file(directory, relative)

    def test_collection_stops_at_each_failure(self):
        for failed_at in range(35):
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
        self.assertEqual(35, len(calls))
        self.assertTrue(calls[0][2].endswith("/006_collect_scenario_evidence.py"))
        self.assertTrue(calls[-1][2].endswith("/023_collect_backup_rerun_evidence.py"))
        self.assertEqual("PT-WEB-TEST", calls[-1][-1])

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
        if scope.startswith(("004_", "017_", "018_")):
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
