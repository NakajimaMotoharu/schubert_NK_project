#!/usr/bin/env python3
"""Bind protocol or messaging regressions to an already validated full-reactor authentication run."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--program", choices=("NK-PRO-002", "NK-MSG-002"), default="NK-PRO-002")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    auth = repo / "evidence/01_PT/007_NK-AUT-001/evidence/manifest.json"
    validated = json.loads(auth.read_text())
    if validated["runId"] != args.run_id or validated["exitCode"] != 0:
        raise SystemExit("collect and validate the matching authentication run first")
    subprocess.run(["git", "diff", "--exit-code", validated["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True, stdout=subprocess.DEVNULL)
    protocol = args.program == "NK-PRO-002"
    module = "protocol" if protocol else "api"
    directory = "002_NK-PRO-002" if protocol else "006_NK-MSG-002"
    evidence = repo / "evidence/01_PT" / directory / "evidence"
    old = json.loads((evidence / "manifest.json").read_text())
    old_id = old["runId"]
    if not all(c.isalnum() or c == "-" for c in old_id):
        raise SystemExit("invalid historical run ID")
    history = evidence / "logs" / (old_id + "-manifest.json")
    if old_id != args.run_id and not history.exists():
        shutil.copyfile(evidence / "manifest.json", history)
    target = repo / ("src/schubert-nk-" + module) / "target"
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
    if count != validated["modules"][module]["tests"]:
        raise SystemExit("protocol reports do not match the validated reactor run")
    (evidence / "coverage").mkdir(exist_ok=True)
    shutil.copyfile(target / "site/jacoco/jacoco.csv", evidence / "coverage" / (module + "-jacoco.csv"))
    static = ET.parse(target / "spotbugsXml.xml").getroot()
    if static.findall("BugInstance") or int(static.find("Errors").get("errors", "0")):
        raise SystemExit("protocol static analysis not clean")
    (evidence / "output/spotbugs.xml").write_text(
        '<BugCollection><Errors errors="0"/><FindBugsSummary total_bugs="0"/></BugCollection>\n')
    summary = {key: validated[key] for key in
               ("runId", "targetCommit", "branch", "startedAt", "completedAt", "exitCode",
                "command", "environment", "modules", "rawLogSha256", "redaction")}
    summary.update(programId=args.program, kind="FULL_REACTOR_COMPONENT_REGRESSION",
                   programStatus="REGRESSION_PASS" if protocol else "IN_PROGRESS",
                   moduleId=module, moduleMethods=methods,
                   testIds=["PT-CODEC-AUTHERR-001", "PT-CODEC-AUTHERR-002", "PT-CODEC-AUTHERR-003"] if protocol else ["PT-IDEM-013-R01", "PT-IDEM-WIPE-001", "PT-IDEM-WIPE-002", "PT-IDEM-WIPE-003"],
                   relatedBug=["BUG-023"] if protocol else ["BUG-025", "BUG-027", "BUG-014"],
                   relatedYkt=["YKT-020"] if protocol else ["YKT-022", "YKT-024", "YKT-012"],
                   relatedSsc=["SSC-012"] if protocol else [],
                   expectation="002 independent UI234 byte/TSV oracle; 006 independent completion/TTL SQL postconditions, synthetic zeroized backing arrays, independent JCA/DataOutputStream and OpenSSL HMAC vectors. Other programs and PGPT remain incomplete.",
                   previousEvidenceRun=old_id if old_id != args.run_id else old.get("previousEvidenceRun"),
                   notRunCountedAsPass=0)
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    summary["files"] = [{"path": str(path.relative_to(evidence)),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in sorted(evidence.rglob("*"))
                        if path.is_file() and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    write_scope_checksums(evidence, summary["files"])
    print(json.dumps({"runId": args.run_id, module + "Tests": count, "status": "REGRESSION_PASS"}))


if __name__ == "__main__":
    main()
