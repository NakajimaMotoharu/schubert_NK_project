#!/usr/bin/env python3
"""Bind non-mutating Inbox lookup and coordinator regression to a certified Scenario reactor."""

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
    if not args.run_id.startswith(("PT-SCN-", "PT-MED-", "PT-ADM-", "PT-WEB-")) or not all(c.isalnum() or c == "-" for c in args.run_id):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    source = evidence_output_root(repo) / "008_NK-SCN-001/evidence"
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
    replacement_relative = "output/TEST-dev.codex.schubert.nk.api.idempotency.JdbcScenarioSnapshotReplacementTest.xml"
    replacement_report = source / replacement_relative
    replacement_hash = next(f["sha256"] for f in validated["files"] if f["path"] == replacement_relative)
    if hashlib.sha256(replacement_report.read_bytes()).hexdigest() != replacement_hash:
        raise SystemExit("certified replacement report hash differs")
    replacement_suite = ET.parse(replacement_report).getroot()
    replacement_methods = [c.get("classname") + "#" + c.get("name") for c in replacement_suite.findall("testcase")]
    replacement_ids = {k: v for k, v in validated["testIdMethods"].items() if k.startswith("PT-IDEM-SR")}
    if (any(int(replacement_suite.get(k, "0")) for k in ("errors", "failures", "skipped"))
            or len(replacement_methods) != 3 or len(replacement_ids) != 3
            or set(replacement_methods) != set(replacement_ids.values())):
        raise SystemExit("missing or nonpassing replacement regression")
    evidence = evidence_output_root(repo) / "006_NK-MSG-002/evidence"
    bound_relative = "output/TEST-dev.codex.schubert.nk.api.idempotency.BoundInboxExecutionTest.xml"
    bound_report = source / bound_relative
    bound_hash = next(f["sha256"] for f in validated["files"] if f["path"] == bound_relative)
    if hashlib.sha256(bound_report.read_bytes()).hexdigest() != bound_hash:
        raise SystemExit("certified bound execution report hash differs")
    bound_suite = ET.parse(bound_report).getroot()
    bound_methods = [c.get("classname") + "#" + c.get("name") for c in bound_suite.findall("testcase")]
    bound_ids = {k: v for k, v in validated["testIdMethods"].items() if k.startswith("PT-IDEM-B")}
    if (any(int(bound_suite.get(k, "0")) for k in ("errors", "failures", "skipped"))
            or len(bound_methods) != 4 or len(bound_ids) != 4
            or set(bound_methods) != set(bound_ids.values())):
        raise SystemExit("missing or nonpassing bound execution regression")
    old = json.loads((evidence / "manifest.json").read_text())
    old_id = old["runId"]
    if not all(c.isalnum() or c == "-" for c in old_id):
        raise SystemExit("invalid historical run ID")
    history = evidence / "logs" / (old_id + "-manifest.json")
    if old_id != args.run_id and not history.exists():
        shutil.copyfile(evidence / "manifest.json", history)
    shutil.copyfile(report, evidence / relative)
    shutil.copyfile(replacement_report, evidence / replacement_relative)
    shutil.copyfile(bound_report, evidence / bound_relative)
    for module in validated["modules"]:
        shutil.copyfile(source / "coverage" / (module + "-jacoco.csv"),
                        evidence / "coverage" / (module + "-jacoco.csv"))
    manifest = {k: validated[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                        "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MSG-002", "programStatus": "IN_PROGRESS", "result": "REGRESSION_SLICE_PASS",
        "currentReports": [relative, replacement_relative, bound_relative], "methods": methods + replacement_methods + bound_methods,
        "testIdMethods": replacement_ids | bound_ids,
        "testIdsPassed": ["PT-IDEM-RO01", "PT-IDEM-RO02", "PT-IDEM-RO03", "PT-IDEM-RO04", "PT-IDEM-SR01", "PT-IDEM-SR02", "PT-IDEM-SR03"] + list(bound_ids),
        "relatedSsc": ["SSC-024", "SSC-027", "SSC-033"], "relatedBug": ["BUG-049"], "relatedYkt": ["YKT-044"], "notRunCountedAsPass": 0,
        "expectations": "Independent SS324 LP/JCE-HMAC plus production-DDL SQL fixtures; literal state, metadata, 29-byte storage-only ciphertext, count and retention. Missing returns empty, identity/body/key mismatches reject, and 100 read-only lookups succeed while another transaction holds the Inbox row lock. No production method generates expected HMAC or stored fixture.",
        "replacementExpectations": "Real PostgreSQL row lock and caller commit/rollback; exactly one of two concurrent old-snapshot replacements commits. Only ciphertext/key change; all 17 metadata columns including original completion/24h expiry stay equal. Independent LP/JCE-HMAC and SQL fixture, all metadata/cipher positions/missing/identity/null/JDBC faults; temporary bind arrays zeroed. Synthetic 29-byte ciphertext is storage-only, not a decryption oracle.",
        "boundExpectations": "Independent SS324 LP/JCE-HMAC, literal 24-byte body and SQL PK/count/time expectations. Source PK is original for same-Message and different-Message same-token replay; original AES-GCM AAD decrypts while retry ID fails. Real unique races reread original PROCESSING source, 100 concurrent distinct Messages produce one execution/row/source. NULL/wrong PK, JDBC query/close, unknown key and HMAC mismatch reject. Legacy execute/one-query read-only inspect and Scenario snapshot replacement preserve metadata/retention and caller transaction ownership. Bound metadata grants no authorization.",
        "scope": "Current reports cover coordinator regression (11 methods), Scenario-only snapshot replacement (3 methods) and saved-Message binding (4 methods). Other retained output belongs to historical runs and is not counted as newly certified program completion. User application replay/reference validation, HTTP, cleanup protection BUG-014 and other NK-MSG-002 gates remain incomplete.",
        "redaction": "Copied hash-verified sanitized JUnit metadata only; no properties, stdout, provider text, secrets or master content.",
    })
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": args.run_id, "coordinatorTests": len(methods), "replacementTests": len(replacement_methods), "boundTests": len(bound_methods), "status": "REGRESSION_SLICE_PASS"}))


if __name__ == "__main__":
    main()
