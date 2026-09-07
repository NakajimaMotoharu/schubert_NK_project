#!/usr/bin/env python3
"""Collect only allowlisted execution metadata, never raw JVM properties/test stdout/secret values."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    if not args.run_id.startswith("PT-AUT-") or not all(c.isalnum() or c == "-" for c in args.run_id):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    evidence = repo / "evidence/01_PT/007_NK-AUT-001/evidence"
    metadata = Path("/tmp")
    read = lambda suffix: (metadata / (args.run_id + suffix)).read_text().strip()
    if read(".exit") != "0":
        raise SystemExit("failed execution cannot be certified")
    commit = read(".commit")
    subprocess.run(["git", "diff", "--exit-code", commit, "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    raw_log = (metadata / (args.run_id + ".log")).read_bytes()
    if b"BUILD SUCCESS" not in raw_log or b"[ERROR]" in raw_log:
        raise SystemExit("build log is not successful")
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    modules = {}
    auth_methods = []
    for module, directory in (("characterization", "program/characterization"),
                              ("protocol", "src/schubert-nk-protocol"),
                              ("api", "src/schubert-nk-api"), ("web", "src/schubert-nk-web")):
        target = repo / directory / "target"
        reports = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        if not reports:
            raise SystemExit("missing JUnit reports")
        count = 0
        for report in reports:
            suite = ET.parse(report).getroot()
            if any(int(suite.get(name, "0")) for name in ("errors", "failures", "skipped")):
                raise SystemExit("nonpassing JUnit report")
            cases = suite.findall("testcase")
            if len(cases) != int(suite.get("tests")):
                raise SystemExit("JUnit method count mismatch")
            for case in cases:
                if any(child.tag not in ("system-out", "system-err") for child in case):
                    raise SystemExit("failure/rerun/flaky/skipped test is not certifiable")
            count += len(cases)
            if ".api.security." in suite.get("name", ""):
                clean = ET.Element("testsuite", {name: suite.get(name) for name in
                                                ("name", "time", "tests", "errors", "failures", "skipped")})
                for case in cases:
                    attributes = {name: case.get(name) for name in ("name", "classname", "time")}
                    ET.SubElement(clean, "testcase", attributes)
                    auth_methods.append(attributes["classname"] + "#" + attributes["name"])
                ET.indent(clean)
                ET.ElementTree(clean).write(evidence / "output" / report.name,
                                            encoding="UTF-8", xml_declaration=True)
        jacoco = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
        counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                         "covered": int(counter.get("covered"))}
                    for counter in jacoco.findall("counter")}
        if not counters or any(value["missed"] for value in counters.values()):
            raise SystemExit("coverage is not 100 percent")
        shutil.copyfile(target / "site/jacoco/jacoco.csv", evidence / "coverage" / (module + "-jacoco.csv"))
        static = "not configured for characterization runner"
        if module != "characterization":
            spot = ET.parse(target / "spotbugsXml.xml").getroot()
            errors = spot.find("Errors")
            if spot.findall("BugInstance") or errors is None or int(errors.get("errors", "0")):
                raise SystemExit("static analysis not clean")
            static = {"tool": "SpotBugs 4.10.4.0", "violations": 0, "errors": 0}
        modules[module] = {"tests": count, "coverage": counters, "spotbugs": static}
    manifest = {
        "runId": args.run_id, "programId": "NK-AUT-001", "targetCommit": commit,
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        "startedAt": read(".started"), "completedAt": read(".completed"), "exitCode": 0,
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify",
        "environment": {"os": platform.platform(), "jdk": "25.0.4", "maven": "3.9.12",
                        "springSecurityCrypto": "7.1.1", "springCore": "7.0.9"},
        "modules": modules, "authenticationMethods": auth_methods,
        "testIdsPassed": ["PT-AUT-001", "PT-AUT-002"],
        "testIdsPartial": {"PT-AUT-003": "immutable policy and real PostgreSQL User/IP counters, reconnect, thresholds, windows, locks, concurrency and rollback passed; Login/hash/audit/Inbox connection remains",
                           "PT-AUT-005": "ASCII SHA256, AES-GCM and transactional session issuance passed; Login/Inbox replay connection remains",
                           "PT-AUT-006": "real PostgreSQL session issuance/oldest replacement/tie/expiry/100 concurrent requests passed; full Login and CHR connection remains",
                           "PT-AUT-007": "real PostgreSQL verifier/idle/role/state/rollback/concurrency/faults passed; dispatcher/wire error mapping remains",
                           "PT-AUT-008": "actor/role/owner policy matrix only; database revocation/predicates/HTTP remain"},
        "testIdsNotRun": ["PT-AUT-004", "PT-AUT-009"],
        "programStatus": "IN_PROGRESS", "notRunCountedAsPass": 0,
        "relatedBug": ["BUG-020"], "relatedYkt": ["YKT-007", "YKT-008", "YKT-017"], "relatedSsc": [],
        "baseline": "Current baseline remains unchanged; authentication application CHR not run yet",
        "rawLogSha256": hashlib.sha256(raw_log).hexdigest(),
        "redaction": "Only fixed metadata, class/method names and counters collected; all test output and properties omitted.",
        "expectations": "007 PT specification; literal Unicode/Instant/authorization matrix, independent JCA PBKDF2/AES-GCM and DataOutputStream envelope/AAD, independently calculated SHA256 vectors. No production function constructs expected values.",
    }
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["files"] = [
        {"path": str(path.relative_to(evidence)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted(evidence.rglob("*"))
        if path.is_file() and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checksum_paths = [path for path in sorted(evidence.rglob("*")) if path.is_file() and path.name != "checksums.sha256"]
    (evidence / "checksums.sha256").write_text("".join(
        hashlib.sha256(path.read_bytes()).hexdigest() + "  " + str(path.relative_to(evidence)) + "\n"
        for path in checksum_paths), encoding="utf-8")
    print(json.dumps({"runId": args.run_id, "tests": sum(item["tests"] for item in modules.values()),
                      "authenticationTests": len(auth_methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
