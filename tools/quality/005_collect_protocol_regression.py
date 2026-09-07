#!/usr/bin/env python3
"""Bind a protocol regression package to the already validated full-reactor authentication run."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    auth = repo / "evidence/01_PT/007_NK-AUT-001/evidence/manifest.json"
    validated = json.loads(auth.read_text())
    if validated["runId"] != args.run_id or validated["exitCode"] != 0:
        raise SystemExit("collect and validate the matching authentication run first")
    subprocess.run(["git", "diff", "--exit-code", validated["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True, stdout=subprocess.DEVNULL)
    evidence = repo / "evidence/01_PT/002_NK-PRO-002/evidence"
    old = json.loads((evidence / "manifest.json").read_text())
    old_id = old["runId"]
    if not all(c.isalnum() or c == "-" for c in old_id):
        raise SystemExit("invalid historical run ID")
    history = evidence / "logs" / (old_id + "-manifest.json")
    if old_id != args.run_id and not history.exists():
        shutil.copyfile(evidence / "manifest.json", history)
    target = repo / "src/schubert-nk-protocol/target"
    methods = []
    count = 0
    for report in sorted((target / "surefire-reports").glob("TEST-*.xml")):
        suite = ET.parse(report).getroot()
        if any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped")):
            raise SystemExit("nonpassing protocol report")
        clean = ET.Element("testsuite", {k: suite.get(k) for k in
                                        ("name", "time", "tests", "errors", "failures", "skipped")})
        cases = suite.findall("testcase")
        if len(cases) != int(suite.get("tests")):
            raise SystemExit("inconsistent protocol method count")
        for case in cases:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("skipped/flaky/failure result cannot be certified")
            ET.SubElement(clean, "testcase", {k: case.get(k) for k in ("name", "classname", "time")})
            methods.append(case.get("classname") + "#" + case.get("name"))
        count += len(cases)
        ET.indent(clean)
        ET.ElementTree(clean).write(evidence / "output" / report.name,
                                   encoding="UTF-8", xml_declaration=True)
    if count != validated["modules"]["protocol"]["tests"]:
        raise SystemExit("protocol reports do not match the validated reactor run")
    (evidence / "coverage").mkdir(exist_ok=True)
    shutil.copyfile(target / "site/jacoco/jacoco.csv", evidence / "coverage/protocol-jacoco.csv")
    static = ET.parse(target / "spotbugsXml.xml").getroot()
    if static.findall("BugInstance") or int(static.find("Errors").get("errors", "0")):
        raise SystemExit("protocol static analysis not clean")
    (evidence / "output/spotbugs.xml").write_text(
        '<BugCollection><Errors errors="0"/><FindBugsSummary total_bugs="0"/></BugCollection>\n')
    summary = {key: validated[key] for key in
               ("runId", "targetCommit", "branch", "startedAt", "completedAt", "exitCode",
                "command", "environment", "modules", "rawLogSha256", "redaction")}
    summary.update(programId="NK-PRO-002", kind="FULL_REACTOR_PROTOCOL_REGRESSION",
                   programStatus="REGRESSION_PASS", protocolMethods=methods,
                   testIds=["PT-CODEC-AUTHERR-001", "PT-CODEC-AUTHERR-002", "PT-CODEC-AUTHERR-003"],
                   relatedBug=["BUG-023"], relatedYkt=["YKT-020"], relatedSsc=["SSC-012"],
                   expectation="002 PT specification; independent UI234 byte vectors and unchanged UI fixture TSV. Other programs and PGPT remain incomplete.",
                   previousCompletionRun="PT-PRO-20260902-08", notRunCountedAsPass=0)
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    summary["files"] = [{"path": str(path.relative_to(evidence)),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in sorted(evidence.rglob("*"))
                        if path.is_file() and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (evidence / "checksums.sha256").write_text("".join(
        hashlib.sha256(path.read_bytes()).hexdigest() + "  " + str(path.relative_to(evidence)) + "\n"
        for path in sorted(evidence.rglob("*")) if path.is_file() and path.name != "checksums.sha256"))
    print(json.dumps({"runId": args.run_id, "protocolTests": count, "status": "REGRESSION_PASS"}))


if __name__ == "__main__":
    main()
