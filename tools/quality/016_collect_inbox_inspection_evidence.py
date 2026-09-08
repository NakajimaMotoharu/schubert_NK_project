#!/usr/bin/env python3
"""Collect only the eight Inbox structure PT from a previously certified full reactor.

NK-DAT-001; PG-D-119; QA-046/SSC-049; no declaration of DB cleanup completion.
Raw JUnit properties, stdout, stderr and ciphertext are never copied.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not re.fullmatch(r"PT-(ADM|WEB|SCN|MED)-[A-Za-z0-9-]+", run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    certified = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    base = json.loads(certified.read_text())
    if base["runId"] != run or base["exitCode"] != 0:
        raise SystemExit("collect matching full reactor evidence first")
    subprocess.run(["git", "diff", "--exit-code", base["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True, stdout=subprocess.DEVNULL)
    target = repo / "src/schubert-nk-api/target"
    class_name = "dev.codex.schubert.nk.api.maintenance.InboxResponseInspectorTest"
    suite = ET.parse(target / "surefire-reports" / ("TEST-" + class_name + ".xml")).getroot()
    names = ["validSuccessAndErrorProfiles", "headerAndMetadataMismatchesReject",
             "payloadEncodingAndSemanticFaultsReject", "cryptographicDamageAndMissingSnapshotReject",
             "exactLengthsAndTimestampPrecision", "nullContractsFailBeforeValidation",
             "concurrentInspectionsDoNotShareState", "databaseReferenceIsNotCertifiedByStructure"]
    cases = suite.findall("testcase")
    if (len(cases) != 8 or int(suite.get("tests", "0")) != 8
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or {c.get("name") for c in cases} != set(names)
            or any(c.get("classname") != class_name or len(c) != 0 for c in cases)):
        raise SystemExit("missing, nonpassing or noncanonical tests")
    coverage_xml = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
    classes = [c for p in coverage_xml.findall("package") for c in p.findall("class")
               if c.get("name") == "dev/codex/schubert/nk/api/maintenance/InboxResponseInspector"]
    if len(classes) != 1:
        raise SystemExit("missing inspection class coverage")
    counters = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                for c in classes[0].findall("counter")}
    if (not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
            or any(v["missed"] or not v["covered"] for v in counters.values())):
        raise SystemExit("inspection coverage below 100 percent")
    out = repo / "evidence/01_PT/004_NK-DAT-001/evidence/inbox-inspection"
    out.mkdir(parents=True, exist_ok=True)
    clean = ET.Element("testsuite", {k: suite.get(k) for k in
                                    ("name", "tests", "failures", "errors", "skipped", "time")})
    for case in cases:
        ET.SubElement(clean, "testcase", {k: case.get(k) for k in ("name", "classname", "time")})
    ET.indent(clean)
    ET.ElementTree(clean).write(out / "results.xml", encoding="UTF-8", xml_declaration=True)
    manifest = {
        "runId": run, "programId": "NK-DAT-001", "targetCommit": base["targetCommit"],
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        "exitCode": 0, "scopeResult": "PASS_STRUCTURE_ONLY", "programStatus": "IN_PROGRESS",
        "startedAt": Path("/tmp", run + ".started").read_text().strip(),
        "completedAt": Path("/tmp", run + ".completed").read_text().strip(),
        "fullReactorManifest": "../../../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": hashlib.sha256(certified.read_bytes()).hexdigest(),
        "environment": {"os": "Ubuntu 26.04.1 LTS x86_64", "java": "25.0.4+7", "maven": "3.9.12",
                        "junit": "5.13.4", "jacoco": "0.8.15", "spotbugsPlugin": "4.10.4.0"},
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify",
        "coverage": counters, "failed": 0, "errors": 0, "skipped": 0,
        "tests": {f"PT-DB-INBOX-{i:03d}": {"method": class_name + "#" + name,
                                         "result": "PASS"} for i, name in enumerate(names, 1)},
        "fixture": "Runtime CSPRNG test-only keys; independent JCE/Deflater envelope and hand-written SS234 wire. No credential or ciphertext saved.",
        "oracle": "003 PT specification: literal true/false, unsigned N3 000/999 valid, nonnumeric/descending invalid. No production expected generation.",
        "remaining": "DB references, expiry/backup/lock/deletion, least-privilege SQL and oneshot wiring NOT certified.",
        "related": ["QA-046", "UIC-006", "SSC-049", "BUG-014", "YKT-012", "BUG-075", "YKT-067"],
        "files": [{"path": "results.xml", "sha256": hashlib.sha256((out / "results.xml").read_bytes()).hexdigest()}]
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (out / "checksums.sha256").write_text("".join(
        hashlib.sha256((out / name).read_bytes()).hexdigest() + "  " + name + "\n"
        for name in ("results.xml", "manifest.json")))
    print(json.dumps({"runId": run, "structureTests": 8, "coverage": counters, "programComplete": False}))


if __name__ == "__main__":
    main()
