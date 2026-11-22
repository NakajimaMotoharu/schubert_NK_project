#!/usr/bin/env python3
"""PT-JMS-020: certify Web request-sender compound Resource failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest"
SUBJECT = "dev/codex/schubert/nk/web/messaging/ArtemisRequestSender"
BASE_METHODS = (
    "sendsOneValidatedPersistentRequestAndCommits(Path)",
    "nullWireIdentityLengthKindAndSessionModeFailBeforeCommit",
    "checkedAndRuntimeProviderFailuresRollbackAndPreserveThePrimaryFailure",
)
METHODS = {
    "PT-JMS-020-A": "jms020aSameFailureReplayedByRollbackCannotMaskPrimary",
    "PT-JMS-020-B": "jms020bSameFailureReplayedByCloseCannotMaskPrimary",
    "PT-JMS-020-C": "jms020cCloseOnlyFailureRemainsVisible",
    "PT-JMS-020-D": "jms020dDistinctSecondaryFailuresRemainVisible",
}
SOURCES = (
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisRequestSender.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ArtemisRequestSenderTest.java",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "7"
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(cases) != 7 or len(set(names)) != 7
            or set(names) != set(BASE_METHODS) | set(METHODS.values())
            or any(case.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing, nonpassing, or unlisted Web request-sender PT")
    return {test_id: CLASS + "#" + name for test_id, name in METHODS.items()}


def validate_coverage(report):
    classes = [element for element in report.iter("class") if element.get("name") == SUBJECT]
    if len(classes) != 1:
        raise ValueError("Web request-sender production class missing")
    counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                      "covered": int(counter.get("covered"))}
                for counter in classes[0].findall("counter")}
    required = ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH")
    if (not set(required).issubset(counters)
            or any(counters[kind]["missed"] != 0 or counters[kind]["covered"] <= 0
                   for kind in required)):
        raise ValueError("Web request-sender production coverage below 100%")
    return counters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(char.isalnum() or char == "-" for char in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise ValueError("matching successful reactor run required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True)
    target = repo / "src/schubert-nk-web/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    program = repo / "evidence/01_PT/005_NK-MSG-001"
    evidence = program / "evidence/request-sender-resource"
    for folder in ("logs", "input", "output", "coverage"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    for name in ("001_NK-MSG-001_単体テスト仕様書.md", "002_NK-MSG-001_実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    oracle = {"testIds": list(METHODS), "source": "SS321/324 and Java Throwable self-suppression contract",
              "expected": {"A": "same primary, rollback1, close1, no suppression",
                           "B": "same primary, rollback1, close1, no suppression",
                           "C": "close failure visible after commit, close1",
                           "D": "primary identity with rollback then close secondary, each once"},
              "scope": "sender unit only; no claim of delivery after failure or full NK startup"}
    (evidence / "input/oracle.json").write_text(json.dumps(oracle, indent=2) + "\n")
    suite = ET.Element("testsuite", name="PT-JMS-020", tests="4", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS,
                      name=method.split("#", 1)[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MSG-001", "testIds": methods,
        "scopeResult": "PASS_WEB_REQUEST_SENDER_RESOURCE_UNIT_ONLY", "programComplete": False,
        "coverage": coverage, "failed": 0, "errors": 0, "skipped": 0,
        "related": ["PG250", "PT-JMS-020", "BUG-241", "YKT-154", "RD MQ-003/008",
                    "UI231", "SS321/324", "442"],
        "limitations": "JMS other owners and Production startup/real NK CHR remain unverified.",
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full),
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCES]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "testIds": list(METHODS), "scopeResult": manifest["scopeResult"]}))


if __name__ == "__main__":
    main()
