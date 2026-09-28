#!/usr/bin/env python3
"""Sanitized PG339 candidate PT and external fail-closed evidence."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET = ROOT / "src/schubert-nk-batch/target"
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG339-morning-candidate"
LOG = pathlib.Path("/tmp/pg339-mmain-clean-fixed.log")
ARCHIVE = pathlib.Path("/home/mini/codex/project1/work/pgpt-vm/private/pg339-RTk31C.tar")
TESTS = {
    "MorningProcessMainTest": 5,
    "MorningServiceUnitTest": 3,
    "MorningRootScopeTest": 6,
    "MaintenanceUnitStopPolicyTest": 7,
}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningProcessMain.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningProcessMainTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceUnitTest.java",
    "src/deployment/systemd/schubert-nk-morning-controller.service.template",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("3daf286ee")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "Tests run: 21, Failures: 0, Errors: 0, Skipped: 0" in log
    assert "BugInstance size is 0" in log and "BUILD SUCCESS" in log
    assert sha(ROOT / SOURCES[-1]) == "5debc9401e3f3db636709f76d5496228130792e1de1f902248d88992cabd31ec"
    assert sha(ARCHIVE) == "739fd661af6245da8847731685f037d73b244d619beabd812a4167396b02c3fe"
    assert pathlib.Path("/tmp/pg339-host.stdout").stat().st_size == 0
    assert pathlib.Path("/tmp/pg339-host.stderr").stat().st_size == 0
    for folder in ("junit", "coverage", "static"):
        (OUT / folder).mkdir(parents=True, exist_ok=False)
    for name, count in TESTS.items():
        matches = list((TARGET / "surefire-reports").glob(f"TEST-*.{name}.xml"))
        assert len(matches) == 1
        suite = ET.parse(matches[0]).getroot()
        cases = suite.findall("testcase")
        assert len(cases) == count == int(suite.get("tests", "-1"))
        assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        assert all(not list(case) or all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
        safe = ET.Element("testsuite", {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")})
        for case in cases:
            ET.SubElement(safe, "testcase", {key: case.get(key) for key in ("name", "classname", "time")})
        ET.indent(safe)
        ET.ElementTree(safe).write(OUT / "junit" / matches[0].name, encoding="utf-8", xml_declaration=True)
    report = ET.parse(TARGET / "site/jacoco/jacoco.xml").getroot()
    coverage = {}
    for klass in report.iter("class"):
        if klass.get("name", "").endswith("/MorningProcessMain"):
            coverage = {item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))} for item in klass.findall("counter") if item.get("type") in ("LINE", "BRANCH", "METHOD", "CLASS")}
    assert set(coverage) == {"LINE", "BRANCH", "METHOD", "CLASS"}
    emit(OUT / "coverage" / "morning-process-main.json", coverage)
    spot = ET.parse(TARGET / "spotbugsXml.xml").getroot()
    assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
    emit(OUT / "static" / "batch.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG339-morning-candidate", "formal": False, "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; isolated Ubuntu VM; JDK25.0.4; Maven3.9.12; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Batch -Dtest=MorningProcessMainTest,MorningServiceUnitTest,MorningRootScopeTest,MaintenanceUnitStopPolicyTest clean test SpotBugs:check JaCoCo:report",
        "exitCode": 0,
        "input": "fail-closed Morning external main; no argv; read-only root admission; candidate unit not installed; existing PG323 test-only unit preserved",
        "expected": "21 selected PT F/E/S0/static0; external host main exit30 with output0; candidate unit syntax valid; no Production acceptance",
        "actual": "21 PT F/E/S0/static0; host Java main exit30/output0; isolated VM systemd-analyze verify exit0; exact Morning unit loaded inactive/PID0 but pre-existing PG323 test-only ExecStart, not PG339",
        "testIds": [f"PT-OPS-MMAIN{n:03d}" for n in range(1, 6)] + [f"PT-OPS-MUNIT{n:03d}" for n in range(1, 4)],
        "counts": TESTS, "coverage": coverage, "coverageSourceSha256": sha(TARGET / "site/jacoco/jacoco.xml"),
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLogs": [{"path": str(LOG), "sha256": sha(LOG)}],
        "externalChecks": {"hostExitCode": 30, "hostStdoutBytes": 0, "hostStderrBytes": 0, "vmUnitVerifyExitCode": 0,
                           "vmUnitSha256": sha(ROOT / SOURCES[-1]), "vmPackageSha256": sha(ARCHIVE),
                           "vmExistingUnit": "schubert-nk-morning-controller.service loaded/inactive/MainPID0; PG323 test-only oneshot; untouched"},
        "bugs": ["BUG-314"], "ykt": ["YKT-247"], "ssc": ["SSC-100", "SSC-101", "SSC-102"],
        "limitations": ["Unit syntax/host smoke are not genuine root Production Morning startup", "Existing PG323 Unit not overwritten or reconfigured", "No M/A/current invalidation, fixed-eight stop, journal, backup/Cleanup, permit, R2/R3", "JUnit suite/case metadata only; raw properties/output omitted"],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(TESTS.values()), "files": len(files), "coverage": coverage, "manifestSha256": sha(OUT / "manifest.json")}))


if __name__ == "__main__":
    main()
