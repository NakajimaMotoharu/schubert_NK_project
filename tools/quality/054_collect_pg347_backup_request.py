#!/usr/bin/env python3
"""Collect a sanitized, immutable Batch-only PG347 run at the saved source commit."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG347-backup-request"
LOG = Path("/tmp/pgpt-pg347-batch.log")
TARGET = ROOT / "src/schubert-nk-batch/target"
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBackupPreparation.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupPreparationTest.java",
    "evidence/01_PT/018_NK-OPS-001/217_NK-OPS-001_Morning_backup_request_単体テスト仕様書.md",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def counters(node):
    result = {
        counter.get("type"): {
            "missed": int(counter.get("missed")),
            "covered": int(counter.get("covered")),
        }
        for counter in node.findall("counter")
        if counter.get("type") in {"BRANCH", "LINE", "METHOD", "CLASS"}
    }
    assert set(result) == {"BRANCH", "LINE", "METHOD", "CLASS"}
    return result


def main():
    assert not OUT.exists(), "Refuse to replace saved evidence"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("775421d8e")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "Tests run: 703, Failures: 0, Errors: 0, Skipped: 0" in log
    assert "BugInstance size is 0" in log and "BUILD SUCCESS" in log
    for directory in ("junit", "coverage", "static"):
        (OUT / directory).mkdir(parents=True, exist_ok=False)
    reports = sorted((TARGET / "surefire-reports").glob("TEST-*.xml"))
    assert reports
    count = 0
    for path in reports:
        suite = ET.parse(path).getroot()
        cases = suite.findall("testcase")
        assert suite.tag == "testsuite" and len(cases) == int(suite.get("tests", "-1"))
        assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        assert all(all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
        safe = ET.Element("testsuite", {key: suite.get(key) for key in
                         ("name", "tests", "failures", "errors", "skipped", "time")})
        for case in cases:
            ET.SubElement(safe, "testcase", {key: case.get(key) for key in
                                              ("name", "classname", "time")})
        ET.indent(safe)
        ET.ElementTree(safe).write(OUT / "junit" / path.name, encoding="utf-8", xml_declaration=True)
        count += len(cases)
    assert count == 703
    report = ET.parse(TARGET / "site/jacoco/jacoco.xml").getroot()
    all_coverage = counters(report)
    changed = {node.get("name"): counters(node) for node in report.iter("class")
               if node.get("name", "").endswith("/MorningBackupPreparation")}
    assert len(changed) == 1
    assert all(value["missed"] == 0 for value in next(iter(changed.values())).values())
    write(OUT / "coverage" / "batch.json", all_coverage)
    write(OUT / "coverage" / "changed-class.json", changed)
    spot = ET.parse(TARGET / "spotbugsXml.xml").getroot()
    assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
    write(OUT / "static" / "batch.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    files = [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
             for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG347-backup-request", "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; Node24.19.0; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Batch clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check",
        "exitCode": 0,
        "input": "same-run original, committed backup begins, root nonsecret worker request",
        "expected": "703 PT F/E/S0; static0; new class four coverage counters missed0",
        "actual": "703 PT F/E/S0; static0; new class counters missed0; external worker not connected",
        "testIds": [f"PT-OPS-MBPREP{i:03d}" for i in range(1, 7)],
        "suites": {"tests": count, "suites": len(reports), "failures": 0, "errors": 0, "skipped": 0},
        "coverage": all_coverage, "changedCoverage": changed,
        "sourceHashes": [{"path": path, "sha256": digest(ROOT / path)} for path in SOURCES],
        "externalLog": {"path": str(LOG), "sha256": digest(LOG)},
        "bugs": ["BUG-315"], "ykt": ["YKT-248", "YKT-250"],
        "ssc": ["SSC-055", "SSC-092", "SSC-094", "SSC-104", "SSC-105"],
        "limitations": [
            "No native parent caller, backup worker, actual Unit, archive or DB success acceptance",
            "Whole Production four-counter 100% gate remains unmet",
            "JUnit properties/stdout/stderr/failure payload omitted; no raw secrets or session IDs",
        ],
        "files": files,
    }
    write(OUT / "manifest.json", manifest)
    assert all(digest(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": count, "suites": len(reports), "files": len(files),
                      "manifestSha256": digest(OUT / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
