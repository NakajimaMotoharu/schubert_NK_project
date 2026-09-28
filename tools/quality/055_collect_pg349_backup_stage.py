#!/usr/bin/env python3
"""Sanitize the immutable PG349 six-module run and retain its coverage gaps."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG349-backup-stage"
LOG = Path("/tmp/pgpt-pg349-six-final.log")
EXPECTED = {"protocol": 80, "storage": 149, "bootstrap": 175, "api": 742, "web": 555, "batch": 713}
CHANGED = ("MorningBackupRequestPublication", "MorningBackupStage", "MorningBackupPreparation")
SOURCES = (
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBackupRequestPublication.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBackupStage.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupRequestPublicationTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupStageTest.java",
    "evidence/01_PT/018_NK-OPS-001/219_NK-OPS-001_Morning_backup_request_root公開_単体テスト仕様書.md",
    "evidence/01_PT/018_NK-OPS-001/221_NK-OPS-001_Morning_backup_stage_単体テスト仕様書.md",
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
    # JaCoCo omits BRANCH for classes containing no conditional bytecode. This is 0/0,
    # not a coverage exclusion; the other three counters remain mandatory.
    value.setdefault("BRANCH", {"missed": 0, "covered": 0})
    assert set(value) == {"BRANCH", "LINE", "METHOD", "CLASS"}
    return value


def main():
    assert not OUT.exists(), "Refuse to overwrite evidence"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("bca771325")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    log = LOG.read_text()
    assert "BUILD SUCCESS" in log and log.count("BugInstance size is 0") == 6
    assert sum(EXPECTED.values()) == 2414
    for expected in EXPECTED.values():
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
            safe = ET.Element("testsuite", {key: suite.get(key) for key in
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
    assert sum(value["suites"] for value in suites.values()) == 354
    batch = ET.parse(ROOT / "src/schubert-nk-batch/target/site/jacoco/jacoco.xml").getroot()
    changed = {klass.get("name"): counts(klass) for klass in batch.iter("class")
               if klass.findall("counter") and any(klass.get("name", "").rsplit("/", 1)[-1].startswith(prefix)
                      for prefix in CHANGED)}
    assert any(name.endswith("/MorningBackupStage") for name in changed)
    assert any(name.endswith("/MorningBackupRequestPublication") for name in changed)
    write(OUT / "coverage" / "all-modules.json", coverage)
    write(OUT / "coverage" / "changed-classes.json", changed)
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
             for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG349-backup-stage", "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; Node24.19.0; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Production six explicit modules: clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check; fixed Node PATH and -Dnk.pt.node",
        "exitCode": 0,
        "input": "same-run parent M/A/DB/original/INVALID then committed backup begins and fixed root request",
        "expected": "2,414 PT F/E/S0; static0; four coverage counters 100% for formal acceptance",
        "actual": "2,414 PT F/E/S0; static0; native parent factories and whole-system coverage remain incomplete",
        "testIds": [f"PT-OPS-MBPUB{i:03d}" for i in range(1, 7)]
                   + [f"PT-OPS-MBSTAGE{i:03d}" for i in range(1, 5)],
        "suites": suites, "coverage": coverage, "changedCoverage": changed,
        "sourceHashes": [{"path": path, "sha256": sha(ROOT / path)} for path in SOURCES],
        "externalLog": {"path": str(LOG), "sha256": sha(LOG)},
        "bugs": ["BUG-315"], "ykt": ["YKT-248", "YKT-250"],
        "ssc": ["SSC-055", "SSC-089", "SSC-092", "SSC-094", "SSC-104", "SSC-105"],
        "limitations": [
            "Actual backup Unit start/termination, archives, cleanup, permit and external Morning main are not connected",
            "Fixed VM request directory is absent; existing pending run, current and old Unit are unchanged",
            "JUnit properties/output/failure payload omitted; no raw secret, cookie, token or Invocation ID",
        ],
        "files": files,
    }
    write(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"tests": sum(EXPECTED.values()), "suites": 354, "files": len(files),
                      "manifestSha256": sha(OUT / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
