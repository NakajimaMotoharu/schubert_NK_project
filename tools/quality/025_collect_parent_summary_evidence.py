#!/usr/bin/env python3
"""SSC049/PG162: bounded parent summary observation, not a child termination certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root

CLASS = "dev.codex.schubert.nk.api.maintenance.InspectionParentBoundaryTest"
METHODS = ("summaryStatesAndCounts", "identityAndTimeBoundaries", "parentLockNamespaces",
           "roleAndCatalog", "freshReadAndRollback", "concurrentOwners",
           "noMutationOrPrivateProjection", "appendOnlyMigration")
TRACES = {"PT-DB-INBOX-251-states.txt": (
    b"absent=[]\nopen=[0, 0, 0, false]\nemptyEnd=[0, 0, 0, true]\n"
    b"mixedEnd=[9, 5, 4, true]\nmaxEnd=[9223372036854775807, 9223372036854775806, 1, true]\n")}


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [c.get("name") for c in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "8"
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or len(names) != 8 or len(set(names)) != 8 or set(names) != set(METHODS)
            or any(c.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in c) for c in cases)):
        raise ValueError("missing or nonpassing parent summary SQL tests")
    return {f"PT-DB-INBOX-{i:03}": CLASS + "#" + name for i, name in enumerate(METHODS, 251)}


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("missing, extra or invalid independent parent summary trace")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        raise SystemExit("matching successful full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    trace_root = target / "parent-summary-traces"
    traces = {str(p.relative_to(trace_root)): p.read_bytes() for p in trace_root.rglob("*") if p.is_file()}
    validate_traces(traces)
    evidence = evidence_output_root(repo) / "004_NK-DAT-001/evidence/parent-summary"
    audit = repo / "evidence/01_PT/004_NK-DAT-001/061_NK-DAT-001_migration一覧横展開.md"
    (evidence / "logs").mkdir(parents=True, exist_ok=True)
    (evidence / "logs/BUG-175-YKT-136.md").write_bytes(audit.read_bytes())
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    suite = ET.Element("testsuite", name="NK-DAT-001-parent-summary", tests="8", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS, name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/resources/db/migration/V019__parent_inbox_inspection_summary.sql",
               repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/MigrationInventory.java",
               repo / "src/schubert-nk-api/src/test/java" / (CLASS.replace(".", "/") + ".java")]
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-DAT-001", "scopeResult": "PASS_PARENT_INSPECTION_SUMMARY_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "javaCoverage": verified["modules"]["api"]["coverage"], "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "sqlCoverage": {"basis": "059/PT251..258 independent SQL predicates/roles/locks/temporal and state matrix; not JaCoCo",
                        "cases": ["0row/open/END/zero/mixed/MAX 4column literal",
                                  "NULL/infinity/0001..9999/1582/UTC/JST/NewYork/identity",
                                  "self exclusive bigint/shared/two-int/other backend and unchanged lock",
                                  "batch-only execute/owner/definer/search_path/UTC/no base grants",
                                  "fresh commit/rollback/uncommitted/parallel owners",
                                  "all table and index snapshot unchanged/no row lock/no backup prerequisite",
                                  "18 frozen migration hashes/22 current inventory/repeat validate (V022 PG246 addition)"]},
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json", "fullReactorManifestSha256": digest(full),
        "related": ["SSC-049", "PG-D-162", "QA-046", "UIC-006", "BUG-175", "YKT-136"],
        "fixture": "Isolated PostgreSQL18.6/Flyway; public synthetic UUID/counts and independent SQL literals.",
        "oracle": "Absent progress stays absent; same-run cutoff exact; inspected/deleted/protected/END observed once without DML or private projection. Independent count vectors and all-role/lock/transaction/time boundaries.",
        "limitations": "No actual fresh child/unit termination, OS-lock continuity, backup artifacts, parent steps, actual NK CHR or IT/ST is certified.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources]})
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)} for p in sorted(evidence.rglob("*"))
                         if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": 8, "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
