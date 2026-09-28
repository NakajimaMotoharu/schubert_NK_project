#!/usr/bin/env python3
"""Selected PG338 parent stop-pass evidence; actual fixed Units remain unstarted."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET = ROOT / "src/schubert-nk-batch/target"
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG338-morning-stop-pass"
LOG = pathlib.Path("/tmp/pg338-mpass-clean-fixed.log")
TESTS = {
    "MorningStopPassTest": 9,
    "MorningUnitTerminalsTest": 5,
    "MaintenanceUnitStopClientTest": 11,
    "MaintenanceUnitTerminationTest": 9,
    "MorningRootScopeTest": 6,
}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MorningStopPass.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningStopPassTest.java",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("d068d94e4")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "Tests run: 40, Failures: 0, Errors: 0, Skipped: 0" in log
    assert "BugInstance size is 0" in log and "BUILD SUCCESS" in log
    for folder in ("junit", "coverage", "static"):
        (OUT / folder).mkdir(parents=True, exist_ok=False)
    for name, count in TESTS.items():
        matches = list((TARGET / "surefire-reports").glob(f"TEST-*.{name}.xml"))
        assert len(matches) == 1
        source = matches[0]
        suite = ET.parse(source).getroot()
        cases = suite.findall("testcase")
        assert len(cases) == count == int(suite.get("tests", "-1"))
        assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        assert all(not list(case) or all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
        safe = ET.Element("testsuite", {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")})
        for case in cases:
            ET.SubElement(safe, "testcase", {key: case.get(key) for key in ("name", "classname", "time")})
        ET.indent(safe)
        ET.ElementTree(safe).write(OUT / "junit" / source.name, encoding="utf-8", xml_declaration=True)
    report = ET.parse(TARGET / "site/jacoco/jacoco.xml").getroot()
    coverage = {}
    for klass in report.iter("class"):
        if not klass.get("name", "").endswith("/MorningStopPass"):
            continue
        coverage = {item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))} for item in klass.findall("counter") if item.get("type") in ("LINE", "BRANCH", "METHOD", "CLASS")}
    assert set(coverage) == {"LINE", "BRANCH", "METHOD", "CLASS"}
    assert coverage["CLASS"]["missed"] == 0 and coverage["BRANCH"]["missed"] == 1
    emit(OUT / "coverage" / "morning-stop-pass.json", coverage)
    spot = ET.parse(TARGET / "spotbugsXml.xml").getroot()
    assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
    emit(OUT / "static" / "batch.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG338-morning-stop-pass", "formal": False, "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; JaCoCo0.8.15; SpotBugs4.10.4.0; no real fixed-eight stop",
        "command": "Batch -Dtest=MorningStopPassTest,MorningUnitTerminalsTest,MaintenanceUnitStopClientTest,MaintenanceUnitTerminationTest,MorningRootScopeTest clean test SpotBugs:check JaCoCo:report",
        "exitCode": 0,
        "input": "fixed eight ordered stop clients, whole-Unit terminal, UNKNOWN reaping/concurrency/interruption, nonzero and null/wrong actor",
        "expected": "40 selected PT F/E/S0/static0; UNKNOWN does not return from held parent scope; no startup authority",
        "actual": "40 PT F/E/S0/static0; stop-pass native factory branch/line/method still uncovered",
        "testIds": [f"PT-OPS-MPASS{n:03d}" for n in range(1, 10)],
        "counts": TESTS, "coverage": coverage, "coverageSourceSha256": sha(TARGET / "site/jacoco/jacoco.xml"),
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLogs": [{"path": str(LOG), "sha256": sha(LOG)}],
        "bugs": [], "ssc": ["SSC-100", "SSC-101", "SSC-102"],
        "limitations": ["ProcessBuilder.start failure before handle and native real Unit stop still unaccepted", "No A/current invalidation, Artemis journal, backup/Cleanup, permit, R2/R3", "JUnit suite/case metadata only; raw properties/output omitted"],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(TESTS.values()), "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}))


if __name__ == "__main__":
    main()
