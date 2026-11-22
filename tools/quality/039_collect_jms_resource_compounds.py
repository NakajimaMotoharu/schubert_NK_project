#!/usr/bin/env python3
"""Certify JMS rollback and owned-context close compound contracts by Program."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root

SUBJECTS = (
    ("PT-JMS-021", "NK-MSG-001", "005_NK-MSG-001", "web",
     "dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumerTest",
     "jms021SameProviderFailureOnCommitAndRollbackPreservesPrimaryIdentity", 7,
     "dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumer"),
    ("PT-IDEM-010-R01", "NK-MSG-002", "006_NK-MSG-002", "api",
     "dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest",
     "idem010r01SameProviderFailureOnStageAndRollbackKeepsOriginalCause", 14,
     "dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender"),
    ("PT-IDEM-010-R02", "NK-MSG-002", "006_NK-MSG-002", "api",
     "dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest",
     "idem010r02SameProviderFailureOnSessionModeAndCloseKeepsOriginalCause", 14,
     "dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender"),
    ("PT-IDEM-010-R03", "NK-MSG-002", "006_NK-MSG-002", "api",
     "dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest",
     "idem010r03DistinctSessionModeAndCloseFailuresKeepFixedPrimary", 14,
     "dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender"),
    ("PT-IDEM-010-R04", "NK-MSG-002", "006_NK-MSG-002", "api",
     "dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest",
     "idem010r04FatalSessionModeAndCloseKeepFatalIdentity", 14,
     "dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender"),
    ("PT-IDEM-010-R05", "NK-MSG-002", "006_NK-MSG-002", "api",
     "dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest",
     "idem010r05CommittedSendCloseRuntimeAndFatalNeverReturnSuccess(Path)", 14,
     "dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender"),
    ("PT-IDEM-012-R01", "NK-MSG-002", "006_NK-MSG-002", "web",
     "dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest",
     "idem012r01SameProviderFailureOnStageAndRollbackKeepsOriginalCauseAndErasesWire", 5,
     "dev/codex/schubert/nk/web/logging/WebLogMessageSender"),
)
SOURCES = (
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumer.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumerTest.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.java",
    "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatcherTest.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogMessageSender.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogMessageSenderTest.java",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_suite(root, class_name, expected_method, total):
    cases = root.findall("testcase")
    names = [case.get("name") for case in cases]
    if (root.get("name") != class_name or root.get("tests") != str(total)
            or any(int(root.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(cases) != total or len(set(names)) != total
            or names.count(expected_method) != 1
            or any(case.get("classname") != class_name or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing or nonpassing JMS compound PT")
    return class_name + "#" + expected_method


def validate_coverage(report, subject):
    classes = [element for element in report.iter("class") if element.get("name") == subject]
    if len(classes) != 1:
        raise ValueError("JMS compound production class missing")
    counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                      "covered": int(counter.get("covered"))}
                for counter in classes[0].findall("counter")}
    required = ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH")
    if (not set(required).issubset(counters)
            or any(counters[kind]["missed"] != 0 or counters[kind]["covered"] <= 0
                   for kind in required)):
        raise ValueError("JMS compound production coverage below 100%")
    return counters


def write_scope(repo, full, verified, program_id, folder, methods, coverage):
    program = repo / "evidence/01_PT" / folder
    candidate = evidence_output_root(repo) / folder
    evidence = (candidate / "evidence/jms-resource-compounds" if program_id == "NK-MSG-001"
                else candidate / "004_JmsResourceCompounds/evidence")
    for name in ("logs", "input", "output", "coverage"):
        (evidence / name).mkdir(parents=True, exist_ok=True)
    for name in ("001_" + program_id + "_単体テスト仕様書.md",
                 "002_" + program_id + "_実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    oracle = {"testIds": list(methods), "source": "SS312/321/324 and Java Throwable self-suppression contract",
              "expected": "same provider Throwable on primary and rollback/close: original identity/cause, each owned resource closed once, no self-suppression; distinct close failure is secondary, and no unconfirmed delivery or ACK success",
              "scope": "three sender/consumer resource units only; not full NK startup"}
    (evidence / "input/oracle.json").write_text(json.dumps(oracle, indent=2) + "\n")
    suite = ET.Element("testsuite", name="JMS-RESOURCE-COMPOUNDS", tests=str(len(methods)),
                       failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        classname, name = method.split("#", 1)
        ET.SubElement(suite, "testcase", id=test_id, classname=classname, name=name, result="PASS")
    ET.ElementTree(suite).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": program_id, "testIds": methods,
        "scopeResult": "PASS_JMS_RESOURCE_COMPOUND_UNIT_ONLY", "programComplete": False,
        "coverage": coverage, "failed": 0, "errors": 0, "skipped": 0,
        "related": ["PG251", "BUG-242", "BUG-244", "YKT-154", "RD MQ-003/004/006/008",
                    "UI231/242", "SS312/321/324", "442"],
        "limitations": "Other JMS/JDBC/IO owners, Production startup, real NK CHR and IT/ST remain unverified.",
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full),
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCES]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])


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
    methods = {"NK-MSG-001": {}, "NK-MSG-002": {}}
    coverage = {"NK-MSG-001": {}, "NK-MSG-002": {}}
    for test_id, program, _, module, class_name, method, count, subject in SUBJECTS:
        target = repo / ("src/schubert-nk-" + module) / "target"
        methods[program][test_id] = validate_suite(
            ET.parse(target / "surefire-reports" / ("TEST-" + class_name + ".xml")).getroot(),
            class_name, method, count)
        coverage[program][subject] = validate_coverage(
            ET.parse(target / "site/jacoco/jacoco.xml").getroot(), subject)
    for program, folder in (("NK-MSG-001", "005_NK-MSG-001"),
                            ("NK-MSG-002", "006_NK-MSG-002")):
        write_scope(repo, full, verified, program, folder, methods[program], coverage[program])
    print(json.dumps({"runId": run, "testIds": list(methods["NK-MSG-001"] | methods["NK-MSG-002"]),
                      "scopeResult": "PASS_JMS_RESOURCE_COMPOUND_UNIT_ONLY"}))


if __name__ == "__main__":
    main()
