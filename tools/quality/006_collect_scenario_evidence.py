#!/usr/bin/env python3
"""Certify Scenario PT using allowlisted metadata; reject failed, skipped, flaky and partial coverage."""

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
    run = args.run_id
    if not run.startswith("PT-SCN-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    evidence = repo / "evidence/01_PT/008_NK-SCN-001/evidence"
    read = lambda suffix: (Path("/tmp") / (run + suffix)).read_text().strip()
    if read(".exit") != "0":
        raise SystemExit("failed execution cannot be certified")
    commit = read(".commit")
    subprocess.run(["git", "diff", "--exit-code", commit, "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    raw = (Path("/tmp") / (run + ".log")).read_bytes()
    if b"BUILD SUCCESS" not in raw or b"[ERROR]" in raw:
        raise SystemExit("build log is not successful")
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    modules, methods = {}, []
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
            cases = suite.findall("testcase")
            if (any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped"))
                    or len(cases) != int(suite.get("tests"))):
                raise SystemExit("nonpassing or inconsistent JUnit report")
            for case in cases:
                if any(child.tag not in ("system-out", "system-err") for child in case):
                    raise SystemExit("failure/rerun/flaky/skipped test is not certifiable")
            count += len(cases)
            if (".api.persistence.Scenario" in suite.get("name", "")
                    or ".api.storage." in suite.get("name", "")):
                clean = ET.Element("testsuite", {k: suite.get(k) for k in
                                                ("name", "time", "tests", "errors", "failures", "skipped")})
                for case in cases:
                    attrs = {k: case.get(k) for k in ("name", "classname", "time")}
                    ET.SubElement(clean, "testcase", attrs)
                    methods.append(attrs["classname"] + "#" + attrs["name"])
                ET.indent(clean)
                ET.ElementTree(clean).write(evidence / "output" / report.name,
                                            encoding="UTF-8", xml_declaration=True)
        jacoco = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
        counters = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                    for c in jacoco.findall("counter")}
        if not counters or any(v["missed"] for v in counters.values()):
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
    if not methods:
        raise SystemExit("missing Scenario tests")
    manifest = {
        "runId": run, "programId": "NK-SCN-001", "targetCommit": commit,
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        "startedAt": read(".started"), "completedAt": read(".completed"), "exitCode": 0,
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify",
        "environment": {"os": platform.platform(), "jdk": "25.0.4", "maven": "3.9.12",
                        "postgresql": "18.6", "artemis": "2.56.0",
                        "libc": subprocess.check_output(["getconf", "GNU_LIBC_VERSION"], text=True).strip(),
                        "apiNativeAccess": "ALL-UNNAMED; public Java25 FFM; SSC-019"},
        "modules": modules, "scenarioMethods": methods,
        "testIdsPartial": ["PT-SCN-001", "PT-SCN-002", "PT-SCN-003", "PT-SCN-004",
                           "PT-SCN-005", "PT-SCN-006", "PT-SCN-007", "PT-SCN-008"],
        "additionalTestsPassed": ["PT-SCN-008-D01", "PT-SCN-008-D02", "PT-SCN-008-D03", "PT-SCN-008-D04",
                                  "PT-SCN-008-F01", "PT-SCN-008-F02-CORE", "PT-SCN-008-F03"],
        "testIdsNotRun": ["PT-SCN-008-F02-ADMIT", "PT-SCN-008-F04", "PT-SCN-009"],
        "programStatus": "IN_PROGRESS", "notRunCountedAsPass": 0,
        "relatedSsc": ["SSC-017", "SSC-018", "SSC-019"], "relatedBug": ["BUG-030", "BUG-031", "BUG-032", "BUG-033", "BUG-035"],
        "relatedYkt": ["YKT-027", "YKT-028", "YKT-029", "YKT-031"],
        "baseline": "Current baseline unchanged; Scenario application CHR not run yet",
        "rawLogSha256": hashlib.sha256(raw).hexdigest(),
        "redaction": "Only class/method names, versions, counters and fixed metadata; all properties/stdout/stderr omitted.",
        "expectations": "008 PT specification: UI234 independent byte offsets and literal route maps, synthetic SQL fixtures and independently enumerated entry IDs/order/filter/page outcomes. Native storage uses literal bytes and actual filesystem postconditions: one of 100 publishers wins without replacing existing bytes; retained FDs survive path replacement and are all closed. Production is not used to generate expected values.",
        "scope": "Read-only queries/detail snapshot plus API native directory capability core. Root/FS/permission/nlink admission, full writer/reader lifecycle, authentication/Inbox/dispatcher, Web/HTTP and CHR remain untested and unimplemented as tracked in 431/008.",
    }
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "checksums.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
                                                     for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"), encoding="utf-8")
    print(json.dumps({"runId": run, "tests": sum(v["tests"] for v in modules.values()), "scenarioTests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
