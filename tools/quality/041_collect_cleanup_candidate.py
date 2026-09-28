#!/usr/bin/env python3
"""Publish sanitized PG334 limited evidence; never certifies Cleanup or full PG/PT."""

import hashlib
import json
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = "3d0371698"
RUN = "PG334-selected"
BASE = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional"
OUTPUT = BASE / RUN
REPORT = ROOT / "src/schubert-nk-batch/target"
TESTS = {
    "CleanupProcessMainTest": 4,
    "CleanupServiceUnitTest": 3,
    "CleanupPreflightTest": 5,
    "CleanupBackupAdmissionTest": 10,
    "CleanupDatabaseSessionTest": 9,
}
SOURCES = [
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CleanupNativePreflight.java",
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CleanupProcessMain.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CleanupProcessMainTest.java",
    "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/CleanupServiceUnitTest.java",
    "src/deployment/systemd/schubert-nk-cleanup.service.template",
]
LOGS = [
    pathlib.Path("/tmp/pg334-final-selected.log"),
    pathlib.Path("/tmp/pg334-production-six-static.log"),
    pathlib.Path("/tmp/pg334-static-coverage.log"),
    pathlib.Path("/tmp/pg334-smoke.log"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not OUTPUT.exists(), "evidence must be new-only"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith(SOURCE)
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml"], cwd=ROOT, check=True)
    selected_log, six_log, red_log, smoke_log = (p.read_text() for p in LOGS)
    assert "Tests run: 31, Failures: 0, Errors: 0, Skipped: 0" in selected_log
    assert "BUILD SUCCESS" in selected_log and "BUILD SUCCESS" in six_log
    assert six_log.count("BugInstance size is 0") == 6
    assert "DMI_HARDCODED_ABSOLUTE_FILENAME" in red_log and "BUILD FAILURE" in red_log
    assert smoke_log == ""  # Native rootless process returns 30 without any raw diagnostic.

    for name in ("junit", "coverage", "static", "logs"):
        (OUTPUT / name).mkdir(parents=True, exist_ok=False)
    counts = {}
    for name, expected in TESTS.items():
        path = next((REPORT / "surefire-reports").glob(f"TEST-*.{name}.xml"))
        root = ET.parse(path).getroot()
        cases = root.findall("testcase")
        assert len(cases) == expected and int(root.get("tests", "-1")) == expected
        assert all(int(root.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        assert all(child.tag in ("system-out", "system-err") for case in cases for child in case)
        clean = ET.Element(
            "testsuite",
            {key: root.get(key) for key in ("name", "tests", "failures", "errors", "skipped", "time")},
        )
        for case in cases:
            ET.SubElement(clean, "testcase", {key: case.get(key) for key in ("name", "classname", "time")})
        ET.indent(clean)
        ET.ElementTree(clean).write(OUTPUT / "junit" / path.name, encoding="utf-8", xml_declaration=True)
        counts[name] = expected

    jacoco = REPORT / "site/jacoco/jacoco.xml"
    tree = ET.parse(jacoco).getroot()
    coverage = {}
    for klass in tree.iter("class"):
        short = klass.get("name", "").split("/")[-1]
        if short not in ("CleanupNativePreflight", "CleanupProcessMain"):
            continue
        coverage[short] = {
            item.get("type"): {"missed": int(item.get("missed")), "covered": int(item.get("covered"))}
            for item in klass.findall("counter")
            if item.get("type") in ("LINE", "BRANCH", "METHOD", "CLASS")
        }
    assert set(coverage) == {"CleanupNativePreflight", "CleanupProcessMain"}
    assert coverage["CleanupNativePreflight"]["LINE"]["missed"] > 0
    write_json(OUTPUT / "coverage/cleanup-classes.json", coverage)
    write_json(
        OUTPUT / "static/production-six.json",
        {"modules": ["protocol", "storage", "bootstrap", "api", "web", "batch"], "bugInstancesEach": 0, "exitCode": 0},
    )
    write_json(
        OUTPUT / "logs/bug312-red-green.json",
        {"bug": "BUG-312", "initial": "DMI_HARDCODED_ABSOLUTE_FILENAME in generated lambda; exit 1", "final": "Production six SpotBugs 0; exit 0"},
    )
    write_json(
        OUTPUT / "logs/rootless-external-smoke.json",
        {"command": "Java25 CleanupProcessMain with compiled Production classpath, no argv", "uid": 1000, "exitCode": 30, "stdoutStderrBytes": 0, "interpretation": "fail-closed only; not a genuine Cleanup Unit"},
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
        "environment": "Linux host UID1000; JDK25.0.4; Maven3.9.12; PostgreSQL18 test fixture; JaCoCo0.8.15; SpotBugs4.10.4.0",
        "command": "Batch selected CleanupProcessMainTest,CleanupServiceUnitTest,CleanupPreflightTest,CleanupBackupAdmissionTest,CleanupDatabaseSessionTest test spotbugs:check jacoco:report; Production6 explicit SpotBugs check; rootless Java main smoke",
        "exitCode": 0,
        "input": "No-argv/argument/null/known-unknown failures; candidate fixed Unit; borrowed preflight/DB/backup; native rootless smoke",
        "expected": "31 PT F/E/S0, Production6 static0, no 0/10 from incomplete Cleanup entry, rootless exit30",
        "actual": "31 PT F/E/S0, Production6 static0, rootless exit30; Java class coverage below 100% and genuine Unit not installed",
        "counts": counts,
        "coverage": coverage,
        "coverageSourceSha256": digest(jacoco),
        "sourceHashes": [{"path": name, "sha256": digest(ROOT / name)} for name in SOURCES],
        "externalLogs": [{"path": str(path), "sha256": digest(path)} for path in LOGS],
        "relatedBug": ["BUG-312"],
        "relatedYkt": ["YKT-245"],
        "relatedSsc": ["SSC-104"],
        "limitations": [
            "Provisional selected test; no same-source Production all-scope formal certification",
            "Native success path unexecuted; both new classes fail Java line/method coverage 100%",
            "Candidate Unit not installed; parent M/A/terminal actors/DELETE/transfer and Artemis remain incomplete",
            "JUnit XML contains only suite/case attributes; no properties, output, failure or secret material",
        ],
        "files": files,
    }
    write_json(OUTPUT / "manifest.json", manifest)
    assert all(digest(ROOT / item["path"]) == item["sha256"] for item in files)
    assert not re.search(r"PRIVATE_CANARY|Bearer |-----BEGIN |AKIA[0-9A-Z]{16}", json.dumps(manifest))
    print(json.dumps({"id": RUN, "tests": sum(counts.values()), "files": len(files), "manifestSha256": digest(OUTPUT / "manifest.json")}))


if __name__ == "__main__":
    main()
