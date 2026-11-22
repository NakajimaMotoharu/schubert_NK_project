#!/usr/bin/env python3
"""Certify Scenario PT using allowlisted metadata; reject failed, skipped, flaky and partial coverage."""

import argparse
from collections import defaultdict
import hashlib
import json
import platform
import re
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_reactor_junit import MODULE_DIRECTORIES, verify_reactor_junit
from pgpt_evidence_destination import evidence_output_root


def scenario_storage_suite(name):
    # PG-D-146: shared module is not shared Program ownership. OPS IDs live in collector022.
    return ".nk.storage." in name and name not in {
        "dev.codex.schubert.nk.storage.LinuxFileLockTest",
        "dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest",
        "dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest",
        "dev.codex.schubert.nk.storage.PrivateChildDirectoryTest",
        "dev.codex.schubert.nk.storage.ResourceScopeTest"}


REQUIRED_COVERAGE = frozenset(("LINE", "METHOD", "CLASS", "BRANCH"))
JACOCO_COUNTERS = REQUIRED_COVERAGE | {"INSTRUCTION", "COMPLEXITY"}


def _coverage_rows(element):
    counters = {}
    for counter in element.findall("counter"):
        metric = counter.get("type")
        missed = counter.get("missed", "")
        covered = counter.get("covered", "")
        if (
            metric not in JACOCO_COUNTERS
            or metric in counters
            or not re.fullmatch(r"[0-9]+", missed)
            or not re.fullmatch(r"[0-9]+", covered)
        ):
            raise ValueError("invalid or duplicated JaCoCo counter")
        counters[metric] = {"missed": int(missed), "covered": int(covered)}
    return counters


