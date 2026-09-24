#!/usr/bin/env python3
"""PG245/SSC077: same-source evidence for Expiry batch audit DDL only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

CLASS = "dev.codex.schubert.nk.api.database.DatabaseMigrationTest"
METHODS = {
    "PT-DB-016": "expiryBatchRunAuditIsCompleteAndOtherStepsRemainUnchanged",
    "PT-DB-017": "legacySuccessfulExpiryAuditIsNotGuessedOrPartiallyMigrated",
}
ORACLE = (
    "PT-DB-016|V021 applied 21/21|expiry three columns timestamptz,bigint,bigint|"
    "SUCCESS before-after=success=target and failure=0|other step all null|"
    "partial/null/infinity/negative/reverse/mismatched 23514|batch allow; web-session deny\n"
    "PT-DB-017|V001..020 plus synthetic old CLEAN_EXPIRY SUCCESS|V021 abort|"
    "history remains 20|new columns remain 0|no inferred backfill\n"
).encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "17"
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != 17 or len(set(names)) != 17
            or not set(METHODS.values()).issubset(names)
            or any(case.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case)
                   for case in cases)):
        raise ValueError("missing or nonpassing Expiry database tests")
    return {test_id: CLASS + "#" + name for test_id, name in METHODS.items()}


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
    xml = repo / "src/schubert-nk-api/target/surefire-reports" / ("TEST-" + CLASS + ".xml")
    methods = validate_suite(ET.parse(xml).getroot())
    evidence = repo / "evidence/01_PT/004_NK-DAT-001/evidence/expiry-audit"
    (evidence / "input").mkdir(parents=True, exist_ok=True)
    (evidence / "output").mkdir(parents=True, exist_ok=True)
    (evidence / "input/independent-oracle.txt").write_bytes(ORACLE)
    result = ET.Element("testsuite", name="NK-DAT-001-expiry-audit", tests="2", failures="0",
                        errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(result, "testcase", id=test_id, classname=CLASS,
                      name=method.split("#")[1], result="PASS")
    ET.ElementTree(result).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/resources/db/migration/V021__expiry_batch_run_audit.sql",
               repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/DatabaseMigrationTest.java",
               repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/MigrationInventory.java"]
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-DAT-001", "scopeResult": "PASS_EXPIRY_AUDIT_DDL_ONLY",
        "programComplete": False, "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "inputAndExpected": ORACLE.decode(),
        "actual": "Validated JUnit method-level PASS and SQLSTATE/catalog/legacy rollback assertions in the fixed source.",
        "javaCoverage": verified["modules"]["api"]["coverage"],
        "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "sqlCoverage": "064/PT-DB-016..017 independent schema, CHECK, role, legacy migration matrix; not Java JaCoCo",
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full),
        "related": ["SSC-077", "BUG-237", "YKT-188"],
        "limitations": "No borrowed parent transaction, startup policy, same-run uncertain commit, actual NK CHR or IT/ST certificate.",
        "sourceFiles": [{"path": str(path.relative_to(repo)), "sha256": digest(path)} for path in sources],
    })
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (evidence / "checksums.sha256").write_text("".join(
        digest(path) + "  " + str(path.relative_to(evidence)) + "\n"
        for path in sorted(evidence.rglob("*")) if path.is_file()
        and path.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": 2, "scopeResult": manifest["scopeResult"],
                      "programComplete": False}))


if __name__ == "__main__":
    main()
