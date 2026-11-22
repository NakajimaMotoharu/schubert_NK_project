#!/usr/bin/env python3
"""PT-IDEM-016: bind real Web-outbox/Artemis/API-ingest PT to one certified reactor."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root

CLASS = "dev.codex.schubert.nk.web.logging.WebApiLogReplayIntegrationTest"
METHOD = "idem016WebOutboxRetriesIntoApiProjectionExactlyOnce"
RESOURCE_CLASS = "dev.codex.schubert.nk.web.logging.WebLogDispatcherTest"
RESOURCE_METHODS = {
    "PT-IDEM-012-R02": "idem012r02SameJdbcFailureAtClaimRollbackAndClosePreservesPrimary",
    "PT-IDEM-012-R03": "idem012r03DistinctRollbackAndCloseFailuresRemainSecondary",
    "PT-IDEM-012-R04": "idem012r04RollbackFatalAndSameCloseFatalRemainFatal",
    "PT-IDEM-012-R05": "idem012r05CloseFatalAfterClaimFailureDoesNotHidePrimary",
}
SUBJECTS = (
    ("web", "dev/codex/schubert/nk/web/logging/WebLogOutboxRepository"),
    ("web", "dev/codex/schubert/nk/web/logging/WebLogDispatcher"),
    ("web", "dev/codex/schubert/nk/web/logging/WebLogMessageSender"),
    ("api", "dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumers"),
    ("api", "dev/codex/schubert/nk/api/messaging/inbound/WebLogListener"),
    ("api", "dev/codex/schubert/nk/api/logging/WebLogIngestService"),
)
SOURCES = (
    "src/schubert-nk-web/pom.xml",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebApiLogReplayIntegrationTest.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogDatabaseFixture.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogDispatcherTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogDispatcher.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogMessageSender.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogOutboxRepository.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumers.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogListener.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/WebLogIngestService.java",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_suite(suite):
    cases = suite.findall("testcase")
    if (suite.get("name") != CLASS or suite.get("tests") != "1"
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(cases) != 1 or cases[0].get("classname") != CLASS
            or cases[0].get("name") != METHOD
            or any(child.tag not in ("system-out", "system-err") for child in cases[0])):
        raise ValueError("missing, failed, flaky, or unlisted vertical Log PT")
    return {"PT-IDEM-016": CLASS + "#" + METHOD}


def validate_resource_suite(suite):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != RESOURCE_CLASS or suite.get("tests") != "9"
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(cases) != 9 or len(set(names)) != 9
            or any(names.count(name) != 1 for name in RESOURCE_METHODS.values())
            or any(case.get("classname") != RESOURCE_CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing or nonpassing Web Log JDBC Resource PT")
    return {test_id: RESOURCE_CLASS + "#" + name
            for test_id, name in RESOURCE_METHODS.items()}


def validate_coverage(report, subject):
    classes = [element for element in report.iter("class") if element.get("name") == subject]
    if len(classes) != 1:
        raise ValueError("vertical Log production class missing")
    counters = {c.get("type"): {"covered": int(c.get("covered")),
                                 "missed": int(c.get("missed"))}
                for c in classes[0].findall("counter")}
    required = ("INSTRUCTION", "LINE", "METHOD", "CLASS")
    if (not set(required).issubset(counters)
            or any(counters[k]["covered"] <= 0 or counters[k]["missed"] != 0
                   for k in required)
            or ("BRANCH" in counters and counters["BRANCH"]["missed"] != 0)):
        raise ValueError("vertical Log production coverage below 100%")
    return counters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = evidence_output_root(repo) / "008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise ValueError("matching successful reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True)
    junit_report = (repo / "src/schubert-nk-web/target/surefire-reports" /
                    ("TEST-" + CLASS + ".xml"))
    methods = validate_suite(ET.parse(junit_report).getroot())
    resource_report = (repo / "src/schubert-nk-web/target/surefire-reports" /
                       ("TEST-" + RESOURCE_CLASS + ".xml"))
    methods.update(validate_resource_suite(ET.parse(resource_report).getroot()))
    coverage = {}
    for module, subject in SUBJECTS:
        report = repo / f"src/schubert-nk-{module}/target/site/jacoco/jacoco.xml"
        coverage[subject] = validate_coverage(ET.parse(report).getroot(), subject)
    evidence = evidence_output_root(repo) / "006_NK-MSG-002/005_LogReplayVertical/evidence"
    for folder in ("logs", "input", "output", "coverage"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    program = repo / "evidence/01_PT/006_NK-MSG-002"
    for name in ("001_NK-MSG-002_単体テスト仕様書.md", "002_NK-MSG-002_実行結果.md",
                 "005_Log再送縦結線単体テスト仕様書.md", "006_Log再送縦結線実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    (evidence / "output/BUG-246-red.txt").write_bytes(
        (program / "006_WebLogJdbcResource/evidence/output/BUG-246-red.txt").read_bytes())
    oracle = {
        "testId": "PT-IDEM-016",
        "source": "UI232/235 fixed byte offsets; SS312/324/351; SQL postconditions on V001..022",
        "expected": {"firstSend": "ERROR/attempt1/JMS_SEND_FAILURE/API row0",
                     "beforeDue": "no claim at due minus 1 microsecond",
                     "retry": "SENT/attempt1/API WEB|REQUEST|HTTP_REQUEST_COMPLETED row1",
                     "duplicate": "second API callback, source_message_id row remains 1",
                     "terminalCallbacks": 0},
        "limitations": "Actual NK process startup and CHR-L01 not covered."
    }
    oracle["jdbcResource"] = {
        "source": "SS324 section 9/332 and Java Throwable self-suppression contract",
        "sameFailure": "original SQL exception identity, one rollback and close, no suppression",
        "distinctFailure": "rollback and close exceptions remain secondary in order",
        "fatalRollback": "fatal identity with original SQL failure suppressed, no self-suppression",
        "fatalClose": "fatal identity with original SQL failure suppressed",
    }
    (evidence / "input/oracle.json").write_text(json.dumps(oracle, indent=2) + "\n")
    suite = ET.Element("testsuite", name="NK-MSG-002-LOG-REPLAY-RESOURCE",
                       tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, qualified in methods.items():
        classname, name = qualified.split("#", 1)
        ET.SubElement(suite, "testcase", id=test_id, classname=classname, name=name, result="PASS")
    ET.ElementTree(suite).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({"programId": "NK-MSG-002", "testIds": methods,
                     "scopeResult": "PASS_REAL_LOG_REPLAY_AND_JDBC_RESOURCE_UNIT_ONLY",
                     "programComplete": False, "failed": 0, "errors": 0, "skipped": 0,
                     "expected": {"vertical": oracle["expected"], "jdbcResource": oracle["jdbcResource"]},
                     "actual": "All independent JUnit SQL/JMS/Resource assertions passed",
                     "coverage": coverage,
                     "related": ["PG253", "PG264", "PT-IDEM-016", "PT-IDEM-012-R02..R05",
                                 "BUG-246", "YKT-154", "RD MQ-006/008/010/MON-003/004/005",
                                 "UI231/235/242/251", "SS312/321/324/331/332/351/352"],
                     "limitations": oracle["limitations"],
                     "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
                     "fullReactorManifestSha256": digest(full),
                     "junitReportSha256": digest(junit_report),
                     "resourceJunitReportSha256": digest(resource_report),
                     "sourceFiles": [{"path": p, "sha256": digest(repo / p)} for p in SOURCES]})
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)}
                         for p in sorted(evidence.rglob("*")) if p.is_file()
                         and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "testIds": methods, "scopeResult": manifest["scopeResult"]}))


if __name__ == "__main__":
    main()
