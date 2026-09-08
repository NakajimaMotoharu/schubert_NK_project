#!/usr/bin/env python3
"""Bind non-mutating Inbox lookup and coordinator regression to a certified Scenario reactor."""

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
    if not args.run_id.startswith("PT-SCN-") or not all(c.isalnum() or c == "-" for c in args.run_id):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    source = repo / "evidence/01_PT/008_NK-SCN-001/evidence"
    validated = json.loads((source / "manifest.json").read_text())
    if validated["runId"] != args.run_id or validated["exitCode"] != 0:
        raise SystemExit("collect the matching verified Scenario run first")
    subprocess.run(["git", "diff", "--exit-code", validated["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    relative = "output/TEST-dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinatorTest.xml"
    expected = next(f["sha256"] for f in validated["files"] if f["path"] == relative)
    report = source / relative
    if hashlib.sha256(report.read_bytes()).hexdigest() != expected:
        raise SystemExit("certified report hash differs")
    suite = ET.parse(report).getroot()
    methods = [c.get("classname") + "#" + c.get("name") for c in suite.findall("testcase")]
    if any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped")) or len(methods) != 11:
        raise SystemExit("missing or nonpassing coordinator regression")
    evidence = repo / "evidence/01_PT/006_NK-MSG-002/evidence"
    old = json.loads((evidence / "manifest.json").read_text())
    old_id = old["runId"]
    if not all(c.isalnum() or c == "-" for c in old_id):
        raise SystemExit("invalid historical run ID")
    history = evidence / "logs" / (old_id + "-manifest.json")
    if old_id != args.run_id and not history.exists():
        shutil.copyfile(evidence / "manifest.json", history)
    shutil.copyfile(report, evidence / relative)
    for module in validated["modules"]:
        shutil.copyfile(source / "coverage" / (module + "-jacoco.csv"),
                        evidence / "coverage" / (module + "-jacoco.csv"))
    manifest = {k: validated[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                        "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MSG-002", "programStatus": "IN_PROGRESS", "result": "REGRESSION_SLICE_PASS",
        "currentReports": [relative], "methods": methods,
        "testIdsPassed": ["PT-IDEM-RO01", "PT-IDEM-RO02", "PT-IDEM-RO03", "PT-IDEM-RO04"],
        "relatedSsc": ["SSC-024"], "relatedBug": [], "notRunCountedAsPass": 0,
        "expectations": "Independent SS324 LP/JCE-HMAC plus production-DDL SQL fixtures; literal state, metadata, 29-byte storage-only ciphertext, count and retention. Missing returns empty, identity/body/key mismatches reject, and 100 read-only lookups succeed while another transaction holds the Inbox row lock. No production method generates expected HMAC or stored fixture.",
        "scope": "Current report is coordinator-only regression including existing seven methods. Other retained output belongs to historical runs and is not counted as newly certified program completion. Response decryption/reference validity, staged service/file replay, HTTP, cleanup protection BUG-014 and other NK-MSG-002 gates remain incomplete.",
        "redaction": "Copied hash-verified sanitized JUnit metadata only; no properties, stdout, provider text, secrets or master content.",
    })
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (evidence / "checksums.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
                                                     for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps({"runId": args.run_id, "coordinatorTests": len(methods), "status": "REGRESSION_SLICE_PASS"}))


if __name__ == "__main__":
    main()
