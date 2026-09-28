#!/usr/bin/env python3
"""Collect sanitized PG344 current-INVALID regression bound to one committed source."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG344-morning-invalid"
MODULES = {
    "protocol": 80,
    "storage": 149,
    "bootstrap": 175,
    "api": 742,
    "web": 555,
    "batch": 682,
}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningCurrentInvalidation.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningControlScope.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningCurrentInvalidationTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningControlScopeTest.java",
)
LOG = pathlib.Path("/tmp/pgpt-pg344-six-final.log")
COUNTERS = ("LINE", "METHOD", "CLASS", "BRANCH")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, payload):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def counters(element):
    result = {
        entry.get("type"): {
            "missed": int(entry.get("missed")),
            "covered": int(entry.get("covered")),
        }
        for entry in element.findall("counter")
        if entry.get("type") in COUNTERS
    }
    assert set(result) == set(COUNTERS)
    return result


def main():
    assert not OUT.exists()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("3f300a84c")
    subprocess.run(
        ["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True
    )
    log = LOG.read_text()
    assert "BUILD SUCCESS" in log and log.count("BugInstance size is 0") == 6
    assert "Tests run: 682, Failures: 0, Errors: 0, Skipped: 0" in log
    assert sum(MODULES.values()) == 2383
    for folder in ("junit", "coverage", "static"):
        (OUT / folder).mkdir(parents=True, exist_ok=False)
    suites, coverage = {}, {}
    for module, expected in MODULES.items():
        target = ROOT / f"src/schubert-nk-{module}/target"
        reports = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        assert reports
        (OUT / "junit" / module).mkdir()
        actual = 0
        for source in reports:
            suite = ET.parse(source).getroot()
            cases = suite.findall("testcase")
            assert suite.tag == "testsuite" and len(cases) == int(suite.get("tests", "-1"))
            assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
            assert all(
                all(child.tag in ("system-out", "system-err") for child in case)
                for case in cases
            )
            safe = ET.Element(
                "testsuite",
                {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")},
            )
            for case in cases:
                ET.SubElement(
                    safe,
                    "testcase",
                    {key: case.get(key) for key in ("name", "classname", "time")},
                )
            ET.indent(safe)
            ET.ElementTree(safe).write(
                OUT / "junit" / module / source.name, encoding="utf-8", xml_declaration=True
            )
            actual += len(cases)
        assert actual == expected
        suites[module] = {"tests": actual, "suites": len(reports), "failures": 0, "errors": 0, "skipped": 0}
        coverage[module] = counters(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
        spot = ET.parse(target / "spotbugsXml.xml").getroot()
        assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
        emit(OUT / "static" / f"{module}.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    batch = ET.parse(ROOT / "src/schubert-nk-batch/target/site/jacoco/jacoco.xml").getroot()
    changed = {}
    for klass in batch.iter("class"):
        name = klass.get("name", "")
        if name.endswith("/MorningCurrentInvalidation") or name.endswith("/MorningControlScope"):
            changed[name.rsplit("/", 1)[-1]] = counters(klass)
    assert set(changed) == {"MorningCurrentInvalidation", "MorningControlScope"}
    assert changed["MorningCurrentInvalidation"]["BRANCH"] == {"missed": 2, "covered": 20}
    assert changed["MorningControlScope"]["BRANCH"] == {"missed": 0, "covered": 4}
    emit(OUT / "coverage" / "all-modules.json", coverage)
    emit(OUT / "coverage" / "changed-classes.json", changed)
    files = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
        for path in sorted(OUT.rglob("*"))
        if path.is_file()
    ]
    manifest = {
        "id": "PG344-morning-invalid",
        "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation",
        "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; Node24.19.0; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Production six explicit modules: clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check; fixed Node absolute path",
        "exitCode": 0,
        "input": "same-run Morning M/original/DB, stop8, A, fresh8, durable INVALID/readback",
        "expected": "2,383 PT F/E/S0; six static0; INVALID only after fresh8; all four coverage counters 100% for formal acceptance",
        "actual": "2,383 PT F/E/S0; six static0; changed native path and four modules below coverage100%; no external Morning acceptance",
        "testIds": [f"PT-OPS-MINVALID{n:03d}" for n in range(1, 7)]
        + ["PT-OPS-MCTRL010", "PT-OPS-MCTRL011"],
        "suites": suites,
        "coverage": coverage,
        "changedCoverage": changed,
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLog": {"path": str(LOG), "sha256": sha(LOG)},
        "bugs": ["BUG-315"],
        "ykt": ["YKT-248"],
        "ssc": ["SSC-089", "SSC-105"],
        "limitations": [
            "Real pending-run resume selection, normal Morning main and all eight Units remain unconnected",
            "Real tmpfs current INVALID, clean broker journal, backup/Cleanup and permit remain untested",
            "JUnit properties/output/failure payload omitted; no raw secret or invocation IDs",
        ],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(
        json.dumps(
            {"tests": sum(MODULES.values()), "suites": sum(item["suites"] for item in suites.values()),
             "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}
        )
    )


if __name__ == "__main__":
    main()
