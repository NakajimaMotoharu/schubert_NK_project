#!/usr/bin/env python3
"""Sanitize the PG335 six-module security regression; never certify the PG/PT gate."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG335-six-security"
MODULES = {
    "protocol": 80,
    "storage": 149,
    "bootstrap": 175,
    "api": 742,
    "web": 555,
    "batch": 626,
}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CleanupNativePreflight.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitTermination.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CleanupNativePreflightTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitTerminationTest.java",
)
VERIFY_LOG = pathlib.Path("/tmp/pg335-six-clean.log")
REGRESSION_LOG = pathlib.Path("/tmp/pg335-six-security-2.log")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("a1898417f")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    verification = VERIFY_LOG.read_text()
    regression = REGRESSION_LOG.read_text()
    assert "BUILD FAILURE" in verification and "schubert-nk-bootstrap: Coverage checks have not been met" in verification
    assert "BUILD SUCCESS" in regression
    assert regression.count("BugInstance size is 0") == 6
    assert sum(MODULES.values()) == 2327
    for folder in ("junit", "coverage", "static", "logs"):
        (OUT / folder).mkdir(parents=True, exist_ok=False)
    counters = {}
    suite_counts = {}
    for module, count in MODULES.items():
        target = ROOT / f"src/schubert-nk-{module}/target"
        junit = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        assert junit
        (OUT / "junit" / module).mkdir()
        actual = 0
        for source in junit:
            suite = ET.parse(source).getroot()
            assert suite.tag == "testsuite"
            assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
            cases = suite.findall("testcase")
            assert len(cases) == int(suite.get("tests", "-1"))
            assert all(not list(case) or all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
            safe = ET.Element("testsuite", {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")})
            for case in cases:
                ET.SubElement(safe, "testcase", {key: case.get(key) for key in ("name", "classname", "time")})
            ET.indent(safe)
            ET.ElementTree(safe).write(OUT / "junit" / module / source.name, encoding="utf-8", xml_declaration=True)
            actual += len(cases)
        assert actual == count
        suite_counts[module] = {"tests": actual, "suites": len(junit), "failures": 0, "errors": 0, "skipped": 0}
        report = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
        counter = {item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))} for item in report.findall("counter") if item.get("type") in ("LINE", "METHOD", "CLASS", "BRANCH")}
        assert set(counter) == {"LINE", "METHOD", "CLASS", "BRANCH"}
        counters[module] = counter
        spot = ET.parse(target / "spotbugsXml.xml").getroot()
        assert not spot.findall("BugInstance")
        assert int(spot.find("Errors").get("errors", "-1")) == 0
        emit(OUT / "static" / f"{module}.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    emit(OUT / "coverage" / "all-modules.json", counters)
    emit(OUT / "logs" / "run-summary.json", {"cleanVerify": "exit 1, Bootstrap JaCoCo 100% gate; API/Web/Batch not run", "securityRegression": "exit 0, 2327 PT F/E/S0; SpotBugs six modules 0; JaCoCo reports generated", "formal": False})
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG335-six-security", "formal": False, "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; JaCoCo0.8.15; SpotBugs4.10.4.0; Node24.19.0",
        "commands": ["Production6 clean verify (exit 1 at Bootstrap coverage)", "Production6 clean test com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check org.jacoco:jacoco-maven-plugin:0.8.15:report (exit 0)"],
        "input": "PG335 child WEB/API whole-Unit stop observation and shared root actor factory; existing six-module regression",
        "expected": "All PT F/E/S0 and static 0; four coverage counters each 100% for formal gate",
        "actual": "2327 PT F/E/S0 and six static 0, but Bootstrap and other coverage gaps; no real Unit/CHR acceptance",
        "suites": suite_counts, "coverage": counters,
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLogs": [{"path": str(path), "sha256": sha(path)} for path in (VERIFY_LOG, REGRESSION_LOG)],
        "bugs": ["BUG-313"], "ykt": ["YKT-246"], "ssc": ["SSC-104"],
        "limitations": ["Not formal same-source 100% coverage", "No genuine root Cleanup Unit success, parent M/A, DELETE, R2 or R3", "Sanitized JUnit contains only suite/case metadata; no properties, stdout, stack traces or secret"],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(item["tests"] for item in suite_counts.values()), "suites": sum(item["suites"] for item in suite_counts.values()), "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}))


if __name__ == "__main__":
    main()
