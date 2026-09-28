#!/usr/bin/env python3
"""Save sanitized PG345 six-module evidence from one immutable source/test commit."""

import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG345-morning-resume"
LOG = pathlib.Path("/tmp/pgpt-pg345-six-final.log")
MODULES = {"protocol": 80, "storage": 149, "bootstrap": 175, "api": 742, "web": 555, "batch": 693}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningResumeAdmission.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningControlScope.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningNewRunAdmission.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningResumeAdmissionTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java",
)
CHANGED = {"MorningResumeAdmission", "MorningControlScope", "MorningNewRunAdmission", "MorningDatabaseSession"}
COUNTERS = {"LINE", "METHOD", "CLASS", "BRANCH"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def counters(element):
    result = {
        node.get("type"): {"missed": int(node.get("missed")), "covered": int(node.get("covered"))}
        for node in element.findall("counter")
        if node.get("type") in COUNTERS
    }
    assert set(result) == COUNTERS
    return result


def main():
    assert not OUT.exists(), "Evidence path must never be silently overwritten"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("0c47d6124")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    raw = LOG.read_text()
    assert "BUILD SUCCESS" in raw and raw.count("BugInstance size is 0") == 6
    for module, count in MODULES.items():
        assert f"Tests run: {count}, Failures: 0, Errors: 0, Skipped: 0" in raw
    assert sum(MODULES.values()) == 2394
    for directory in ("junit", "coverage", "static"):
        (OUT / directory).mkdir(parents=True, exist_ok=False)
    suites = {}
    coverage = {}
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
            assert all(all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
            sanitized = ET.Element(
                "testsuite",
                {key: suite.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")},
            )
            for case in cases:
                ET.SubElement(
                    sanitized,
                    "testcase",
                    {key: case.get(key) for key in ("name", "classname", "time")},
                )
            ET.indent(sanitized)
            ET.ElementTree(sanitized).write(
                OUT / "junit" / module / source.name, encoding="utf-8", xml_declaration=True
            )
            actual += len(cases)
        assert actual == expected
        suites[module] = {"tests": actual, "suites": len(reports), "failures": 0, "errors": 0, "skipped": 0}
        coverage[module] = counters(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
        spot = ET.parse(target / "spotbugsXml.xml").getroot()
        assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
        emit(OUT / "static" / f"{module}.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    changed = {}
    batch = ET.parse(ROOT / "src/schubert-nk-batch/target/site/jacoco/jacoco.xml").getroot()
    for node in batch.iter("class"):
        name = node.get("name", "").rsplit("/", 1)[-1]
        if name in CHANGED:
            changed[name] = counters(node)
    assert set(changed) == CHANGED
    emit(OUT / "coverage" / "all-modules.json", coverage)
    emit(OUT / "coverage" / "changed-classes.json", changed)
    files = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
        for path in sorted(OUT.rglob("*")) if path.is_file()
    ]
    manifest = {
        "id": "PG345-morning-resume", "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; Node24.19.0; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Production six explicit modules: clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check; fixed Node PATH and -Dnk.pt.node",
        "exitCode": 0,
        "input": "explicit same-run resume under M, dedicated DB advisory before durable original mutation, reference consistency",
        "expected": "2,394 PT F/E/S0; six static0; DB-before-file mutation; all four coverage counters 100% for formal acceptance",
        "actual": "2,394 PT F/E/S0; six static0; four modules below coverage100%; no external Morning acceptance",
        "testIds": [f"PT-OPS-MRESUME{n:03d}" for n in range(1, 10)] + ["PT-OPS-MDB013", "PT-OPS-MDB014"],
        "suites": suites, "coverage": coverage, "changedCoverage": changed,
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLog": {"path": str(LOG), "sha256": sha(LOG)},
        "bugs": ["BUG-317"], "ykt": ["YKT-250"], "ssc": ["SSC-055", "SSC-094", "SSC-105"],
        "limitations": [
            "Production external Morning main and real pending-run resume are not connected",
            "Five fixed Units are missing; actual M/A/stop8/backup/Cleanup/permit and real NK CHR unaccepted",
            "JUnit properties/output/failure payload omitted; no raw secret, session or Invocation ID",
        ],
        "files": files,
    }
    emit(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(MODULES.values()), "suites": sum(s["suites"] for s in suites.values()),
                      "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
