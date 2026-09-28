#!/usr/bin/env python3
"""Selected PG335 child-stop evidence only; does not certify native Cleanup success."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = "a1898417f"
RUN = "PG335-selected"
TARGET = ROOT / "src/schubert-nk-batch/target"
OUTPUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional" / RUN
TESTS = {
    "RootStartupContextTest": 9,
    "MaintenanceUnitTerminationTest": 9,
    "CleanupProcessMainTest": 4,
    "CleanupPreflightTest": 5,
    "CleanupNativePreflightTest": 4,
}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CleanupNativePreflight.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitTermination.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CleanupNativePreflightTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitTerminationTest.java",
)
LOG = pathlib.Path("/tmp/pg335-final-selected.log")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUTPUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith(SOURCE)
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "Tests run: 31, Failures: 0, Errors: 0, Skipped: 0" in log
    assert "BugInstance size is 0" in log and "BUILD SUCCESS" in log
    for folder in ("junit", "coverage", "static", "logs"):
        (OUTPUT / folder).mkdir(parents=True, exist_ok=False)
    for name, count in TESTS.items():
        source = next((TARGET / "surefire-reports").glob(f"TEST-*.{name}.xml"))
        suite = ET.parse(source).getroot()
        cases = suite.findall("testcase")
        assert len(cases) == count and int(suite.get("tests", "-1")) == count
        assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        assert all(child.tag in ("system-out", "system-err") for case in cases for child in case)
        sanitized = ET.Element(
            "testsuite",
            {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")},
        )
        for case in cases:
            ET.SubElement(sanitized, "testcase", {key: case.get(key) for key in ("name", "classname", "time")})
        ET.indent(sanitized)
        ET.ElementTree(sanitized).write(OUTPUT / "junit" / source.name, encoding="utf-8", xml_declaration=True)

    jacoco = TARGET / "site/jacoco/jacoco.xml"
    report = ET.parse(jacoco).getroot()
    coverage = {}
    for klass in report.iter("class"):
        short = klass.get("name", "").split("/")[-1]
        if short not in ("MaintenanceUnitTermination", "CleanupNativePreflight"):
            continue
        coverage[short] = {
            item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))}
            for item in klass.findall("counter")
            if item.get("type") in ("LINE", "BRANCH", "METHOD", "CLASS")
        }
    assert set(coverage) == {"MaintenanceUnitTermination", "CleanupNativePreflight"}
    assert all(value["missed"] == 0 for value in coverage["MaintenanceUnitTermination"].values())
    assert coverage["CleanupNativePreflight"]["LINE"]["missed"] > 0
    write(OUTPUT / "coverage/changed-classes.json", coverage)
    spot = ET.parse(TARGET / "spotbugsXml.xml").getroot()
    assert not spot.findall("BugInstance")
    assert int(spot.find("Errors").get("errors", "-1")) == 0
    write(OUTPUT / "static/batch.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    write(
        OUTPUT / "logs/bug313-red-green.json",
        {
            "bug": "BUG-313",
            "initial": "Known StopGateException escaped fixed Cleanup exit mapping; code review, no Unit launch",
            "final": "NCLEAN005 fixed redacted IOException, then CMAIN003 exit30; selected 31 PT pass",
        },
    )
    files = [
        {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
        for path in sorted(OUTPUT.rglob("*"))
        if path.is_file()
    ]
    manifest = {
        "id": RUN,
        "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation",
        "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; JaCoCo0.8.15; SpotBugs4.10.4.0; native root Unit not started",
        "command": "Batch selected MaintenanceUnitTerminationTest,RootStartupContextTest,CleanupNativePreflightTest,CleanupProcessMainTest,CleanupPreflightTest test SpotBugs:check JaCoCo:report (no clean)",
        "exitCode": 0,
        "input": "CLEANUP actor + WEB/API only, ordered two-unit stop read, busy/not-found/null/known/unknown, parent regression",
        "expected": "31 PT F/E/S0, Batch static0, MaintenanceUnitTermination four JaCoCo counters missed0; no successful Cleanup",
        "actual": "31 PT F/E/S0, Batch static0, whole-Unit observer four counters missed0; Native preflight coverage incomplete",
        "counts": TESTS,
        "coverage": coverage,
        "coverageSourceSha256": digest(jacoco),
        "sourceHashes": [{"path": path, "sha256": digest(ROOT / path)} for path in SOURCES],
        "externalLogs": [{"path": str(LOG), "sha256": digest(LOG)}],
        "bugs": ["BUG-313"],
        "ykt": ["YKT-246"],
        "ssc": ["SSC-104"],
        "limitations": [
            "No clean/full Production same-source certification; native child Unit/root success unexecuted",
            "CleanupNativePreflight remains below Java four-metric 100%; no DELETE/parent M/A/transfer",
            "JUnit XML includes suite/case metadata only; no properties, output, raw state or secret",
        ],
        "files": files,
    }
    write(OUTPUT / "manifest.json", manifest)
    assert all(digest(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"run": RUN, "tests": sum(TESTS.values()), "files": len(files), "sha256": digest(OUTPUT / "manifest.json")}))


if __name__ == "__main__":
    main()
