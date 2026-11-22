#!/usr/bin/env python3
"""SSC057/PG164: atomic non-Log cleanup counts; no whole-parent certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.api.maintenance.StepCleanupBoundaryTest"
METHODS = ("sevenKindAtomicCounts", "handleArgumentsAndIdentity", "backupLockAndRoleBoundary", "zeroChunkLockedRemainder", "retentionAndProtectedRows", "rollbackOverflowAndForeignKey", "typedProjectionAndNoBypass", "appendOnlyMigrationInventory",)
TRACES = {"PT-DB-INBOX-259-seven-kinds.txt": b"NOTIFICATIONS=1|1|0|1|1|false|OK\nQUESTIONS=1|1|0|1|1|false|OK\nSESSIONS=3|3|0|3|3|false|OK\nOUTBOX=2|2|0|2|2|false|OK\nBATCH_RUNS=1|1|0|1|1|false|OK\nINBOX_PROGRESS=1|1|0|2|2|false|OK\nLOG_PROGRESS=1|1|0|3|3|false|OK\n"}


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [c.get("name") for c in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "8"
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or len(names) != 8 or len(set(names)) != 8 or set(names) != set(METHODS)
            or any(c.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in c) for c in cases)):
        raise ValueError("missing or nonpassing atomic cleanup SQL tests")
    return {f"PT-DB-INBOX-{i:03}": CLASS + "#" + name for i, name in enumerate(METHODS, 259)}


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("missing, extra or invalid independent atomic cleanup trace")


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
    trace_root = target / "atomic-cleanup-traces"
    traces = {str(p.relative_to(trace_root)): p.read_bytes() for p in trace_root.rglob("*") if p.is_file()}
    validate_traces(traces)
    evidence = repo / "evidence/01_PT/004_NK-DAT-001/evidence/atomic-cleanup"
    audit = repo / "evidence/01_PT/017_NK-BAT-001/032_NK-BAT-001_cleanup証跡横展開.md"
    (evidence / "logs").mkdir(parents=True, exist_ok=True)
    (evidence / "logs/BUG-179-YKT-140.md").write_bytes(audit.read_bytes())
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    suite = ET.Element("testsuite", name="NK-DAT-001-atomic-cleanup", tests="8", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS, name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/resources/db/migration/V020__atomic_cleanup_step_counts.sql",
               repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/MigrationInventory.java",
               repo / "src/schubert-nk-api/src/test/resources/maintenance/step-cleanup-fixture.sql",
               repo / "src/schubert-nk-api/src/test/java" / (CLASS.replace(".", "/") + ".java")]
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-DAT-001", "scopeResult": "PASS_ATOMIC_NON_LOG_CLEANUP_SQL_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "javaCoverage": verified["modules"]["api"]["coverage"], "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "sqlCoverage": {"basis": "062/PT259..266 SS331 3.14 independent predicate, transaction, handle, lock, role and typed projection matrix; not JaCoCo",
                        "cases": ["7 closed kinds/10 table components/full handle/1000 bound", "strict retention and protected row/locked remainder never END", "backup-before-step lock/NULL unknown counts/batch-only execute", "DELETE and count atomic rollback/overflow/trigger/FK23503 question deferral", "typed seven-column projection/null/extra/invalid/guard rows", "19 frozen migration hashes/22 current SQL inventory/1 SCHEMA/repeat0"]},
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json", "fullReactorManifestSha256": digest(full),
        "related": ["SSC-057", "PG-D-164", "BUG-179", "YKT-140"],
        "fixture": "Isolated PostgreSQL18.6/Flyway; public synthetic UUID/counts and independent SQL literals.",
        "oracle": "Independent seven-kind totals 1/1/3/2/1/2/3 and per-call 1/1/3/2/1/1/1; existing retention unchanged. Read-only candidate remainder defeats SKIP LOCKED false END. Known totals only after full handle lock; DELETE plus stored count in one transaction.",
        "limitations": "No Log or request_inbox deletion bypass. Actual parent, child termination, OS-lock continuity, backup artifacts, actual NK CHR and IT/ST remain incomplete.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources]})
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)} for p in sorted(evidence.rglob("*"))
                         if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": 8, "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