def validate_module_coverage(report):
    """Require four nonempty module counters with matching package totals."""
    root = _coverage_rows(report)
    packages = report.findall("package")
    names = [package.get("name") for package in packages]
    if (
        report.tag != "report"
        or not packages
        or None in names
        or len(names) != len(set(names))
        or not REQUIRED_COVERAGE <= root.keys()
        or any(root[metric]["covered"] == 0 for metric in REQUIRED_COVERAGE)
        or any(values["missed"] for values in root.values())
    ):
        raise ValueError("incomplete or nonpassing module JaCoCo report")
    totals = defaultdict(lambda: {"missed": 0, "covered": 0})
    for package in packages:
        for metric, values in _coverage_rows(package).items():
            totals[metric]["missed"] += values["missed"]
            totals[metric]["covered"] += values["covered"]
    if root != totals:
        raise ValueError("module JaCoCo counters disagree with package totals")
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    run = args.run_id
    if not run.startswith(("PT-SCN-", "PT-MED-", "PT-ADM-", "PT-WEB-")) or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    evidence = evidence_output_root(repo) / "008_NK-SCN-001/evidence"
    read = lambda suffix: (Path("/tmp") / (run + suffix)).read_text().strip()
    if read(".exit") != "0":
        raise SystemExit("failed execution cannot be certified")
    commit = read(".commit")
    subprocess.run(["git", "diff", "--exit-code", commit, "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    report_receipt = verify_reactor_junit(repo, run, commit)
    raw = (Path("/tmp") / (run + ".log")).read_bytes()
    if b"BUILD SUCCESS" not in raw or b"[ERROR]" in raw:
        raise SystemExit("build log is not successful")
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    modules, methods, regressions = {}, [], []
    current_reports = set()
    for module, directory in MODULE_DIRECTORIES:
        target = repo / directory / "target"
        reports = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        if not reports:
            raise SystemExit("missing JUnit reports")
        count = 0
        for report in reports:
            suite = ET.parse(report).getroot()
            cases = suite.findall("testcase")
            if (any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped"))
                    or len(cases) != int(suite.get("tests"))):
                raise SystemExit("nonpassing or inconsistent JUnit report")
            for case in cases:
                if any(child.tag not in ("system-out", "system-err") for child in case):
                    raise SystemExit("failure/rerun/flaky/skipped test is not certifiable")
            count += len(cases)
            scenario = (".api.persistence.Scenario" in suite.get("name", "")
                        or ".api.security.AuthenticationContextVerifierTest" in suite.get("name", "")
                        or ".api.idempotency.JdbcInboxCoordinatorTest" in suite.get("name", "")
                        or ".api.idempotency.BoundInboxExecutionTest" in suite.get("name", "")
                        or ".api.idempotency.JdbcScenarioSnapshotReplacementTest" in suite.get("name", "")
                        or ".api.application.scenario." in suite.get("name", "")
                        or ".api.storage." in suite.get("name", "")
                        or scenario_storage_suite(suite.get("name", ""))
                        or ".web.storage." in suite.get("name", "")
                        or ".protocol.codec.ScenarioRecordEncodingTest" in suite.get("name", ""))
            selected = cases if scenario else [c for c in cases if c.get("name", "").startswith("bug036")]
            if selected:
                current_reports.add(report.name)
                clean = ET.Element("testsuite", {k: suite.get(k) for k in
                                                ("name", "time", "tests", "errors", "failures", "skipped")})
                clean.set("tests", str(len(selected)))
                clean.set("time", str(sum(float(c.get("time", "0")) for c in selected)))
                for case in selected:
                    attrs = {k: case.get(k) for k in ("name", "classname", "time")}
                    ET.SubElement(clean, "testcase", attrs)
                    (methods if scenario else regressions).append(attrs["classname"] + "#" + attrs["name"])
                ET.indent(clean)
                ET.ElementTree(clean).write(evidence / "output" / report.name,
                                            encoding="UTF-8", xml_declaration=True)
        jacoco = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
        counters = validate_module_coverage(jacoco)
        shutil.copyfile(target / "site/jacoco/jacoco.csv", evidence / "coverage" / (module + "-jacoco.csv"))
        static = "not configured for characterization runner"
        if module != "characterization":
            spot = ET.parse(target / "spotbugsXml.xml").getroot()
            errors = spot.find("Errors")
            if spot.findall("BugInstance") or errors is None or int(errors.get("errors", "0")):
                raise SystemExit("static analysis not clean")
            static = {"tool": "SpotBugs 4.10.4.0", "violations": 0, "errors": 0}
        modules[module] = {"tests": count, "coverage": counters, "spotbugs": static}
    if not methods:
        raise SystemExit("missing Scenario tests")
    if len(regressions) != 3 or not any("#bug036" in m for m in methods):
        raise SystemExit("missing cross-program monitor regression")
    # Preserve historical package names, but do not mix them into current output.
    for report in sorted((evidence / "output").glob("TEST-*.xml")):
        if report.name not in current_reports:
            archive = evidence / "logs" / (run + "-superseded-junit")
            archive.mkdir(exist_ok=True)
            destination = archive / report.name
            if destination.exists():
                raise SystemExit("refusing to overwrite archived JUnit evidence")
            report.rename(destination)
    required_methods = {
        "PT-SCN-008-A07": "dev.codex.schubert.nk.storage.StorageRootInspectionTest#a07AcceptsSixExistingRootsAndRejectsUnsafeExistingRoots",
        "PT-SCN-008-A07-M": "dev.codex.schubert.nk.storage.StorageRootInspectionTest#a07MetadataAndProviderNegativeMatrix",
        "PT-SCN-008-A08": "dev.codex.schubert.nk.storage.StorageRootInspectionTest#a08DeviceAndInodeBothDefinePhysicalRootIdentity",
        "PT-IDEM-B01": "dev.codex.schubert.nk.api.idempotency.BoundInboxExecutionTest#boundFirstMessageAndOperationTokenKeepOriginalAadIdentity",
        "PT-IDEM-B02": "dev.codex.schubert.nk.api.idempotency.BoundInboxExecutionTest#boundNullCorruptIdentityAndSqlFaultsNeverProduceReplay",
        "PT-IDEM-B03": "dev.codex.schubert.nk.api.idempotency.BoundInboxExecutionTest#boundConcurrentInsertRecoveryAndProcessingUseStoredMessage",
        "PT-IDEM-B04": "dev.codex.schubert.nk.api.idempotency.BoundInboxExecutionTest#boundCompatibilityPreservesReadOnlyAndSnapshotReplacement",
        "PT-SCN-009-T01": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#sixRequestsCommitFrozenResponsesAndReplayWithFreshHeaders",
        "PT-SCN-009-T02": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#detailBoundariesReleaseDatabaseBeforeFilesAndPreserveOriginalContent",
        "PT-SCN-009-T03": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#replayRegeneratesOnlyMissingOriginalFilesAndPreservesLifetime",
        "PT-SCN-009-T04": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#oneHundredSameMessagesGenerateOnceAndFinalAuthenticationWins",
        "PT-SCN-009-T05": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#failuresAtEveryTransactionFileClockAndIdentityBoundaryNeverClaimSuccess",
        "PT-SCN-009-T06": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#brokerSendAndAckFailuresReplayOneCommittedResult(Path)",
        "PT-SCN-009-T07": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#realWriterInspectorAndDatabaseRegenerationShareExactFrozenBytes(Path)",
        "PT-SCN-009-T08": "dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationServiceTest#productionAssemblyUsesRealQueryInboxAndNullContract",
        "PT-SCN-008-P04": "dev.codex.schubert.nk.api.storage.TransferStoragePreparationTest#p04ProbePrecedesCompleteScanAndPublisherUsesScannedQuota",
        "PT-SCN-008-P05": "dev.codex.schubert.nk.api.storage.TransferStoragePreparationTest#p05InvalidRootAndIncompleteScanNeverYieldPreparedCapabilities",
        "PT-IDEM-SR01": "dev.codex.schubert.nk.api.idempotency.JdbcScenarioSnapshotReplacementTest#replacementCommitsOnlyCiphertextAndKeyWithoutExtendingLifetime",
        "PT-IDEM-SR02": "dev.codex.schubert.nk.api.idempotency.JdbcScenarioSnapshotReplacementTest#invalidMetadataIdentityAndStoredStateRejectBeforeReplacement",
        "PT-IDEM-SR03": "dev.codex.schubert.nk.api.idempotency.JdbcScenarioSnapshotReplacementTest#nullTransactionAndJdbcFaultsPreserveOwnershipAndClearBindings",
        "PT-SCN-009-G01": "dev.codex.schubert.nk.api.application.scenario.ScenarioMessageGuardTest#sameMessageAndHashCollisionSerializeButNeverShareResults",
        "PT-SCN-009-G02": "dev.codex.schubert.nk.api.application.scenario.ScenarioMessageGuardTest#differentStripesRunTogetherAndCallerMonitorDoesNotBlock",
        "PT-SCN-009-G03": "dev.codex.schubert.nk.api.application.scenario.ScenarioMessageGuardTest#interruptAndCallbackFailuresReleaseOnlyOwnedLocks",
        "PT-SCN-009-F01": "dev.codex.schubert.nk.api.application.scenario.ScenarioFileRegeneratorTest#originalContentRegeneratesAtAllFileBoundaries",
        "PT-SCN-009-F02": "dev.codex.schubert.nk.api.application.scenario.ScenarioFileRegeneratorTest#changedMasterAndUnexpectedPublishedContentAreRejected",
        "PT-SCN-009-F03": "dev.codex.schubert.nk.api.application.scenario.ScenarioFileRegeneratorTest#nullErrorsAndProviderFailuresPreserveBoundaries",
        "PT-SCN-009-V01": "dev.codex.schubert.nk.api.storage.ScenarioReadyFileInspectorTest#realReadyFilesMissingNamesAndConcurrentReadsStayReadOnly",
        "PT-SCN-009-V02": "dev.codex.schubert.nk.api.storage.ScenarioReadyFileInspectorTest#presentButInvalidFilesAreNeverDeclaredMissing",
        "PT-SCN-009-V03": "dev.codex.schubert.nk.api.storage.ScenarioReadyFileInspectorTest#nullNativeCallbackAndCloseFailuresNeverBecomeAbsence",
        "PT-SCN-009-S06": "dev.codex.schubert.nk.api.application.scenario.ScenarioReplayServiceTest#regeneratedDescriptorKeepsOriginalHeaderResultAndCompletionTime",
    }
    if not set(required_methods.values()).issubset(set(methods)):
        raise SystemExit("missing required Scenario lifecycle Test ID/method evidence")
    manifest = {
        "runId": run, "programId": "NK-SCN-001", "targetCommit": commit,
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        "startedAt": read(".started"), "completedAt": read(".completed"), "exitCode": 0,
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress clean verify",
        "environment": {"os": platform.platform(), "jdk": "25.0.4", "maven": "3.9.12",
                        "postgresql": "18.6", "artemis": "2.56.0", "node": "24.19.0",
                        "libc": subprocess.check_output(["getconf", "GNU_LIBC_VERSION"], text=True).strip(),
                        "nativeAccess": "Storage/API/Web test JVM: ALL-UNNAMED; public Java25 FFM; SSC-019/021"},
        "modules": modules, "scenarioMethods": methods, "testIdMethods": required_methods, "crossProgramRegressionMethods": regressions,
        "testIdsPartial": ["PT-SCN-001", "PT-SCN-002", "PT-SCN-003", "PT-SCN-004",
                           "PT-SCN-005", "PT-SCN-006", "PT-SCN-007", "PT-SCN-008", "PT-SCN-008-F04", "PT-SCN-009"],
        "additionalTestsPassed": ["PT-SCN-008-D01", "PT-SCN-008-D02", "PT-SCN-008-D03", "PT-SCN-008-D04",
                                  "PT-SCN-008-F01", "PT-SCN-008-F02-CORE", "PT-SCN-008-F03",
                                  "PT-SCN-008-A01", "PT-SCN-008-A02", "PT-SCN-008-A03", "PT-SCN-008-A04",
                                  "PT-SCN-008-A05", "PT-SCN-008-A06",
                                  "PT-SCN-008-R01", "PT-SCN-008-R02", "PT-SCN-008-R03",
                                  "PT-SCN-008-C01", "PT-SCN-008-C02", "PT-SCN-008-C03",
                                  "PT-SCN-008-W01", "PT-SCN-008-W02", "PT-SCN-008-W03",
                                  "PT-SCN-008-W04", "PT-SCN-008-W05", "PT-SCN-008-W06",
                                  "PT-SCN-008-W07", "PT-SCN-008-W08", "PT-SCN-008-W09", "PT-SCN-008-W10",
                                  "PT-SCN-008-LIB01", "PT-SCN-008-RD01", "PT-SCN-008-RD02",
                                  "PT-SCN-008-RD03", "PT-SCN-008-RD04", "PT-SCN-008-RD05",
                                  "PT-SCN-008-U01", "PT-SCN-008-U02", "PT-SCN-008-U03",
                                  "PT-SCN-008-P01", "PT-SCN-008-P02", "PT-SCN-008-P03", "PT-SCN-008-P04", "PT-SCN-008-P05",
                                  "PT-AUT-007-R01", "PT-AUT-007-R02", "PT-AUT-007-R03", "PT-AUT-007-R04",
                                  "PT-IDEM-RO01", "PT-IDEM-RO02", "PT-IDEM-RO03", "PT-IDEM-RO04",
                                  "PT-IDEM-SR01", "PT-IDEM-SR02", "PT-IDEM-SR03",
                                  "PT-IDEM-B01", "PT-IDEM-B02", "PT-IDEM-B03", "PT-IDEM-B04",
                                  "PT-SCN-009-T01", "PT-SCN-009-T02", "PT-SCN-009-T03", "PT-SCN-009-T04", "PT-SCN-009-T05", "PT-SCN-009-T06", "PT-SCN-009-T07", "PT-SCN-009-T08",
                                  "PT-SCN-009-Q01", "PT-SCN-009-Q02", "PT-SCN-009-Q03", "PT-SCN-009-Q04",
                                  "PT-SCN-009-S01", "PT-SCN-009-S02", "PT-SCN-009-S03", "PT-SCN-009-S04", "PT-SCN-009-S05", "PT-SCN-009-S06",
                                  "PT-SCN-009-G01", "PT-SCN-009-G02", "PT-SCN-009-G03",
                                  "PT-SCN-009-F01", "PT-SCN-009-F02", "PT-SCN-009-F03",
                                  "PT-SCN-009-V01", "PT-SCN-009-V02", "PT-SCN-009-V03"],
        "testIdsNotRun": ["PT-SCN-008-F02-ADMIT-ROOT", "PT-SCN-008-F04-READINESS"],
        "programStatus": "IN_PROGRESS", "notRunCountedAsPass": 0,
        "relatedSsc": ["SSC-017", "SSC-018", "SSC-019", "SSC-020", "SSC-021", "SSC-022", "SSC-023", "SSC-024", "SSC-025", "SSC-026", "SSC-027"], "relatedBug": ["BUG-030", "BUG-031", "BUG-032", "BUG-033", "BUG-035", "BUG-036", "BUG-037", "BUG-038", "BUG-039", "BUG-041"],
        "relatedYkt": ["YKT-027", "YKT-028", "YKT-029", "YKT-031", "YKT-032", "YKT-033", "YKT-034", "YKT-035"],
        "baseline": "Current baseline unchanged; Scenario application CHR not run yet",
        "rawLogSha256": hashlib.sha256(raw).hexdigest(),
        "redaction": "Only class/method names, versions, counters and fixed metadata; all properties/stdout/stderr omitted.",
        "expectations": "008 PT specification: UI234 independent byte offsets and literal route maps, synthetic SQL fixtures and independently enumerated entry IDs/order/filter/page outcomes. Native storage uses literal bytes and actual filesystem postconditions: one of 100 publishers wins without replacing existing bytes; retained FDs survive path replacement and are all closed. Production is not used to generate expected values.",
        "scope": "Queries/detail, shared retained directory/inode capabilities, root metadata and lexical layout checks, atomic quota and inline/file projection. Internal writer creates, initializes, streams, verifies and publishes real files with collision, cleanup and retained-quota fault tests. Internal Web reader opens existing children read-only, validates the held inode and hash before decode, then verifies decoded bytes/hash/sequence without returning partial data; maximum 48 MB, 100 concurrent reads and fault rejection tested. Projection's separate stub is not a real hash oracle. Complete startup metadata scanning now includes empty/partial parts and verified ready sizes, rejects unknown/corrupt entries and incomplete enumerations, and enforces the 10000-file inventory bound; it is not allocated-block disk usage or a live concurrent snapshot. An internal exclusive-startup diagnostic probe now verifies real A/B file force/hash/group, no-replace collision and directory fsync; only confirmed diagnostic artifacts are cleaned, while uncertain/changed ready files or cleanup failures remain failed startup evidence. Internal staged Scenario service now connects read-only authentication/Inbox/query, DB-free file work and freshly authenticated final Inbox commit/close before reply. T01-T05 use explicit publisher/inspector doubles; T06 connects real PostgreSQL/Artemis send/ACK failures; T07 connects real retained-inode writer/inspector and PostgreSQL with independent 201/10000-record bytes/hash and ready preservation. Full root/exclusive startup composition/readiness and scan-to-service initialization, production registration, actual service UID separation, HTTP and CHR remain incomplete as tracked in 431/008.",
    }
    if verify_reactor_junit(repo, run, commit) != report_receipt:
        raise ValueError("reactor JUnit receipt changed during collection")
    receipt_path = Path("logs") / (run + "-junit-receipt.json")
    (evidence / receipt_path).write_bytes(report_receipt)
    manifest["reactorJunitReceipt"] = str(receipt_path)
    manifest["reactorJunitReceiptSha256"] = hashlib.sha256(report_receipt).hexdigest()
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": sum(v["tests"] for v in modules.values()), "scenarioTests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
