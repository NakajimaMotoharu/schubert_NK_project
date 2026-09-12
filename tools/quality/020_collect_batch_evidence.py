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
OPS_CLASSES = {"dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest",
               "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest",
               "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest",
               "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest",
               "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest"}


def select_program_suites(suites):
    # PG-D-147/148: shared module, distinct Program IDs; no unknown/missing/duplicate class.
    expected = {CLASS, LOG_CLASS, HANDOFF_CLASS, *OPS_CLASSES}
    if len(suites) != len(expected) or {s.get("name") for s in suites} != expected:
        raise ValueError("unmapped or missing shared batch module class")
    return [s for s in suites if s.get("name") not in OPS_CLASSES]


def validate_suite(suite):
    return validate_group(suite, CLASS, METHODS, 1)


def validate_log_suite(suite):
    return validate_group(suite, LOG_CLASS, LOG_METHODS, 18)


def validate_handoff_suite(suite):
    return validate_group(suite, HANDOFF_CLASS, HANDOFF_METHODS, 30)


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
    if len(suites) != 3 or {s.get("name") for s in suites} != {CLASS, LOG_CLASS, HANDOFF_CLASS}:
        raise ValueError("unmapped or missing batch test class")
    methods = {}
    for suite in suites:
        validator = {CLASS: validate_suite, LOG_CLASS: validate_log_suite, HANDOFF_CLASS: validate_handoff_suite}[suite.get("name")]
        methods.update(validator(suite))
    return methods


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0 or verified["modules"]["batch"]["tests"] != 71:
        raise SystemExit("matching verified full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-batch/target"
    reports = list((target / "surefire-reports").glob("TEST-*.xml"))
    methods = validate_reports(select_program_suites([ET.parse(report).getroot() for report in reports]))
    evidence = repo / "evidence/01_PT/017_NK-BAT-001/evidence"
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    sanitized = ET.Element("testsuite", name="NK-BAT-001", tests="37", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(sanitized, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(sanitized).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    for suffix in ("csv", "xml"):
        shutil.copyfile(target / ("site/jacoco/jacoco." + suffix), evidence / ("coverage/batch-jacoco." + suffix))
    summary = {"runId": run, "targetCommit": verified["targetCommit"], "tests": 37,
               "failed": 0, "errors": 0, "skipped": 0,
               "coverage": verified["modules"]["batch"]["coverage"],
               "staticAnalysis": verified["modules"]["batch"]["spotbugs"],
               "result": "PASS_REPOSITORY_LOG_AND_HANDOFF_BOUNDARIES_ONLY", "programComplete": False}
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-BAT-001", "scopeResult": "PASS_REPOSITORY_LOG_AND_HANDOFF_BOUNDARIES_ONLY",
        "programComplete": False, "testIdMethods": methods,
        "sharedModuleOwnership": "Batch module65 PT = NK-BAT-00137 + NK-OPS-00128. Full module coverage includes both; OPS IDs and admission/stop/run-file coverage are certified separately by022/018_NK-OPS-001. No duplicate PT credit.",
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
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (evidence / "checksums.sha256").write_text("".join(
        hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
        for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
