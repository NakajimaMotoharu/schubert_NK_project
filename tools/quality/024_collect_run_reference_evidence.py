#!/usr/bin/env python3
"""SSC055/PG159: least-privilege run reference observation, never an original GC certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.api.maintenance.RunReferenceBoundaryTest"
METHODS = ("referenceCombinations", "identityConsistency", "temporalAndNullBoundaries", "lockOwnership",
           "roleAndCatalog", "transactionVisibility", "concurrentOwnership", "migrationAndReadOnlyHistory", "jdbcUtcVectors", "productionUtcBoundaryInventory")
TRACES = {"PT-DB-INBOX-241-combinations.txt": (
    b"0:[false, false, false, true]\n1:[true, false, false, true]\n"
    b"2:[false, true, false, true]\n3:[true, true, false, true]\n"
    b"4:[false, false, true, true]\n5:[true, false, true, true]\n"
    b"6:[false, true, true, true]\n7:[true, true, true, true]\n")}


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [c.get("name") for c in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "10"
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or len(names) != 10 or len(set(names)) != 10 or set(names) != set(METHODS)
            or any(c.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in c) for c in cases)):
        raise ValueError("missing or nonpassing run reference SQL tests")
    return {f"PT-DB-INBOX-{i:03}": CLASS + "#" + name for i, name in enumerate(METHODS, 241)}


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("missing, extra or invalid independent run reference trace")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    trace_root = target / "run-reference-traces"
    traces = {str(p.relative_to(trace_root)): p.read_bytes() for p in trace_root.rglob("*") if p.is_file()}
    validate_traces(traces)
    evidence = repo / "evidence/01_PT/004_NK-DAT-001/evidence/run-references"
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    suite = ET.Element("testsuite", name="NK-DAT-001-run-references", tests="10", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS, name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/resources/db/migration/V018__maintenance_run_references.sql",
               repo / "src/schubert-nk-api/src/test/java" / (CLASS.replace(".", "/") + ".java")]
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-DAT-001", "scopeResult": "PASS_RUN_REFERENCE_OBSERVATION_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "javaCoverage": verified["modules"]["api"]["coverage"], "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "sqlCoverage": {"basis": "055/057/PT241..250 independent predicate/role/lock/time matrix; not JaCoCo",
                        "cases": ["all8 reference combinations/all5 statuses and age/completion ignored",
                                  "all history dates and each progress cutoff/one microsecond/other run",
                                  "NULL/infinity/UTC0001..9999 and session timezone admission",
                                  "self exclusive bigint lock/shared/two-int/other backend/no lock",
                                  "batch only execute/catalog/unchanged base grants",
                                  "same/other TX uncommitted, committed, rollback, fresh reads and concurrency",
                                  "all17 prior migration hashes and read-only history preserved",
                                  "JDBC42 UTC literal/epoch/projection0001..9999/1582 gap/3 zones/SQL NULL",
                                  "23 production UTC targets/legacy JDBC time scan plus full program regressions"]},
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json", "fullReactorManifestSha256": digest(full),
        "related": ["SSC-055", "SSC-056", "PG-D-159", "PG-D-160", "BUG-167", "YKT-128", "BUG-163", "BUG-164", "BUG-165", "BUG-166", "YKT-127"],
        "fixture": "Isolated PostgreSQL18.6/Flyway; literal public UUID/time and four boolean projections. No deployed data.",
        "oracle": "All8 combinations independently enumerated; existing same-run rows always protect originals regardless of status/age. All history JST dates and each progress cutoff must match. No original backfill, DML or implicit lock/backup gate. SQL parameters are typed before function TimeZone; explicit UTC out-of-range values reject across UTC/JST/NewYork.",
        "limitations": "No OS/session lock continuity, parent admission, actual original retirement marker/400day GC, backup artifacts, actual NK CHR or IT/ST is certified.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources]})
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)} for p in sorted(evidence.rglob("*"))
                         if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": 10, "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
