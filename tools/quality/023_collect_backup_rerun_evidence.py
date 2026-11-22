#!/usr/bin/env python3
"""SSC-054/PG-D-145: backup success-history index PT, not a backup artifact certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root

CLASS = "dev.codex.schubert.nk.api.maintenance.BackupRerunBoundaryTest"
METHODS = ("sameDayBackupReruns", "ordinarySuccessStillUnique", "attemptAndDateBoundaries",
           "failureAndLatestSuccessHistory", "transactionRollbackAndMigration",
           "concurrentSuccessAndAttemptConflicts", "cleanupGatesWithRepeatedBackups", "catalogAndPrivileges")


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [c.get("name") for c in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "8"
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or len(names) != 8 or set(names) != set(METHODS)
            or any(c.get("classname") != CLASS or len(c) for c in cases)):
        raise ValueError("missing or nonpassing backup rerun tests")
    return {f"PT-DB-INBOX-{i:03}": CLASS + "#" + name for i, name in enumerate(METHODS, 233)}


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
    evidence = evidence_output_root(repo) / "004_NK-DAT-001/evidence/backup-rerun"
    evidence.mkdir(parents=True, exist_ok=True)
    suite = ET.Element("testsuite", name="NK-DAT-001-backup-rerun", tests="8", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS, name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/resources/db/migration" / name for name in
               ("V004__indexes_and_initial_data.sql", "V017__backup_rerun_success_history.sql")]
    sources += [repo / "src/schubert-nk-api/src/test/java" / (CLASS.replace(".", "/") + ".java")]
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-DAT-001", "scopeResult": "PASS_BACKUP_HISTORY_CONSTRAINT_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "javaCoverage": verified["modules"]["api"]["coverage"], "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "sqlCoverage": {"basis": "053/PT233..240 independent SQL predicate/constraint matrix, not JaCoCo",
                        "cases": ["both backup steps / other steps / lookalikes", "SUCCESS / all4 other statuses / NULL / unknown",
                                  "attempt1/99/0/100/duplicate and another date", "old SUCCESS history retained / later failure",
                                  "V004 counterexample23505 / V017 success / rollback / Flyway validate",
                                  "16 independent attempts / duplicate-attempt and ordinary-success races",
                                  "all8 cleanup gates and private Inbox helper still reject absent/other-run/unfinished backups"]},
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json", "fullReactorManifestSha256": digest(full),
        "related": ["SSC-054", "PG-D-145", "BUG-138", "BUG-139", "YKT-108", "YKT-109", "BUG-014", "YKT-012"],
        "fixture": "Isolated PostgreSQL18.6 with production Flyway; public UUID/date/status/counts only. No deployed DB or dump.",
        "oracle": "UI251 section11 permits another successful backup while retaining the prior success. Only BACKUP_DB/CONFIG are excepted from the day/step success unique index. Attempt1..99/day-step-attempt uniqueness, ordinary success uniqueness, grant/ownership, rollback and same-run/day/finished2step backup gates remain unchanged.",
        "limitations": "No parent BatchRunRepository, fixed-run persistence, real backup generation, latest directory/manifest/hash verification, OS flock/inactive gate, actual NK CHR or IT/ST is certified.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources],
    })
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)} for p in sorted(evidence.rglob("*"))
                         if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": 8, "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
