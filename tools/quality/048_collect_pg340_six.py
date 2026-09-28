#!/usr/bin/env python3
"""Sanitize PG340 security regression; never certify the formal 100% PT gate."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG340-six-security"
MODULES = {"protocol": 80, "storage": 149, "bootstrap": 175, "api": 742, "web": 555, "batch": 655}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClientTest.java",
)
FAILED_LOG = pathlib.Path("/tmp/pg340-six-clean.log")
PASS_LOG = pathlib.Path("/tmp/pg340-six-clean-node.log")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("42d419534")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    failed, passed = FAILED_LOG.read_text(), PASS_LOG.read_text()
    assert "BUILD FAILURE" in failed and 'Cannot run program "node"' in failed
    assert "Schubert NK Batch .................................. SKIPPED" in failed
    assert "BUILD SUCCESS" in passed and passed.count("BugInstance size is 0") == 6
    assert sum(MODULES.values()) == 2356
    for folder in ("junit", "coverage", "static", "logs"):
        (OUT / folder).mkdir(parents=True, exist_ok=False)
    counters, suite_counts = {}, {}
    for module, count in MODULES.items():
        target = ROOT / f"src/schubert-nk-{module}/target"
        junit = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        assert junit
        (OUT / "junit" / module).mkdir()
        actual = 0
        for source in junit:
            suite = ET.parse(source).getroot()
            cases = suite.findall("testcase")
            assert suite.tag == "testsuite" and len(cases) == int(suite.get("tests", "-1"))
            assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
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
        assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
        emit(OUT / "static" / f"{module}.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    assert sum(item["suites"] for item in suite_counts.values()) == 347
    batch_report = ET.parse(ROOT / "src/schubert-nk-batch/target/site/jacoco/jacoco.xml").getroot()
    changed_coverage = {}
    for klass in batch_report.iter("class"):
        name = klass.get("name", "")
        if name.endswith("/MaintenanceUnitStopClient") or name.endswith("MaintenanceUnitStopClient$Attempt"):
            changed_coverage[name.rsplit("/", 1)[-1]] = {item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))} for item in klass.findall("counter") if item.get("type") in ("LINE", "METHOD", "CLASS", "BRANCH")}
    assert len(changed_coverage) == 2
    assert all(all(item["missed"] == 0 for item in entry.values()) for entry in changed_coverage.values())
    emit(OUT / "coverage" / "all-modules.json", counters)
    emit(OUT / "coverage" / "changed-stop-client.json", changed_coverage)
    emit(OUT / "logs" / "run-summary.json", {"firstAttempt": "exit1: Web Node missing, Web E2 and Batch not run", "correctedEnvironment": "exit0: 2356 PT/347 suite F/E/S0, six static0; all-module coverage below 100%", "formal": False})
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG340-six-security", "formal": False, "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; Node24.19.0; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "commands": ["Production6 clean test SpotBugs:check JaCoCo:report without Node PATH (exit1)", "Same-source Production6 clean test SpotBugs:check JaCoCo:report with fixed Node PATH and -Dnk.pt.node (exit0)"],
        "input": "BUG315 post-start unknown ownership; existing six-module security regression",
        "expected": "Every PT F/E/S0/static0, changed stop client four counters missed0; formal bundle coverage four counters missed0 separately required",
        "actual": "2356 PT/347 suite F/E/S0, six static0 and changed stop client four counters missed0; bundle coverage not 100%; no genuine Morning/Unit/CHR acceptance",
        "suites": suite_counts, "coverage": counters, "changedCoverage": changed_coverage,
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLogs": [{"path": str(path), "sha256": sha(path)} for path in (FAILED_LOG, PASS_LOG)],
        "bugs": ["BUG-315"], "ykt": ["YKT-248"], "ssc": ["SSC-102", "SSC-105"],
        "limitations": ["Handle-less UNKNOWN cannot reap itself; systemd hard-timeout/M protection remains unaccepted", "Not formal same-source 100% coverage", "No actual fixed-eight stop, parent A/current INVALID, R2/R3", "Sanitized JUnit has suite/case metadata only; no raw properties/stdout/stack traces"],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(item["tests"] for item in suite_counts.values()), "suites": sum(item["suites"] for item in suite_counts.values()), "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}))


if __name__ == "__main__":
    main()
