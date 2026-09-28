#!/usr/bin/env python3
"""Sanitize the PG346 six-module run without changing its JUnit or production outputs."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG346-morning-db-capability"
LOG = Path("/tmp/pgpt-pg346-six-final.log")
EXPECTED = {"protocol": 80, "storage": 149, "bootstrap": 175, "api": 742, "web": 555, "batch": 697}
CHANGED = {"MorningControlScope", "MorningNewRunAdmission", "MorningResumeAdmission", "MorningDatabaseSession"}
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningControlScope.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningNewRunAdmission.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningResumeAdmission.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningControlScopeTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningNewRunAdmissionTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningResumeAdmissionTest.java",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def counts(node):
    value = {counter.get("type"): {"missed": int(counter.get("missed")),
                                    "covered": int(counter.get("covered"))}
             for counter in node.findall("counter")
             if counter.get("type") in {"BRANCH", "LINE", "METHOD", "CLASS"}}
    assert set(value) == {"BRANCH", "LINE", "METHOD", "CLASS"}
    return value


def main():
    assert not OUT.exists(), "Refuse to overwrite recorded evidence"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("fc0951740")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "BUILD SUCCESS" in log and log.count("BugInstance size is 0") == 6
    assert sum(EXPECTED.values()) == 2398
    for name, expected in EXPECTED.items():
        assert f"Tests run: {expected}, Failures: 0, Errors: 0, Skipped: 0" in log
    for name in ("junit", "coverage", "static"):
        (OUT / name).mkdir(parents=True, exist_ok=False)
    suites, coverage = {}, {}
    for name, expected in EXPECTED.items():
        target = ROOT / f"src/schubert-nk-{name}/target"
        reports = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        assert reports
        (OUT / "junit" / name).mkdir()
        actual = 0
        for path in reports:
            suite = ET.parse(path).getroot()
            cases = suite.findall("testcase")
            assert suite.tag == "testsuite" and len(cases) == int(suite.get("tests", "-1"))
            assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
            assert all(all(child.tag in ("system-out", "system-err") for child in case) for case in cases)
            safe = ET.Element(
                "testsuite", {key: suite.get(key) for key in
                              ("name", "tests", "failures", "errors", "skipped", "time")})
            for case in cases:
                ET.SubElement(safe, "testcase", {key: case.get(key) for key in
                                                 ("name", "classname", "time")})
            ET.indent(safe)
            ET.ElementTree(safe).write(OUT / "junit" / name / path.name,
                                       encoding="utf-8", xml_declaration=True)
            actual += len(cases)
        assert actual == expected
        suites[name] = {"tests": actual, "suites": len(reports),
                        "failures": 0, "errors": 0, "skipped": 0}
        coverage[name] = counts(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
        spot = ET.parse(target / "spotbugsXml.xml").getroot()
        assert not spot.findall("BugInstance") and int(spot.find("Errors").get("errors", "-1")) == 0
        write(OUT / "static" / f"{name}.json", {"bugInstances": 0, "errors": 0, "exitCode": 0})
    changed = {}
    batch = ET.parse(ROOT / "src/schubert-nk-batch/target/site/jacoco/jacoco.xml").getroot()
    for klass in batch.iter("class"):
        name = klass.get("name", "").rsplit("/", 1)[-1]
        if name in CHANGED:
            changed[name] = counts(klass)
    assert set(changed) == CHANGED
    write(OUT / "coverage" / "all-modules.json", coverage)
    write(OUT / "coverage" / "changed-classes.json", changed)
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
             for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG346-morning-db-capability", "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; Node24.19.0; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Production six explicit modules: clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check; fixed Node PATH and -Dnk.pt.node",
        "exitCode": 0,
        "input": "same-run M/A, durable original, dedicated DB Access, INVALID then backup begin/handoff callback",
        "expected": "2,398 PT F/E/S0; six static0; backup capability only inside owner scope; all four coverage counters 100% for formal acceptance",
        "actual": "2,398 PT F/E/S0; six static0; four modules below coverage100%; no external parent/worker acceptance",
        "testIds": ["PT-OPS-MNEW011", "PT-OPS-MRESUME010", "PT-OPS-MCTRL012", "PT-OPS-MCTRL013"],
        "suites": suites, "coverage": coverage, "changedCoverage": changed,
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLog": {"path": str(LOG), "sha256": sha(LOG)},
        "bugs": ["BUG-315"], "ykt": ["YKT-248", "YKT-250"],
        "ssc": ["SSC-055", "SSC-094", "SSC-104", "SSC-105"],
        "limitations": [
            "Actual backup worker, cleanup child, permit, external Morning main and NK capture are not connected",
            "Five fixed Units are not deployed and old pending VM run/current are unchanged",
            "JUnit properties/output/failure payload omitted; no raw secret, cookie, token or Invocation ID",
        ],
        "files": files,
    }
    write(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(EXPECTED.values()), "suites": sum(s["suites"] for s in suites.values()),
                      "files": len(files), "manifestSha256": sha(OUT / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
