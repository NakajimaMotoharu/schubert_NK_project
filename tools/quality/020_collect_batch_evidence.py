#!/usr/bin/env python3
"""PG-D-137: certify only executed batch repository PT; no process/backup completion claim."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

METHODS = (
    "runIdentityBoundaries", "countInvariants", "cleanupAllowlist", "rejectionAndProgressContracts",
    "emptyCleanupAndExplicitTransaction", "heldLogsAndDurableRead", "rollbackSavepointAndResume",
    "backupAndAdvisoryRejection", "exactLimitsAndNullInputs", "rowProjectionFailures",
    "progressProjectionFailures", "jdbcFailuresRemainRedacted", "roleIsolationAndNoInboxBypass",
    "timezoneAndCutoffIdentity", "lockedLogsDoNotAdvance", "retentionAndResourceOwnership",
    "moduleDependencyBoundary",
)
CLASS = "dev.codex.schubert.nk.batch.repository.CleanupRepositoryTest"
REFERENCES_CLASS = "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryTest"
REFERENCES_METHODS = ("referenceValueInvariants", "realReferenceRead", "transactionAndLockContracts",
                      "projectionAndNullContracts", "jdbcFailureMatrix", "interruptionAndRuntime",
                      "rollbackAndFreshVisibility", "independentConcurrentConnections")
LOG_METHODS = (
    "emptyAndCompletedRuns", "heldPrefixAndLargeChunks", "resumedAttemptCounts", "sessionLockOwnership",
    "backupAndRowLockStop", "timeBoundaryAndClockWrap", "interruptsRemainSet", "rollbackAndUncertainCommit",
    "restorationAndUnlockFailures", "invalidInputsAndProjections", "summaryInvariants", "failuresLeaveNoFalseSuccess",
)
LOG_CLASS = "dev.codex.schubert.nk.batch.cleanup.LogCleanupServiceTest"
HANDOFF_CLASS = "dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoffTest"
HANDOFF_METHODS = ("actualTransactionHandoff", "preconditionsAndReentrantLock", "callbackFailuresAndNull",
                   "reacquisitionConflict", "jdbcFailureMatrix", "invalidResultMatrix",
                   "stateChangesAndInterrupts", "concurrentGapCompetition")
DURABLE_CLASS = "dev.codex.schubert.nk.batch.file.DurableRecordFilesTest"
LIFECYCLE_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRunFilesTest"
LIFECYCLE_METHODS = ("newRunPublication", "resumeActive", "resumeOrphanAnchor", "resumePendingBegin",
                     "resumeCompletedHistory", "completedActiveRecovery", "completeSuccessAndWarning",
                     "completionRetryAndMismatch", "noImplicitNewIdentity", "malformedGraphReferences",
                     "ambiguousPendingStates", "inventoryUnknownAndPartial", "namespacePermissions",
                     "namespaceReplacement", "recordReplacementDuringScan", "listingAndIoFailures",
                     "rootAcquisitionAndCloseFailures", "startCrashBoundaries", "resumeCrashBoundaries",
                     "completionCrashBoundaries", "nullAndClosedContracts", "interruptionAndRuntime",
                     "concurrentScopeOwnership", "fixedFactoryAndReopen")
RETIREMENT_RECORD_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest"
RETIREMENT_RECORD_METHODS = ("literalMarkerAndPlanHash", "temporalAndCountInvariants", "nullAndOwnership", "malformedMarkerBytes", "markerAliases", "boundedStorageRecords", "planNameBinding", "concurrentCanonicalRecords")
RETIREMENT_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRunRetirementTest"
RETIREMENT_METHODS = ("candidatesAndProtectedRuns", "strictAgeAndLatestCompletion", "referenceCombinations", "missingAndContradictoryIdentity", "newRetirementPreservesOtherRuns", "preMarkerPlanRecovery", "markerOriginalRecovery", "metadataOnlyRecovery", "planCompletenessAndDigest", "namespaceAndForeignArtifacts", "referenceReappearanceAndDbFaults", "publicationAndDeletionCrashes", "everyIoFailurePreservesState", "scopeNullAndInterruption", "concurrentAndClosedScope", "resourceCloseAndDigestFailure")
REVIEWED_STATIC_DIAGNOSTICS = (
    {"method": "MaintenanceRunFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /var", "owner": "NK-BAT-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-BAT-081", "coverageExcluded": False},)
DURABLE_METHODS = ("literalReads", "newPublication", "sameRecordReuse", "expectedRetirement",
                   "nameContentAndNull", "metadataAndFilesystems", "boundedChannels",
                   "namespaceAndReplacement", "allReadFailures", "allWriteRetireFailures",
                   "interruptionsAndUnknownRuntime", "concurrencyAndNative")
RECORD_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest"
RECORD_METHODS = ("literalRecords", "identityTemporalBoundaries", "malformedSources", "scalarAliases",
                  "completionInvariants", "nullContracts", "ownershipAndRedaction", "concurrentUse")
RECORD_TRACES = {
    "PT-BAT-038-anchor.txt": b"NKRUN1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\n",
    "PT-BAT-038-activation.txt": b"NKACT1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\nfedcba98-7654-3210-8fed-cba987654321\n",
    "PT-BAT-038-completion-0.txt": b"NKDONE1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\nfedcba98-7654-3210-8fed-cba987654321\n2026-09-12T05:06:07.234567Z\n0\n",
    "PT-BAT-038-completion-10.txt": b"NKDONE1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\nfedcba98-7654-3210-8fed-cba987654321\n2026-09-12T05:06:07.234567Z\n10\n"}
OPS_CLASSES = {"dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest",
               "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest",
               "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest",
               "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest",
               "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest",
               "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest",
               "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest",
               "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest",
               "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest"}
DURABLE_TRACES = {
    "PT-BAT-047-anchor.txt": RECORD_TRACES["PT-BAT-038-anchor.txt"],
    "PT-BAT-047-active.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-047-begin.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-047-done-10.txt": RECORD_TRACES["PT-BAT-038-completion-10.txt"]}
LIFECYCLE_NAMES = (b"attempts/fedcba98-7654-3210-8fed-cba987654321.begin\n"
                   b"attempts/fedcba98-7654-3210-8fed-cba987654321.done\n"
                   b"runs/12345678-9abc-def0-8123-456789abcdef.run\n")
LIFECYCLE_TRACES = {
    "PT-BAT-058-anchor.txt": RECORD_TRACES["PT-BAT-038-anchor.txt"],
    "PT-BAT-058-begin.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-058-active.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-064-done-0.txt": RECORD_TRACES["PT-BAT-038-completion-0.txt"],
    "PT-BAT-064-done-10.txt": RECORD_TRACES["PT-BAT-038-completion-10.txt"],
    "PT-BAT-064-names-0.txt": LIFECYCLE_NAMES,
    "PT-BAT-064-names-10.txt": LIFECYCLE_NAMES}


RETIREMENT_TRACES = {
    "PT-BAT-090-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
    "PT-BAT-090-maximum.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n2147483647\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
    "PT-BAT-099-two-activation-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-03T00:00:00.000000Z\n2026-02-07T00:00:00.000001Z\n2\ne6ff18dc21a10852fe4de7e8606fe0ad005c8e242bdc535ea8d391dd052528de\n",
    "PT-BAT-102-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
    "PT-BAT-102-phases.txt": b"phase0:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase1:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase2:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase3:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase4:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase5:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nphase6:\n12345678-9abc-def0-8123-456789abcdef.retire\nphase7:\n",
}


def validate_retirement_traces(traces):
    if traces != RETIREMENT_TRACES:
        raise ValueError("missing, extra or invalid independent retirement trace")


def select_program_suites(suites):
    # PG-D-147/148: shared module, distinct Program IDs; no unknown/missing/duplicate class.
    expected = {CLASS, LOG_CLASS, HANDOFF_CLASS, RECORD_CLASS, DURABLE_CLASS, LIFECYCLE_CLASS, REFERENCES_CLASS,
                RETIREMENT_RECORD_CLASS, RETIREMENT_CLASS, *OPS_CLASSES}
    if len(suites) != len(expected) or {s.get("name") for s in suites} != expected:
        raise ValueError("unmapped or missing shared batch module class")
    return [s for s in suites if s.get("name") not in OPS_CLASSES]


def validate_suite(suite):
    return validate_group(suite, CLASS, METHODS, 1)


def validate_log_suite(suite):
    return validate_group(suite, LOG_CLASS, LOG_METHODS, 18)


def validate_handoff_suite(suite):
    return validate_group(suite, HANDOFF_CLASS, HANDOFF_METHODS, 30)


def validate_record_suite(suite):
    return validate_group(suite, RECORD_CLASS, RECORD_METHODS, 38)


def validate_durable_suite(suite):
    return validate_group(suite, DURABLE_CLASS, DURABLE_METHODS, 46)


def validate_lifecycle_suite(suite):
    return validate_group(suite, LIFECYCLE_CLASS, LIFECYCLE_METHODS, 58)


def validate_references_suite(suite):
    return validate_group(suite, REFERENCES_CLASS, REFERENCES_METHODS, 82)


def validate_retirement_record_suite(suite):
    return validate_group(suite, RETIREMENT_RECORD_CLASS, RETIREMENT_RECORD_METHODS, 90)


def validate_retirement_suite(suite):
    return validate_group(suite, RETIREMENT_CLASS, RETIREMENT_METHODS, 98)


def validate_record_traces(traces):
    if traces != RECORD_TRACES:
        raise ValueError("missing, extra or invalid independently checked run record trace")


def validate_durable_traces(traces):
    if traces != DURABLE_TRACES:
        raise ValueError("missing, extra or invalid independently checked durable record trace")


def validate_lifecycle_traces(traces):
    if traces != LIFECYCLE_TRACES:
        raise ValueError("missing, extra or invalid independently checked lifecycle trace")


def validate_group(suite, cls, expected, start):
    cases = suite.findall("testcase")
    names = [c.get("name") for c in cases]
    if (suite.get("name") != cls or suite.get("tests") != str(len(expected))
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or len(names) != len(set(names)) or set(names) != set(expected)
            or any(c.get("classname") != cls or
                   any(child.tag not in ("system-out", "system-err") for child in c) for c in cases)):
        raise ValueError("batch PT inventory or execution is not certifiable")
    return {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(expected, start)}


def validate_reports(suites):
    validators = {CLASS: validate_suite, LOG_CLASS: validate_log_suite,
                  HANDOFF_CLASS: validate_handoff_suite, RECORD_CLASS: validate_record_suite,
                  DURABLE_CLASS: validate_durable_suite, LIFECYCLE_CLASS: validate_lifecycle_suite,
                  REFERENCES_CLASS: validate_references_suite,
                  RETIREMENT_RECORD_CLASS: validate_retirement_record_suite,
                  RETIREMENT_CLASS: validate_retirement_suite}
    if len(suites) != len(validators) or {s.get("name") for s in suites} != set(validators):
        raise ValueError("unmapped or missing batch test class")
    methods = {}
    for suite in suites:
        validator = validators[suite.get("name")]
        methods.update(validator(suite))
    return methods


def ownership_description(total, program):
    # BUG-153/YKT-119: observed totals have one source; this is reporting, not the PT oracle.
    return (f"Batch module{total} PT = NK-BAT-001{program} + NK-OPS-001{total - program}. "
            "Full module coverage includes both; OPS IDs are certified separately by022/018_NK-OPS-001. "
            "No duplicate PT credit.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0 or verified["modules"]["batch"]["tests"] != 183:
        raise SystemExit("matching verified full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-batch/target"
    reports = list((target / "surefire-reports").glob("TEST-*.xml"))
    methods = validate_reports(select_program_suites([ET.parse(report).getroot() for report in reports]))
    evidence = repo / "evidence/01_PT/017_NK-BAT-001/evidence"
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    trace_root = target / "maintenance-record-traces"
    traces = {str(p.relative_to(trace_root)): p.read_bytes() for p in trace_root.rglob("*") if p.is_file()}
    validate_record_traces(traces)
    durable_root = target / "durable-record-traces"
    durable_traces = {str(p.relative_to(durable_root)): p.read_bytes()
                      for p in durable_root.rglob("*") if p.is_file()}
    validate_durable_traces(durable_traces)
    lifecycle_root = target / "run-lifecycle-traces"
    lifecycle_traces = {str(p.relative_to(lifecycle_root)): p.read_bytes()
                        for p in lifecycle_root.rglob("*") if p.is_file()}
    validate_lifecycle_traces(lifecycle_traces)
    retirement_root = target / "run-retirement-traces"
    retirement_traces = {str(p.relative_to(retirement_root)): p.read_bytes()
                         for p in retirement_root.rglob("*") if p.is_file()}
    validate_retirement_traces(retirement_traces)
    for folder, values in (("input/run-retirement", RETIREMENT_TRACES), ("output/run-retirement", retirement_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for folder, values in (("input/run-lifecycle", LIFECYCLE_TRACES), ("output/run-lifecycle", lifecycle_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for folder, values in (("input/durable-records", DURABLE_TRACES), ("output/durable-records", durable_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for folder, values in (("input/maintenance-records", RECORD_TRACES), ("output/maintenance-records", traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    sanitized = ET.Element("testsuite", name="NK-BAT-001", tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(sanitized, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(sanitized).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    for suffix in ("csv", "xml"):
        shutil.copyfile(target / ("site/jacoco/jacoco." + suffix), evidence / ("coverage/batch-jacoco." + suffix))
    summary = {"runId": run, "targetCommit": verified["targetCommit"], "tests": len(methods),
               "failed": 0, "errors": 0, "skipped": 0,
               "coverage": verified["modules"]["batch"]["coverage"],
               "staticAnalysis": verified["modules"]["batch"]["spotbugs"],
               "result": "PASS_REPOSITORY_LOG_HANDOFF_RECORDS_AND_RUN_RETIREMENT_ONLY", "programComplete": False}
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-BAT-001", "scopeResult": "PASS_REPOSITORY_LOG_HANDOFF_RECORDS_AND_RUN_RETIREMENT_ONLY",
        "programComplete": False, "testIdMethods": methods,
        "sharedModuleOwnership": ownership_description(verified["modules"]["batch"]["tests"], len(methods)),
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": hashlib.sha256(full.read_bytes()).hexdigest(),
        "related": ["PG-D-137", "PG-D-138", "SSC-051", "BUG-104", "YKT-092", "BUG-109", "BUG-110", "BUG-111", "YKT-096", "YKT-097", "BUG-112", "YKT-098", "BUG-014", "YKT-012", "BUG-145", "YKT-113"],
        "fixture": "Isolated PostgreSQL18 with real Flyway and five denied roles; literal public log rows, fixed UUID/time, explicit parent transactions and public JDBC fault probes. No deployed credentials or data.",
        "oracle": "001/PT-BAT-001..017: independent8 function names/limits and3 reasons; held2+eligible1 gives2/0/2 then1/1/0 thenEND, run cumulative3/1/2; rollback/savepoint/reconnect/lock do not lose or duplicate counts; UTC/JST/NewYork epoch1789603200 and90day microsecond boundary; no parent connection commit/rollback/close/config mutation; all typed-null/row-count/SQL-stage failures reject; dependency allowlist.",
        "logServiceOracle": "003/PT018..029: held10000 then eligible1 yields three committed chunks and cumulative10001/1/10000; resume initial2/0/2 yields attempt1/1/0; derive initial cumulative by first committed cumulative minus its same-TX chunk; parent reentrant session lock retained, own acquisition released; first/late backup and row locks stop;30min/interrupt/wrap; rollback failure never enables implicit commit; unknown commit/recovery, every JDBC and resource failure, invalid counts/continuity reject before commit; only complete committed/restored/unlocked summary returns0/10.",
        "limitations": "No OS flock, actual backup verification, dedicated main, unit, whole-morning orchestrator, or IT/ST certificate. Repository observations require caller commit; LogCleanupService owns chunk transactions but borrows the parent connection.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in sorted((repo / "src/schubert-nk-batch").glob("src/**/*.java"))],
    })
    manifest["logServiceOracle"] += " BUG145/YKT113: BAT026 crosses real foreign-connection lock contention with result/statement/both close faults, and TIME_LIMIT/INTERRUPTED/BACKUP_GATE with both unlock close faults. All typed failures have zero cause/suppressed after closure; primary reason, interruption and caller connection ownership are preserved; no deletion on lock rejection."
    manifest["related"] += ["PG-D-150", "SSC-049", "BUG-146", "YKT-114"]
    manifest["handoffOracle"] = "005/PT-BAT-030..037: parent single session lock -> child dedicated-role transaction lock -> parent nonblocking reacquire; repeated handoff preserves exact one acquisition. Missing/shared/two-int/reentrant/state/interrupt/null reject, every observed JDBC occurrence and each of5 scalar missing/duplicate/null/flipped/null-resource faults reject, resources close and provider diagnostics stay absent. Child IOException fixed, unexpected Runtime/Error identity preserved, null result never succeeds. A competing real connection/thread in the gap prevents parent success without waiting/force unlock."
    manifest["limitations"] += " InspectorLockHandoff only supplies the borrowed-connection synchronous handoff boundary. Caller must retain OS lock, admit backup/stopped applications/run, confirm child process termination before callback return, avoid sharing parent connection, verify receipts/progress, and dispose parent connection after failure. Actual oneshot and OS/backup orchestration remain unverified."
    manifest["related"] += ["PG-D-156", "SSC-055"]
    manifest["recordOracle"] = "007/PT-BAT-038..045: hand-written ASCII anchor72/activation109/done140 or141 bytes; nil/max UUID, UTC0001/9999 and microseconds, Asia/Tokyo civil date boundaries,0/10 only. Each fixed magic/delimiter byte mutated to all other byte values; aliases, leap normalization, scalar errors, malformed/null and wrong model reject. Valid different identity remains different data, not authentication. Completion invariants, caller-owned arrays, redacted values and64 independent activations use literal field/byte oracles."
    manifest["related"] += ["PG-D-157"]
    manifest["durableRecordOracle"] = "009/PT-BAT-046..057: independent literal records and real private inode/no-replace/fsync with synthetic root admission. Borrowed-root canonical name-to-content binding; bounded read, same-content reuse only, expected-inode retirement, every independently counted native/IO occurrence fails closed and releases owned resources; namespace replacement, metadata/ACL/filesystem, null, invalid IO, interruption and concurrency. No partial-file overwrite or automatic cleanup."
    manifest["related"] += ["PG-D-158", "BUG-159", "BUG-160", "BUG-161", "BUG-162", "YKT-124", "YKT-125", "YKT-126"]
    manifest["lifecycleOracle"] = "011/PT-BAT-058..081: fixed six-root namespace and scope-bound session, complete unfiltered canonical inventory, original-inode snapshots through whole-graph scan, anchor/begin/done/active consistency and unique pending run. Literal start/resume/complete and crash states, no new cutoff on resume, immutable prior completion, same-byte recovery force/directory sync and absent retirement re-sync, independently counted native/IO fault locations, null/closed/interrupt/runtime and concurrency. Root admission is synthetic over actual local inodes; parent OS lock and legacy DB uniqueness are caller obligations."
    manifest["reviewedStaticDiagnostics"] = list(REVIEWED_STATIC_DIAGNOSTICS)
    manifest["related"] += ["PG-D-159", "BUG-163", "BUG-164", "BUG-165", "BUG-166", "YKT-127"]
    manifest["runReferencesOracle"] = "013/BAT082..089: immutable4boolean/3flag OR/inconsistent-empty rejection; realPG reads and fixed UUID/cutoff; explicit read-write READ COMMITTED, own DB advisory required; all16 independently counted JDBC calls including all4 NULL columns and both close failures, missing/duplicate/null resource reject after closure. Initial/final interrupt retained, unknown runtime/NPE not normal, connection ownership/config untouched, fresh rollback and separate-owner concurrent connections. Observation alone never authorizes GC or substitutes for parent lock continuity."
    manifest["related"] += ["PG-D-160", "SSC-056", "PG-D-161", "BUG-171", "BUG-172", "YKT-132", "YKT-133"]
    manifest["retirementOracle"] = "015/BAT090..113: literal NKRET1 195..204 bytes and independent one/two-activation SHA256 vectors; full canonical plan count/hash retained through original done/begin/anchor deletion, original-directory durability barriers BEFORE any plan/marker disposal, metadata-only recovery, strict latest-completion400day age, actual PG18 V018 three-reference combinations/identity/query failures, target-only active/pending protection and other-run preservation. Full namespace/graph, bounded record ownership, every native IO occurrence, crash/close/null/interruption/concurrency, no unknown part repair or recursive deletion."
    manifest["limitations"] += " The file scope establishes fixed-namespace, record lifecycle and limited400day retirement under caller exclusion, not actual OS-lock continuity, parent/child lifecycle or whole-morning orchestration. No actual reboot or root deployment."
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (evidence / "checksums.sha256").write_text("".join(
        hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
        for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
