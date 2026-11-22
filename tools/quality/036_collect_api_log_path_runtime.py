#!/usr/bin/env python3
"""PT-JMS-018/019/022/023: certify API Log-path and borrowed connection gate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.api.dispatch.ApiLogPathApplicationRuntimeTest"
METHODS = (
    "realDatabaseAndBrokerBindThreeRoutesAndTerminal(Path)",
    "allDependenciesFailBeforeOpeningConsumer",
    "failedConsumerStartupDoesNotReturnPartialRuntime",
)
SUBJECT = "dev/codex/schubert/nk/api/dispatch/ApiLogPathApplicationRuntime"
READY_CLASS = "dev.codex.schubert.nk.api.dispatch.ApiDependencyReadinessTest"
READY_METHODS = (
    "realPostgresAndBothReceiveQueuesCloseAfterProbe",
    "nullAndInvalidDatabaseFailBeforeBroker",
    "jdbcInspectionAndCloseFailuresAreRedacted",
    "brokerNullModeAttachAndCloseFailuresAreRedacted",
    "stoppedBrokerCannotPassConnectivity",
    "apiReadinessFatalBrokerCloseCannotBeDowngradedToOrdinaryUnavailable",
    "apiReadinessOrdinaryInspectionAndCloseFailuresRemainRedacted",
    "apiReadinessFatalInspectionRetainsIdentityEvenWhenCloseAlsoFatal",
    "apiReadinessFatalDatabaseCloseCannotBeDowngradedToOrdinaryUnavailable",
    "apiReadinessOrdinaryDatabaseInspectionAndCloseFailuresRemainRedacted",
    "apiReadinessFatalDatabaseInspectionRetainsIdentityEvenWhenCloseAlsoFatal",
)
READY_SUBJECT = "dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness"
SOURCE_FILES = (
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiLogPathApplicationRuntime.java",
    "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/dispatch/ApiLogPathApplicationRuntimeTest.java",
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java",
    "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadinessTest.java",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_suite(root):
    cases = root.findall("testcase")
    names = [case.get("name") for case in cases]
    if (root.get("name") != CLASS or root.get("tests") != str(len(METHODS))
            or any(int(root.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != len(METHODS) or len(set(names)) != len(METHODS)
            or set(names) != set(METHODS)
            or any(case.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing, nonpassing, or unlisted API Log-path runtime PT")
    return {"PT-JMS-018-" + chr(ord("A") + index): CLASS + "#" + name
            for index, name in enumerate(METHODS)}


def validate_ready_suite(root):
    cases = root.findall("testcase")
    names = [case.get("name") for case in cases]
    if (root.get("name") != READY_CLASS or root.get("tests") != str(len(READY_METHODS))
            or any(int(root.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != len(READY_METHODS) or len(set(names)) != len(READY_METHODS)
            or set(names) != set(READY_METHODS)
            or any(case.get("classname") != READY_CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing, nonpassing, or unlisted API dependency readiness PT")
    return {("PT-JMS-019-" + chr(ord("A") + index) if index < 5
             else "PT-JMS-022-" + chr(ord("A") + index - 5) if index < 8
             else "PT-JMS-023-" + chr(ord("A") + index - 8)): READY_CLASS + "#" + name
            for index, name in enumerate(READY_METHODS)}


def validate_coverage(report):
    classes = [element for element in report.iter("class") if element.get("name") == SUBJECT]
    if len(classes) != 1:
        raise ValueError("API Log-path runtime production class missing")
    counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                       "covered": int(counter.get("covered"))}
                for counter in classes[0].findall("counter")}
    required = ("INSTRUCTION", "LINE", "METHOD", "CLASS")
    if (not set(required).issubset(counters)
            or any(counters[kind]["missed"] != 0 or counters[kind]["covered"] <= 0
                   for kind in required)
            or ("BRANCH" in counters and counters["BRANCH"]["missed"] != 0)):
        raise ValueError("API Log-path runtime production coverage below 100%")
    return counters


def validate_ready_coverage(report):
    classes = [element for element in report.iter("class") if element.get("name") == READY_SUBJECT]
    if len(classes) != 1:
        raise ValueError("API dependency readiness production class missing")
    counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                       "covered": int(counter.get("covered"))}
                for counter in classes[0].findall("counter")}
    required = ("INSTRUCTION", "LINE", "METHOD", "CLASS", "BRANCH")
    if (not set(required).issubset(counters)
            or any(counters[kind]["missed"] != 0 or counters[kind]["covered"] <= 0
                   for kind in required)):
        raise ValueError("API dependency readiness production coverage below 100%")
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
    ready_methods = validate_ready_suite(ET.parse(target / "surefire-reports" / ("TEST-" + READY_CLASS + ".xml")).getroot())
    report = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
    coverage = {"runtime": validate_coverage(report), "readiness": validate_ready_coverage(report)}
    program = repo / "evidence/01_PT/005_NK-MSG-001"
    evidence = program / "evidence/api-log-path-runtime"
    for folder in ("logs", "input", "output", "coverage"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    for name in ("001_NK-MSG-001_単体テスト仕様書.md", "002_NK-MSG-001_実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    oracle = {"testIds": ["PT-JMS-018", "PT-JMS-019", "PT-JMS-022", "PT-JMS-023"],
              "subcases": list(methods) + list(ready_methods),
              "syncConsumers": 4, "webLogConsumers": 1,
              "loginTransaction": "JDBC autoCommit false before handler; commit before JMS reply owner",
              "terminal": "one signal after committed fatal DLQ; both consumer groups closed",
              "preflight": "JDBC isValid(2), then borrowed transacted JMS attachment to exact sync/Web-log FQQNs; no consumption",
              "resourceFailurePrecedence": "fatal owned JMS or JDBC close escapes ordinary inspection; two ordinary failures remain fixed/redacted; fatal inspection retains identity against fatal close",
              "source": "SS312/321/324 five-consumer, preflight and transaction/terminal contracts; 442 owned resource failure precedence; not production count calculation"}
    (evidence / "input/oracle.json").write_text(json.dumps(oracle, indent=2) + "\n")
    suite = ET.Element("testsuite", name="PT-JMS-018-019-022-023", tests=str(len(methods) + len(ready_methods)),
                       failures="0", errors="0", skipped="0")
    for test_id, method in (methods | ready_methods).items():
        ET.SubElement(suite, "testcase", id=test_id, classname=method.split("#")[0],
                      name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MSG-001", "testIds": methods | ready_methods,
        "scopeResult": "PASS_API_LOG_PATH_STARTUP_UNIT_ONLY", "programComplete": False,
        "coverage": coverage, "failed": 0, "errors": 0, "skipped": 0,
        "related": ["PG233/234/266/268", "PT-JMS-018/019/022/023", "BUG-248/249", "YKT-154", "RD FUN-001/008 AUT-001/002 MQ-001/003/006/008 SYS-004",
                    "UI225/226/231/232/235", "SS311/312/314/321/323/324"],
        "limitations": "No full API process, production credentials, broker-management readiness, real NK CHR or IT/ST.",
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full),
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCE_FILES]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "testIds": ["PT-JMS-018", "PT-JMS-019", "PT-JMS-022", "PT-JMS-023"],
                      "subcases": len(methods) + len(ready_methods),
                      "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
