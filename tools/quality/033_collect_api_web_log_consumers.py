#!/usr/bin/env python3
"""PT-JMS-015: certify one real API Web-log consumer, not the full API parent."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.api.messaging.inbound.WebLogConsumersTest"
METHODS = (
    "oneConsumerCommitsValidatedWebLog(Path)",
    "temporaryProcessorFailureRollsBackAndRedelivers(Path)",
    "permanentInvalidEventsCommitDlqAndSignalTerminalOnce(Path)",
    "startupRejectsNullAndWrongModeBeforeDelivery(Path)",
    "closeIsIdempotentAndStartupPreservesCloseFailure",
)
SUBJECT = "dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumers"
SOURCE_FILES = (
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumers.java",
    "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumersTest.java",
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
        raise ValueError("missing, nonpassing, or unlisted API Web-log consumer PT")
    return {"PT-JMS-015-" + chr(ord("A") + index): CLASS + "#" + name
            for index, name in enumerate(METHODS)}


def validate_coverage(report):
    classes = [element for element in report.iter("class") if element.get("name") == SUBJECT]
    if len(classes) != 1:
        raise ValueError("API Web-log consumer production class missing")
    counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                       "covered": int(counter.get("covered"))}
                for counter in classes[0].findall("counter")}
    if (not {"INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
            or any(counters[kind]["missed"] != 0 or counters[kind]["covered"] <= 0
                   for kind in ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH"))):
        raise ValueError("API Web-log consumer production coverage below 100%")
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
    target = repo / "src/schubert-nk-api/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    program = repo / "evidence/01_PT/005_NK-MSG-001"
    evidence = program / "evidence/api-web-log-consumer"
    for folder in ("logs", "input", "output", "coverage"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    for name in ("001_NK-MSG-001_単体テスト仕様書.md", "002_NK-MSG-001_実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    oracle = {"testId": "PT-JMS-015", "subcases": list(methods),
              "consumerCount": 1, "sessionMode": "SESSION_TRANSACTED",
              "sourceQueue": "nk.web.log::nk.web.log.q",
              "fatalQueue": "nk.dead.letter::nk.dead.letter.q",
              "expected": "valid log ACK once; temporary failure rollback/redelivery; permanent invalid DLQ/terminal once; failed startup closes",
              "source": "SS321 sections 6-10 and SS323 fixed header offsets; not production encoder"}
    (evidence / "input/oracle.json").write_text(json.dumps(oracle, indent=2) + "\n")
    suite = ET.Element("testsuite", name="PT-JMS-015", tests=str(len(methods)),
                       failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS,
                      name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MSG-001", "testIds": methods,
        "scopeResult": "PASS_API_WEB_LOG_SINGLE_CONSUMER_UNIT_ONLY", "programComplete": False,
        "coverage": coverage, "failed": 0, "errors": 0, "skipped": 0,
        "related": ["PG228", "PT-JMS-015", "RD MQ-006/008/010 MON-003/005", "UI212/231/251", "SS312/321/323"],
        "limitations": "No production API parent, Web parent, full broker readiness, real NK CHR or IT/ST.",
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full),
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCE_FILES]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "testId": "PT-JMS-015", "subcases": len(methods),
                      "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
