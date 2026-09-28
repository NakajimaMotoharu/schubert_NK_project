#!/usr/bin/env python3
"""Collect sanitized PG350 isolated-VM fixed request I/O, not Morning acceptance."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG350-native-backup-request"
LOG = Path("/tmp/pg350-native-final.log")
STATE = Path("/tmp/pg350-native-state.txt")
NATIVE = Path("/tmp/pg350-native-coverage.exec")
MERGED = Path("/tmp/pg350-merged.exec")
JAR = ROOT / "src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar"
PROBE = Path("/tmp/pg350-probe-classes/dev/codex/schubert/nk/batch/file/NativeMorningBackupRequestProbe.class")
TESTS = ("MorningBackupRequestPublicationTest", "BackupWorkerRequestFilesTest")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def counts(node):
    data = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
            for c in node.findall("counter") if c.get("type") in {"BRANCH", "LINE", "METHOD", "CLASS"}}
    data.setdefault("BRANCH", {"missed": 0, "covered": 0})
    assert set(data) == {"BRANCH", "LINE", "METHOD", "CLASS"}
    return data


def main():
    assert not OUT.exists(), "Refuse to overwrite existing native evidence"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head.startswith("2453e9dea")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src", "pom.xml",
                    "tools/quality/vm/NativeMorningBackupRequestProbe.java"], cwd=ROOT, check=True)
    assert LOG.read_text() == "PUBLICATION_READBACK_RETIRED\n"
    state = STATE.read_text()
    assert "directory 700 0:0" in state and "user::rwx\ngroup::---\nother::---" in state
    assert "backup-request d 700 root:root\n" in state
    assert state.count("ActiveState=inactive\nMainPID=0\n") == 2
    assert "ec2018fcfdf89471ccc1cd842c9f6b5f00e755d657921b634281d6589d3f0613" in state
    assert "729594f1096270611e1ed4d71f622ffa08533665ece059a40f687817284f4daa" in state
    assert sha(JAR) == "ec2018fcfdf89471ccc1cd842c9f6b5f00e755d657921b634281d6589d3f0613"
    assert sha(PROBE) == "729594f1096270611e1ed4d71f622ffa08533665ece059a40f687817284f4daa"
    for name in ("junit", "coverage", "output"):
        (OUT / name).mkdir(parents=True, exist_ok=False)
    count = 0
    for name in TESTS:
        path = ROOT / f"src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.file.{name}.xml"
        suite = ET.parse(path).getroot()
        cases = suite.findall("testcase")
        assert int(suite.get("tests", "-1")) == len(cases)
        assert all(int(suite.get(key, "-1")) == 0 for key in ("failures", "errors", "skipped"))
        safe = ET.Element("testsuite", {key: suite.get(key) for key in
                                 ("name", "tests", "failures", "errors", "skipped", "time")})
        for case in cases:
            ET.SubElement(safe, "testcase", {key: case.get(key) for key in
                                                ("name", "classname", "time")})
        ET.indent(safe)
        ET.ElementTree(safe).write(OUT / "junit" / path.name, encoding="utf-8", xml_declaration=True)
        count += len(cases)
    assert count == 14
    report = ET.parse(ROOT / "src/schubert-nk-batch/target/site/jacoco/jacoco.xml").getroot()
    changed = {node.get("name"): counts(node) for node in report.iter("class")
               if node.get("name", "").rsplit("/", 1)[-1].startswith("MorningBackupRequestPublication")
               and node.findall("counter")}
    assert len(changed) == 2
    write(OUT / "coverage" / "merged-host-selected-and-vm-native.json", changed)
    write(OUT / "output" / "native-result.json", {
        "missingDirectoryExploration": "MISSING_REFUSED, prior to source commit, identical JAR byte; not formal",
        "committedSourcePresentRun": "PUBLICATION_READBACK_RETIRED",
        "actualDirectory": "root:root 0700 tmpfs, ACL entries only user/group/other, no remaining child file",
        "morningUnit": "inactive/PID0, preexisting PG323 test-only Unit unchanged",
        "backupUnit": "inactive/PID0, unchanged",
        "vm": "Linux 7.0.0-31-generic x86_64; JDK25.0.4",
    })
    files = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
             for path in sorted(OUT.rglob("*")) if path.is_file()]
    manifest = {
        "id": "PG350-native-backup-request", "formal": False,
        "executionTime": datetime.now().astimezone().isoformat(),
        "branch": "dev-foundation", "sourceCommit": head,
        "environment": "isolated Linux VM; JDK25.0.4; root actor probe, not authenticated Morning Unit",
        "command": "sudo java -javaagent:JaCoCo0.8.15 --enable-native-access=ALL-UNNAMED -cp fixed PG350 probe/batch JAR/PG316 lib NativeMorningBackupRequestProbe present",
        "exitCode": 0,
        "input": "fixed nonsecret BackupWorkerRequest vector; new-only part; root700 fixed tmpfs",
        "expected": "publication/readback/retire; no residual request; no existing Unit or pending run mutation",
        "actual": "PUBLICATION_READBACK_RETIRED; fixed directory empty; Morning and Backup inactive/PID0",
        "testIds": ["PT-OPS-MBNATIVE002", "PT-OPS-MBNATIVE003"],
        "selectedHostTests": {"tests": count, "suites": len(TESTS), "failures": 0, "errors": 0, "skipped": 0},
        "coverage": {"mergedChangedClasses": changed,
                     "nativeExecSha256": sha(NATIVE), "mergedExecSha256": sha(MERGED),
                     "fourCounter100": False},
        "externalLog": {"path": str(LOG), "sha256": sha(LOG)},
        "externalState": {"path": str(STATE), "sha256": sha(STATE)},
        "sourceHashes": [
            {"path": "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBackupRequestPublication.java",
             "sha256": sha(ROOT / "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBackupRequestPublication.java")},
            {"path": "tools/quality/vm/NativeMorningBackupRequestProbe.java",
             "sha256": sha(ROOT / "tools/quality/vm/NativeMorningBackupRequestProbe.java")},
        ],
        "jarSha256": sha(JAR), "probeClassSha256": sha(PROBE),
        "bugs": ["BUG-315"], "ykt": ["YKT-248", "YKT-250"],
        "ssc": ["SSC-055", "SSC-092", "SSC-094", "SSC-104", "SSC-105"],
        "limitations": [
            "Native actor is a root probe, not Morning Unit/cgroup authentication or continuous M/A/DB ownership",
            "No backup worker start/terminal proof, archive, DB success, cleanup or startup permit",
            "JaCoCo host-selected/native merge is provisional and still below four-counter 100%; full six-module run was prior source",
        ],
        "files": files,
    }
    write(OUT / "manifest.json", manifest)
    assert all(sha(ROOT / item["path"]) == item["sha256"] for item in files)
    print(json.dumps({"hostTests": count, "nativeExit": 0, "files": len(files),
                      "manifestSha256": sha(OUT / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
