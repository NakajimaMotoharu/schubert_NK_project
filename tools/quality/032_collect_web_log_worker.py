#!/usr/bin/env python3
"""PT-IDEM-012-W01: certify real Web Log background retry and bounded lifecycle."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root

CLASS = "dev.codex.schubert.nk.web.logging.WebLogReplayWorkerTest"
METHODS = (
    "realOutboxRetriesInBackgroundAndSendsOnce",
    "temporarySqlAndRuntimeFailuresRecoverWithoutLeakingDetails",
    "fatalVmFailureMakesWorkerNotReadyWithoutExposingCause",
    "closeIsIdempotentAndRejectsInvalidInputs",
    "boundedStopReportsUnresponsiveWorkerThenReleases",
    "interruptedStopRestoresCallerFlag",
)
SUBJECTS = (
    "dev/codex/schubert/nk/web/logging/WebLogReplayWorker",
    "dev/codex/schubert/nk/web/logging/WebLogReplayWorker$Snapshot",
)
SOURCE_FILES = (
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogReplayWorker.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogReplayWorkerTest.java",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != str(len(METHODS))
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != len(METHODS) or len(set(names)) != len(METHODS)
            or set(names) != set(METHODS)
            or any(case.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing, nonpassing, or unlisted Web Log worker PT")
    return {"PT-IDEM-012-W01-" + chr(ord("A") + index): CLASS + "#" + name
            for index, name in enumerate(METHODS)}


def validate_coverage(report):
    classes = [element for element in report.iter("class") if element.get("name") in SUBJECTS]
    if len(classes) != len(SUBJECTS) or {item.get("name") for item in classes} != set(SUBJECTS):
        raise ValueError("Web Log worker production classes missing")
    results = {}
    for subject in classes:
        counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                           "covered": int(counter.get("covered"))}
                    for counter in subject.findall("counter")}
        if (not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
                or any(counters[kind]["missed"] != 0 or counters[kind]["covered"] <= 0
                       for kind in ("LINE", "METHOD", "CLASS", "BRANCH"))):
            raise ValueError("Web Log worker production coverage below 100%")
        results[subject.get("name")] = counters
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(char.isalnum() or char == "-" for char in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = evidence_output_root(repo) / "008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise ValueError("matching successful reactor run required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True)
    target = repo / "src/schubert-nk-web/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    program = repo / "evidence/01_PT/006_NK-MSG-002"
    evidence = evidence_output_root(repo) / "006_NK-MSG-002/003_WebLogReplayWorker/evidence"
    for folder in ("logs", "input", "output", "coverage", "database"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    for name in ("001_NK-MSG-002_単体テスト仕様書.md", "002_NK-MSG-002_実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    oracle = {"testId": "PT-IDEM-012-W01", "subcases": list(methods),
              "workerCount": 1, "batchLimit": "1..100", "leaseSeconds": 10,
              "firstRetryMilliseconds": 1000,
              "expected": "PENDING to ERROR on first send failure; due replay to SENT; one JMS delivery; bounded stop and no later cycle",
              "source": "SS324 section 9, SS332 Web outbox SQL postconditions and prior independent PT-IDEM-012 matrix"}
    (evidence / "input/oracle.json").write_text(json.dumps(oracle, indent=2) + "\n")
    suite = ET.Element("testsuite", name="PT-IDEM-012-W01", tests=str(len(methods)),
                       failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS,
                      name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    (evidence / "database/postconditions.json").write_text(json.dumps({
        "testId": "PT-IDEM-012-W01-A", "fixture": "isolated PostgreSQL 18/Flyway and Artemis File Journal",
        "expectedSqlStatus": ["PENDING", "ERROR", "SENT"], "expectedJmsDeliveries": 1,
        "actualEvidence": "JUnit XML asserts persisted SENT, exactly two send attempts and one broker delivery; no row or wire exported"
    }, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MSG-002", "testIds": methods,
        "scopeResult": "PASS_WEB_LOG_BACKGROUND_RETRY_UNIT_ONLY", "programComplete": False,
        "coverage": coverage, "failed": 0, "errors": 0, "skipped": 0,
        "related": ["PG226", "PT-IDEM-012-W01", "RD MON-003/MQ-008", "UI242", "SS311/324/332"],
        "limitations": "No Web parent bootstrap, API log listener/process or real NK CHR; IT/ST not run.",
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full),
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCE_FILES]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "testId": "PT-IDEM-012-W01", "subcases": len(methods),
                      "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
