#!/usr/bin/env python3
"""Publish selected PG336 Morning-root evidence without certifying native parent startup."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG336-morning-root"
TARGET = ROOT / "src/schubert-nk-batch/target"
LOG = pathlib.Path("/tmp/pg336-mroot-clean-selected.log")
TESTS = {
    "MorningRootScopeTest": 6,
    "MaintenanceFileLockTest": 8,
    "RootStartupContextTest": 9,
    "MaintenanceUnitStopClientTest": 11,
    "MaintenanceUnitStopPolicyTest": 7,
}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningRootScope.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningRootScopeTest.java",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("587fb88a0")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "Tests run: 41, Failures: 0, Errors: 0, Skipped: 0" in log
    assert "BugInstance size is 0" in log and "BUILD SUCCESS" in log
    for folder in ("junit", "coverage", "static"):
        (OUT / folder).mkdir(parents=True, exist_ok=False)
    for name, expected in TESTS.items():
        candidates = list((TARGET / "surefire-reports").glob(f"TEST-*.{name}.xml"))
        assert len(candidates) == 1
        suite = ET.parse(candidates[0]).getroot()
        cases = suite.findall("testcase")
        assert len(cases) == expected == int(suite.get("tests", "-1"))
        assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        assert all(not list(case) or all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
        safe = ET.Element("testsuite", {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")})
        for case in cases:
            ET.SubElement(safe, "testcase", {key: case.get(key) for key in ("name", "classname", "time")})
        ET.indent(safe)
        ET.ElementTree(safe).write(OUT / "junit" / candidates[0].name, encoding="utf-8", xml_declaration=True)
    report = ET.parse(TARGET / "site/jacoco/jacoco.xml").getroot()
    coverage = {}
    for klass in report.iter("class"):
        if not klass.get("name", "").endswith("/MorningRootScope"):
            continue
        coverage = {item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))} for item in klass.findall("counter") if item.get("type") in ("LINE", "BRANCH", "METHOD", "CLASS")}
    assert set(coverage) == {"LINE", "BRANCH", "METHOD", "CLASS"}
    assert coverage["BRANCH"]["missed"] == 0 and coverage["CLASS"]["missed"] == 0
    assert coverage["LINE"]["missed"] > 0 and coverage["METHOD"]["missed"] > 0
    emit(OUT / "coverage" / "morning-root.json", coverage)
    spot = ET.parse(TARGET / "spotbugsXml.xml").getroot()
    assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
    emit(OUT / "static" / "batch.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG336-morning-root", "formal": False, "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; JaCoCo0.8.15; SpotBugs4.10.4.0; no genuine Morning Unit",
        "command": "Batch -Dtest=MorningRootScopeTest,MaintenanceFileLockTest,RootStartupContextTest,MaintenanceUnitStopClientTest,MaintenanceUnitStopPolicyTest clean test SpotBugs:check JaCoCo:report",
        "exitCode": 0,
        "input": "fixed MORNING root/M gate, eight-Unit policy, M contention, all root rechecks, null and downstream failure",
        "expected": "41 selected PT F/E/S0, Batch static0; no continuation before root/M/eight-policy; native parent remains unaccepted",
        "actual": "41 selected PT F/E/S0, Batch static0; package scope branch/class fully covered, native entry line/method incomplete",
        "testIds": ["PT-OPS-MROOT001", "PT-OPS-MROOT002", "PT-OPS-MROOT003", "PT-OPS-MROOT004", "PT-OPS-MROOT005", "PT-OPS-MROOT006"],
        "counts": TESTS, "coverage": coverage, "coverageSourceSha256": sha(TARGET / "site/jacoco/jacoco.xml"),
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLogs": [{"path": str(LOG), "sha256": sha(LOG)}],
        "bugs": [], "ssc": ["SSC-100", "SSC-101", "SSC-102"],
        "limitations": ["No real root/M/A or fixed eight Unit stop", "No UNKNOWN quarantine, backup, Cleanup success, permit, R2/R3", "JUnit suite/case metadata only; properties/output/raw credentials omitted"],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(TESTS.values()), "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}))


if __name__ == "__main__":
    main()
