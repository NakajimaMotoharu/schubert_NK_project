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
references = module("run_reference_collector", "024_collect_run_reference_evidence.py")
parent_summary = module("parent_summary_collector", "025_collect_parent_summary_evidence.py")
atomic = module("atomic_collector", "026_collect_atomic_cleanup_evidence.py")
scenario = module("scenario_collector", "006_collect_scenario_evidence.py")


class EvidenceSetTest(unittest.TestCase):

    @staticmethod
    def atomic_fixture(group):
        cls, names, prefix, start = [
            ("dev.codex.schubert.nk.batch.repository.CleanupStepValuesTest", ("kindStepMapping", "successfulChunkContracts", "rejectionAndDeferredContracts", "summaryCountsAndCompletion", "counterOverflowAndBounds", "nullAndRedaction", "immutableValues", "concurrentValues",), "BAT", 154),
            ("dev.codex.schubert.nk.batch.repository.CleanupStepRepositoryTest", ("actualSevenKindsAndStepTotals", "borrowedStateAndMapping", "nullAndProjection", "allJdbcFailures", "rejectionReasonsAndUnknownTotals", "utcFullHandle", "interruptRuntimeAndResourceOwnership", "concurrentTransactionsAndRollback",), "BAT", 162),
            ("dev.codex.schubert.nk.batch.cleanup.StepCleanupServiceTest", ("allKindsCompleteAndPersistedCounts", "multiChunkResumeAndSharedStep", "lockBackupAndForeignKeyDeferral", "transactionFaultsAndUnknownCommit", "timeoutInterruptAndClockWrap", "counterContinuityAndOverflow", "connectionStateRestorationAndNulls", "concurrencyAndIndependentTrace",), "BAT", 170),
            ("dev.codex.schubert.nk.api.maintenance.StepCleanupBoundaryTest", ("sevenKindAtomicCounts", "handleArgumentsAndIdentity", "backupLockAndRoleBoundary", "zeroChunkLockedRemainder", "retentionAndProtectedRows", "rollbackOverflowAndForeignKey", "typedProjectionAndNoBypass", "appendOnlyMigrationInventory",), "DB-INBOX", 259),
        ][group]
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_atomic_cleanup_inventories(self):
        for group, validate in enumerate((batch.validate_atomic_value_suite, batch.validate_atomic_repository_suite,
                                           batch.validate_atomic_service_suite, atomic.validate_suite)):
            suite, expected = self.atomic_fixture(group)
            self.assertEqual(expected, validate(suite))
            for position in range(8):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_atomic_cleanup_literal_traces(self):
        batch_expected = {
            "PT-BAT-162-seven-kinds.txt": b"NOTIFICATIONS=1|1|END\nQUESTIONS=1|1|END\nSESSIONS=3|3|END\nOUTBOX=2|2|END\nBATCH_RUNS=1|1|END\nINBOX_PROGRESS=2|1|END\nLOG_PROGRESS=3|1|END\n",
            "PT-BAT-165-jdbc.txt": b"repository=53\nfault_positions=53\ndouble_close_pairs=3\n",
            "PT-BAT-171-chunks.txt": b"sessions=1001\nchunks=1000|1|0\nservice_jdbc=171\nresume_delta=0\n",
            "PT-BAT-173-jdbc.txt": b"positive_end=115\nfault_positions=115\ncommit_response_unknown=stored1|resume_delta0\n",
            "PT-BAT-177-service.txt": b"NOTIFICATIONS=RUNNING|1|1|0|0|true\nQUESTIONS=RUNNING|1|1|0|0|true\nSESSIONS=RUNNING|3|3|0|0|true\nOUTBOX=RUNNING|2|2|0|0|true\nBATCH_RUNS=RUNNING|1|1|0|0|true\nINBOX_PROGRESS=RUNNING|2|2|0|0|true\nLOG_PROGRESS=RUNNING|3|3|0|0|true\n",
        }
        sql_expected = {"PT-DB-INBOX-259-seven-kinds.txt": b"NOTIFICATIONS=1|1|0|1|1|false|OK\nQUESTIONS=1|1|0|1|1|false|OK\nSESSIONS=3|3|0|3|3|false|OK\nOUTBOX=2|2|0|2|2|false|OK\nBATCH_RUNS=1|1|0|1|1|false|OK\nINBOX_PROGRESS=1|1|0|2|2|false|OK\nLOG_PROGRESS=1|1|0|3|3|false|OK\n"}
        for expected, constants, validate in ((batch_expected, batch.ATOMIC_TRACES, batch.validate_atomic_traces),
                                               (sql_expected, atomic.TRACES, atomic.validate_traces)):
            self.assertEqual(expected, constants); self.assertIsNone(validate(expected))
            for name in expected:
                missing = dict(expected); del missing[name]
                wrong = dict(expected); wrong[name] += b"X"
                for bad in (missing, wrong, {**expected, "unknown": b""}):
                    with self.assertRaises(ValueError): validate(bad)

    @staticmethod
    def step_fixture(repository=False):
        cls, names, start = (
            ("dev.codex.schubert.nk.batch.repository.BatchRunRepositoryTest",
             ("firstAttemptAndTerminalStates", "ordinarySuccessSkipsByBusinessDate", "backupAlwaysRunsAndAttemptLimit", "explicitAbandonedRecovery", "foreignRunningAndRootIdentity", "exactFinishReplay", "handleIdentityAndMissingRows", "rollbackAndUnknownCommit", "historicalUtcAndFixedRunDay", "clockRegressionPreservesRows", "parentTransactionAndLock", "historyProjectionAndNulls", "jdbcFailurePositions", "interruptionAndRuntime", "concurrentOwnersAndRowLocks", "independentSqlInventoryAndGrants",), 138) if repository else
            ("dev.codex.schubert.nk.batch.repository.BatchStepValuesTest",
             ("closedStepsAndBackupPolicy", "attemptIdentityAndBounds", "terminalStatesAndReasonMatrix", "counterAndStatusBoundaries", "temporalContractAndBusinessDay", "nullContractsAndRedaction", "immutableValueSemantics", "independentConcurrentValues",), 130))
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_parent_step_inventories(self):
        for repository, validate in ((False, batch.validate_step_value_suite), (True, batch.validate_step_repository_suite)):
            suite, expected = self.step_fixture(repository)
            self.assertEqual(expected, validate(suite))
            for position in range(len(suite)):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "1"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_parent_step_literal_traces(self):
        expected = {
            "PT-BAT-138-terminals.txt": b"BACKUP_DB=SUCCESS|5|3|0|9|NULL|NULL\nBACKUP_CONFIG=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\nCLEAN_NOTIFICATION=FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed\nCLEAN_QUESTION=SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable\nCLEAN_SESSION=SUCCESS|5|3|0|9|NULL|NULL\nCLEAN_INBOX_OUTBOX=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\nCLEAN_LOG=FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed\nCLEAN_BATCH_RUN=SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable\nCLEAN_TRANSFER=SUCCESS|5|3|0|9|NULL|NULL\nCLEAN_EXPIRY=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\n",
            "PT-BAT-150-jdbc.txt": b"empty=57/57/2\nhistory=70/70/2\nskip=70/70/2\nrecover=80/80/2\nfinish=50/50/2\nreplay=72/72/2\n",
        }
        self.assertEqual(expected, batch.STEP_TRACES)
        self.assertIsNone(batch.validate_step_traces(expected))
        for name in expected:
            missing = dict(expected); del missing[name]
            wrong = dict(expected); wrong[name] += b"X"
            for bad in (missing, wrong):
                with self.assertRaises(ValueError): batch.validate_step_traces(bad)
        with self.assertRaises(ValueError): batch.validate_step_traces(dict(expected, unknown=b""))
    @staticmethod
    def parent_fixture(kind):
        cls, names, prefix, start = {
            "sql": ("dev.codex.schubert.nk.api.maintenance.InspectionParentBoundaryTest",
                    ("summaryStatesAndCounts", "identityAndTimeBoundaries", "parentLockNamespaces", "roleAndCatalog",
                     "freshReadAndRollback", "concurrentOwners", "noMutationOrPrivateProjection", "appendOnlyMigration"), "PT-DB-INBOX", 251),
            "repository": ("dev.codex.schubert.nk.batch.repository.InspectionSummaryRepositoryTest",
                    ("summaryValueInvariants", "realBoundedRead", "parentStateAndLock", "projectionAndNull",
                     "allJdbcFailurePositions", "historicalUtcIdentity", "freshVisibilityAndBorrowing", "interruptAndRuntime"), "PT-BAT", 114),
            "attempt": ("dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest",
                    ("matchingSuccessAndWarning", "zeroAndResumedAttemptCounts", "completedBaselineImmutability",
                     "countRegressionAndOverflow", "runIdentityAndMissingEnd", "receiptCodesAndNulls",
                     "redactionAndValueOwnership", "independentConcurrentObservations"), "PT-BAT", 122),
        }[kind]
        suite = ET.Element("testsuite", name=cls, tests="8", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_parent_summary_inventories(self):
        for kind, validate in (("sql", parent_summary.validate_suite), ("repository", batch.validate_summary_suite),
                               ("attempt", batch.validate_attempt_suite)):
            suite, expected = self.parent_fixture(kind)
            self.assertEqual(expected, validate(suite))
            for position in range(8):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    def test_parent_summary_literal_trace(self):
        literal = (b"absent=[]\nopen=[0, 0, 0, false]\nemptyEnd=[0, 0, 0, true]\n"
                   b"mixedEnd=[9, 5, 4, true]\nmaxEnd=[9223372036854775807, 9223372036854775806, 1, true]\n")
        expected = {"PT-DB-INBOX-251-states.txt": literal}
        self.assertEqual(expected, parent_summary.TRACES)
        self.assertIsNone(parent_summary.validate_traces(expected))
        for wrong in ({}, dict(expected, unknown=b""), {"PT-DB-INBOX-251-states.txt": literal + b"\0"}):
            with self.assertRaises(ValueError): parent_summary.validate_traces(wrong)

    def test_retirement_literal_traces(self):
        io = b"{acl=1075, attributes=1075, close=854, create=2, filesystem=1075, force=2, namesClose=54, namesHasNext=138, namesIterator=54, namesNext=84, namesOpen=54, openDirectory=477, openEntry=324, openRead=57, openRoot=53, openWriter=2, publish=2, read=114, readClose=57, readSize=114, readonly=1075, sync=13, unlink=5, write=2, writeSize=4, writerClose=2}"
        self.assertEqual(io, batch.RETIREMENT_IO_TRACE)
        with self.assertRaises(ValueError):
            batch.validate_retirement_io(b"{acl=1075, attributes=1075, close=854, create=2, filesystem=1075, force=2, namesClose=54, namesHasNext=138, namesIterator=54, namesNext=84, namesOpen=54, openDirectory=477, openEntry=324, openRead=57, openRoot=53, openWriter=2, publish=2, read=114, readClose=57, readonly=1075, readSize=114, sync=13, unlink=5, write=2, writerClose=2, writeSize=4}")
        self.assertIsNone(batch.validate_retirement_io(io))
        for wrong in (b"", io + b"\0", io.replace(b"openDirectory=477", b"openDirectory=461"),
                      io.replace(b"close=854", b"close=838"), io + b"\n"):
            with self.assertRaises(ValueError): batch.validate_retirement_io(wrong)
        expected = {
            "PT-BAT-090-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
            "PT-BAT-090-maximum.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n2147483647\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
            "PT-BAT-099-two-activation-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-03T00:00:00.000000Z\n2026-02-07T00:00:00.000001Z\n2\ne6ff18dc21a10852fe4de7e8606fe0ad005c8e242bdc535ea8d391dd052528de\n",
            "PT-BAT-102-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
            "PT-BAT-102-phases.txt": b"phase0:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase1:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase2:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase3:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase4:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase5:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nphase6:\n12345678-9abc-def0-8123-456789abcdef.retire\nphase7:\n",
        }
        self.assertEqual(expected, batch.RETIREMENT_TRACES)
        self.assertIsNone(batch.validate_retirement_traces(expected))
        for key in expected:
            wrong = dict(expected); del wrong[key]
            with self.assertRaises(ValueError): batch.validate_retirement_traces(wrong)
            wrong = dict(expected); wrong[key] += b"\0"
            with self.assertRaises(ValueError): batch.validate_retirement_traces(wrong)
        for wrong in ({}, dict(expected, unknown=b"")):
            with self.assertRaises(ValueError): batch.validate_retirement_traces(wrong)

    @staticmethod
    def retirement_fixture(records=False):
        cls = ("dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest" if records else
               "dev.codex.schubert.nk.batch.file.MaintenanceRunRetirementTest")
        names = (("literalMarkerAndPlanHash", "temporalAndCountInvariants", "nullAndOwnership", "malformedMarkerBytes", "markerAliases", "boundedStorageRecords", "planNameBinding", "concurrentCanonicalRecords") if records else
                 ("candidatesAndProtectedRuns", "strictAgeAndLatestCompletion", "referenceCombinations", "missingAndContradictoryIdentity", "newRetirementPreservesOtherRuns", "preMarkerPlanRecovery", "markerOriginalRecovery", "metadataOnlyRecovery", "planCompletenessAndDigest", "namespaceAndForeignArtifacts", "referenceReappearanceAndDbFaults", "publicationAndDeletionCrashes", "everyIoFailurePreservesState", "scopeNullAndInterruption", "concurrentAndClosedScope", "resourceCloseAndDigestFailure"))
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        start = 90 if records else 98
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_retirement_inventory_rejects_nonpassing_cases(self):
        for records in (False, True):
            suite, expected = self.retirement_fixture(records)
            validate = batch.validate_retirement_record_suite if records else batch.validate_retirement_suite
            self.assertEqual(expected, validate(suite))
            for position in range(len(suite)):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "0"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)

    @staticmethod
    def references_fixture(sql=False):
        cls = ("dev.codex.schubert.nk.api.maintenance.RunReferenceBoundaryTest" if sql else
               "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryTest")
        names = (("referenceCombinations", "identityConsistency", "temporalAndNullBoundaries", "lockOwnership",
                  "roleAndCatalog", "transactionVisibility", "concurrentOwnership", "migrationAndReadOnlyHistory", "jdbcUtcVectors", "productionUtcBoundaryInventory") if sql else
                 ("referenceValueInvariants", "realReferenceRead", "transactionAndLockContracts",
                  "projectionAndNullContracts", "jdbcFailureMatrix", "interruptionAndRuntime",
                  "rollbackAndFreshVisibility", "independentConcurrentConnections"))
        suite = ET.Element("testsuite", name=cls, tests=str(len(names)), failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        prefix, start = ("PT-DB-INBOX", 241) if sql else ("PT-BAT", 82)
        return suite, {f"{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(names, start)}

    def test_run_reference_inventories_and_traces(self):
        for sql in (False, True):
            suite, expected = self.references_fixture(sql)
            validate = references.validate_suite if sql else batch.validate_references_suite
            self.assertEqual(expected, validate(suite))
            for position in range(len(suite)):
                wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
                with self.assertRaises(ValueError): validate(wrong)
            for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
                wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("tests", "7"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
                wrong = copy.deepcopy(suite); wrong.set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
            for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
                wrong = copy.deepcopy(suite); wrong[0].set(key, value)
                with self.assertRaises(ValueError): validate(wrong)
        literal = ("0:[false, false, false, true]\n1:[true, false, false, true]\n"
                   "2:[false, true, false, true]\n3:[true, true, false, true]\n"
                   "4:[false, false, true, true]\n5:[true, false, true, true]\n"
                   "6:[false, true, true, true]\n7:[true, true, true, true]\n").encode("ascii")
        traces = {"PT-DB-INBOX-241-combinations.txt": literal}
        self.assertEqual(traces, references.TRACES)
        self.assertIsNone(references.validate_traces(traces))
        for wrong in ({}, dict(traces, unknown=b""), {"PT-DB-INBOX-241-combinations.txt": literal + b"\0"}):
            with self.assertRaises(ValueError): references.validate_traces(wrong)

    @staticmethod
    def lifecycle_fixture():
        cls = "dev.codex.schubert.nk.batch.file.MaintenanceRunFilesTest"
        names = ("newRunPublication", "resumeActive", "resumeOrphanAnchor", "resumePendingBegin",
                 "resumeCompletedHistory", "completedActiveRecovery", "completeSuccessAndWarning",
                 "completionRetryAndMismatch", "noImplicitNewIdentity", "malformedGraphReferences",
                 "ambiguousPendingStates", "inventoryUnknownAndPartial", "namespacePermissions",
                 "namespaceReplacement", "recordReplacementDuringScan", "listingAndIoFailures",
                 "rootAcquisitionAndCloseFailures", "startCrashBoundaries", "resumeCrashBoundaries",
                 "completionCrashBoundaries", "nullAndClosedContracts", "interruptionAndRuntime",
                 "concurrentScopeOwnership", "fixedFactoryAndReopen")
        suite = ET.Element("testsuite", name=cls, tests="24", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 58)}

    def test_run_lifecycle_inventory_and_nonpassing_cases(self):
        suite, expected = self.lifecycle_fixture()
        self.assertEqual(suite.get("name"), batch.LIFECYCLE_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.LIFECYCLE_METHODS)
        self.assertEqual(expected, batch.validate_lifecycle_suite(suite))
        run = "12345678-9abc-def0-8123-456789abcdef"
        activation = "fedcba98-7654-3210-8fed-cba987654321"
        prefix = run + "\n2026-09-12T04:05:06.123456Z\n"
        names = ("attempts/" + activation + ".begin\nattempts/" + activation + ".done\nruns/" + run + ".run\n").encode("ascii")
        traces = {"PT-BAT-058-anchor.txt": ("NKRUN1\n" + prefix).encode("ascii"),
                  "PT-BAT-058-begin.txt": ("NKACT1\n" + prefix + activation + "\n").encode("ascii"),
                  "PT-BAT-058-active.txt": ("NKACT1\n" + prefix + activation + "\n").encode("ascii"),
                  "PT-BAT-064-done-0.txt": ("NKDONE1\n" + prefix + activation + "\n2026-09-12T05:06:07.234567Z\n0\n").encode("ascii"),
                  "PT-BAT-064-done-10.txt": ("NKDONE1\n" + prefix + activation + "\n2026-09-12T05:06:07.234567Z\n10\n").encode("ascii"),
                  "PT-BAT-064-names-0.txt": names, "PT-BAT-064-names-10.txt": names}
        self.assertEqual(traces, batch.LIFECYCLE_TRACES)
        self.assertIsNone(batch.validate_lifecycle_traces(traces))
        for name in traces:
            wrong = dict(traces); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_lifecycle_traces(wrong)
            wrong = dict(traces); wrong[name] = traces[name] + b"\x00"
            with self.assertRaises(ValueError): batch.validate_lifecycle_traces(wrong)
        with self.assertRaises(ValueError): batch.validate_lifecycle_traces(dict(traces, unknown=b""))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)
        for key, value in (("tests", "23"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_lifecycle_suite(wrong)

    @staticmethod
    def durable_fixture():
        cls = "dev.codex.schubert.nk.batch.file.DurableRecordFilesTest"
        names = ("literalReads", "newPublication", "sameRecordReuse", "expectedRetirement",
                 "nameContentAndNull", "metadataAndFilesystems", "boundedChannels",
                 "namespaceAndReplacement", "allReadFailures", "allWriteRetireFailures",
                 "interruptionsAndUnknownRuntime", "concurrencyAndNative")
        suite = ET.Element("testsuite", name=cls, tests="12", failures="0", errors="0", skipped="0")
        for name in names: ET.SubElement(suite, "testcase", classname=cls, name=name)
        return suite, {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(names, 46)}

    def test_durable_record_inventory_and_nonpassing_cases(self):
        suite, expected = self.durable_fixture()
        self.assertEqual(suite.get("name"), batch.DURABLE_CLASS)
        self.assertEqual(tuple(c.get("name") for c in suite), batch.DURABLE_METHODS)
        self.assertEqual(expected, batch.validate_durable_suite(suite))
        prefix = "12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\n"
        activation = "fedcba98-7654-3210-8fed-cba987654321\n"
        traces = {"PT-BAT-047-anchor.txt": ("NKRUN1\n" + prefix).encode("ascii"),
                  "PT-BAT-047-active.txt": ("NKACT1\n" + prefix + activation).encode("ascii"),
                  "PT-BAT-047-begin.txt": ("NKACT1\n" + prefix + activation).encode("ascii"),
                  "PT-BAT-047-done-10.txt": ("NKDONE1\n" + prefix + activation + "2026-09-12T05:06:07.234567Z\n10\n").encode("ascii")}
        self.assertEqual(traces, batch.DURABLE_TRACES)
        self.assertIsNone(batch.validate_durable_traces(traces))
        for name in traces:
            wrong = dict(traces); del wrong[name]
            with self.assertRaises(ValueError): batch.validate_durable_traces(wrong)
            wrong = dict(traces); wrong[name] = b"unknown"
            with self.assertRaises(ValueError): batch.validate_durable_traces(wrong)
        with self.assertRaises(ValueError): batch.validate_durable_traces(dict(traces, unknown=b""))
        for position in range(len(suite)):
            wrong = copy.deepcopy(suite); wrong.remove(wrong[position])
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)
        for tag in ("failure", "error", "skipped", "flakyFailure", "rerunFailure", "unknown"):
            wrong = copy.deepcopy(suite); ET.SubElement(wrong[0], tag)
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)
        for key, value in (("tests", "11"), ("name", "unknown"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            wrong = copy.deepcopy(suite); wrong.set(key, value)
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)
        for key, value in (("name", "unknown"), ("name", suite[1].get("name")), ("classname", "unknown")):
            wrong = copy.deepcopy(suite); wrong[0].set(key, value)
            with self.assertRaises(ValueError): batch.validate_durable_suite(wrong)

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
                 "dev.codex.schubert.nk.batch.file.DurableRecordFilesTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRunFilesTest",
                 "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest",
                 "dev.codex.schubert.nk.batch.file.MaintenanceRunRetirementTest",
                 "dev.codex.schubert.nk.batch.repository.InspectionSummaryRepositoryTest",
                 "dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest",
                 "dev.codex.schubert.nk.batch.repository.BatchStepValuesTest",
                 "dev.codex.schubert.nk.batch.repository.BatchRunRepositoryTest",
                 "dev.codex.schubert.nk.batch.repository.CleanupStepValuesTest",
                 "dev.codex.schubert.nk.batch.repository.CleanupStepRepositoryTest",
                 "dev.codex.schubert.nk.batch.cleanup.StepCleanupServiceTest",
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
        self.assertEqual(25, len(suites))
        self.assertEqual(suites[:16], batch.select_program_suites(suites))
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
        self.assertEqual("Batch module247 PT = NK-BAT-001177 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(247, 177))
        self.assertEqual("Batch module65 PT = NK-BAT-00137 + NK-OPS-00128. " + suffix,
                         batch.ownership_description(65, 37))
        self.assertEqual("Batch module91 PT = NK-BAT-00137 + NK-OPS-00154. " + suffix,
                         batch.ownership_description(91, 37))
        self.assertEqual("Batch module107 PT = NK-BAT-00137 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(107, 37))
        self.assertEqual("Batch module115 PT = NK-BAT-00145 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(115, 45))
        self.assertEqual("Batch module127 PT = NK-BAT-00157 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(127, 57))
        self.assertEqual("Batch module151 PT = NK-BAT-00181 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(151, 81))
        self.assertEqual("Batch module159 PT = NK-BAT-00189 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(159, 89))
        self.assertEqual("Batch module183 PT = NK-BAT-001113 + NK-OPS-00170. " + suffix,
                         batch.ownership_description(183, 113))
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
            {"method": "InspectorEnvironmentFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /etc and /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-NS-008", "coverageExcluded": False},
            {"method": "MaintenanceRunFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /var", "owner": "NK-BAT-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-BAT-081", "coverageExcluded": False}),
            launch.REVIEWED_STATIC_DIAGNOSTICS)
        self.assertEqual((launch.REVIEWED_STATIC_DIAGNOSTICS[2],), batch.REVIEWED_STATIC_DIAGNOSTICS)

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
        durable, expected_durable = self.durable_fixture()
        lifecycle, expected_lifecycle = self.lifecycle_fixture()
        refs, expected_refs = self.references_fixture()
        retirement_records, expected_retirement_records = self.retirement_fixture(True)
        retirement, expected_retirement = self.retirement_fixture()
        summary, expected_summary = self.parent_fixture("repository")
        attempt, expected_attempt = self.parent_fixture("attempt")
        step_values, expected_step_values = self.step_fixture()
        step_repository, expected_step_repository = self.step_fixture(True)
        reports = [suite, repository, handoff, records, durable, lifecycle, refs, retirement_records, retirement, summary, attempt, step_values, step_repository] + [self.atomic_fixture(i)[0] for i in range(3)]
        accepted = batch.validate_reports(reports)
        self.assertEqual(177, len(accepted))
        for i in range(3):
            _, atomic_expected = self.atomic_fixture(i)
            self.assertEqual(atomic_expected, {k: v for k, v in accepted.items() if k in atomic_expected})
        self.assertEqual(expected_step_values, {k: v for k, v in accepted.items() if k in expected_step_values})
        self.assertEqual(expected_step_repository, {k: v for k, v in accepted.items() if k in expected_step_repository})
        self.assertEqual(expected_summary, {k: v for k, v in accepted.items() if k in expected_summary})
        self.assertEqual(expected_attempt, {k: v for k, v in accepted.items() if k in expected_attempt})
        self.assertEqual(expected_retirement_records, {k: v for k, v in accepted.items() if k in expected_retirement_records})
        self.assertEqual(expected_retirement, {k: v for k, v in accepted.items() if k in expected_retirement})
        self.assertEqual(expected_refs, {k: v for k, v in accepted.items() if k in expected_refs})
        self.assertEqual(expected_lifecycle, {k: v for k, v in accepted.items() if k in expected_lifecycle})
        self.assertEqual(expected_durable, {k: v for k, v in accepted.items() if k in expected_durable})
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
                "inspector-process", "log-cleanup-progress", "question-query", "result-binding", "question-mutation", "inspector-database", "inspector-application", "inspector-launch")] + ["018_NK-OPS-001/evidence", "004_NK-DAT-001/evidence/backup-rerun", "004_NK-DAT-001/evidence/run-references", "004_NK-DAT-001/evidence/parent-summary", "004_NK-DAT-001/evidence/atomic-cleanup"]
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
            self.assertEqual(38, len(check()))
            outside = root / "outside.xml"
            outside.write_bytes(b"fixture")
            link = directory / "escape.xml"
            link.symlink_to(outside)
            for relative in ("", "../results.xml", str(outside), "missing.xml", "escape.xml"):
                with self.assertRaises(ValueError):
                    gate.local_file(directory, relative)

    def test_collection_stops_at_each_failure(self):
        for failed_at in range(38):
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
        self.assertEqual(38, len(calls))
        self.assertTrue(calls[0][2].endswith("/006_collect_scenario_evidence.py"))
        self.assertTrue(calls[-1][2].endswith("/026_collect_atomic_cleanup_evidence.py"))
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
