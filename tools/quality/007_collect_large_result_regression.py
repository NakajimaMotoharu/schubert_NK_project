#!/usr/bin/env python3
"""Bind NK-PRO-003 regression and compiled constant-time callsite to a certified Scenario reactor run."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    validated = json.loads((evidence_output_root(repo) / "008_NK-SCN-001/evidence/manifest.json").read_text())
    if validated["runId"] != args.run_id or validated["exitCode"] != 0:
        raise SystemExit("collect the matching verified Scenario run first")
    subprocess.run(["git", "diff", "--exit-code", validated["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
    target = repo / "src/schubert-nk-protocol/target"
    evidence = evidence_output_root(repo) / "003_NK-PRO-003/evidence"
    old = json.loads((evidence / "manifest.json").read_text())
    old_id = old["runId"]
    if not all(c.isalnum() or c == "-" for c in old_id):
        raise SystemExit("invalid historical run ID")
    history = evidence / "logs" / (old_id + "-manifest.json")
    history.parent.mkdir(parents=True, exist_ok=True)
    if old_id != args.run_id and not history.exists():
        shutil.copyfile(evidence / "manifest.json", history)
    methods = []
    names = ("dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest",
             "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest",
             "dev.codex.schubert.nk.protocol.time.JstWireTimestampTest")
    for name in names:
        report = target / "surefire-reports" / ("TEST-" + name + ".xml")
        suite = ET.parse(report).getroot()
        if any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped")):
            raise SystemExit("nonpassing large-result test")
        clean = ET.Element("testsuite", {k: suite.get(k) for k in ("name", "time", "tests", "errors", "failures", "skipped")})
        for case in suite.findall("testcase"):
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("nonpassing/flaky test")
            attrs = {k: case.get(k) for k in ("name", "classname", "time")}
            ET.SubElement(clean, "testcase", attrs)
            methods.append(attrs["classname"] + "#" + attrs["name"])
        ET.indent(clean)
        ET.ElementTree(clean).write(evidence / "output" / report.name, encoding="UTF-8", xml_declaration=True)
    bytecode = subprocess.check_output([
        "/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javap", "-c", "-classpath", str(target / "classes"),
        "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodec"], text=True)
    if "Method java/security/MessageDigest.isEqual:([B[B)Z" not in bytecode or "java/lang/String.equals:" in bytecode:
        raise SystemExit("compiled integrity comparison is not the specified JDK primitive")
    for name in ("jacoco.csv", "jacoco.xml"):
        shutil.copyfile(target / "site/jacoco" / name, evidence / "coverage" / name)
    shutil.copyfile(target / "spotbugsXml.xml", evidence / "output/spotbugs.xml")
    manifest = {
        "runId": args.run_id, "programId": "NK-PRO-003", "targetCommit": validated["targetCommit"],
        "branch": validated["branch"], "startedAt": validated["startedAt"], "completedAt": validated["completedAt"],
        "command": validated["command"], "environment": validated["environment"], "exitCode": 0,
        "result": "PASS_PROGRAM_COMPLETE", "tests": {"program": len(methods), "reactor": sum(v["tests"] for v in validated["modules"].values())},
        "methods": methods, "module": validated["modules"]["protocol"],
        "relatedBugs": ["BUG-034", "BUG-037", "BUG-040"], "relatedYkt": ["YKT-030", "YKT-033", "YKT-036"], "relatedSsc": ["SSC-004"],
        "testId": "PT-PRO-003-H01/T03/T04/T05/M03 plus full existing NK-PRO-003 regression",
        "expected": "Independent JCA 32-byte digest; valid record accepted; each of 32 digest-byte mutations rejected. Compiled verification invokes MessageDigest.isEqual, with no String.equals callsite. Independent 17-digit timestamp boundaries reject expanded/signed years and unrepresentable instants before Header or required/optional DATA encoding; valid boundary and parse vectors are preserved.",
        "actual": "PASS", "bytecodeSha256": hashlib.sha256(bytecode.encode()).hexdigest(),
        "rawLogSha256": validated["rawLogSha256"],
        "redaction": "JUnit names/counters only, no properties/stdout/stderr; public synthetic bytes, no secrets or master content.",
        "scope": "NK-PRO-003 codec/timestamp/descriptor only; Scenario application/file lifecycle/HTTP/IT/ST remain incomplete.",
    }
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": args.run_id, "programTests": len(methods), "status": "PASS_PROGRAM_COMPLETE"}))


if __name__ == "__main__":
    main()
