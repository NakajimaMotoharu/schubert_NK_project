#!/usr/bin/env python3
"""Certify only executed NK-MED-001 methods against a verified full reactor, with no raw logs."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-MED-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json").read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("collect the matching full verified reactor first")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    prefix = "dev.codex.schubert.nk.web.media."
    expected = {
        "PT-MED-001": prefix + "HttpByteRangeParserTest#literalRangesPreserveFirstSpecAndOneMebibyteCap",
        "PT-MED-002": prefix + "HttpByteRangeParserTest#invalidGrammarBoundsAndArithmeticNeverSelectBytes",
        "PT-MED-003": prefix + "HttpByteRangeParserTest#nullAndConstructedSelectionsKeepInvariants",
        "PT-MED-004": prefix + "HttpByteRangeParserTest#oneHundredConcurrentParsesHaveNoSharedState",
        "PT-MED-005": prefix + "ContentDispositionFactoryTest#literalHeadersEncodeUtf8WithoutRawMetadata",
        "PT-MED-006": prefix + "MediaBodyStreamerTest#exactIntervalsUseBoundedWritesAndLeaveResourcesOpen(Path)",
        "PT-MED-007": prefix + "MediaBodyStreamerTest#nullBoundsAndIoFailuresDoNotClaimCompleteTransfer",
    }
    methods, clean_reports = [], {}
    for report in sorted((repo / "src/schubert-nk-web/target/surefire-reports").glob("TEST-" + prefix + "*.xml")):
        suite = ET.parse(report).getroot()
        cases = suite.findall("testcase")
        if any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped")) or len(cases) != int(suite.get("tests")):
            raise SystemExit("nonpassing/inconsistent media suite")
        clean = ET.Element("testsuite", {k: suite.get(k) for k in ("name", "time", "tests", "errors", "failures", "skipped")})
        for case in cases:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("failed/skipped/flaky/rerun media case")
            attrs = {k: case.get(k) for k in ("name", "classname", "time")}
            methods.append(attrs["classname"] + "#" + attrs["name"])
            ET.SubElement(clean, "testcase", attrs)
        ET.indent(clean)
        clean_reports[report.name] = ET.ElementTree(clean)
    if len(methods) != len(expected) or set(methods) != set(expected.values()):
        raise SystemExit("media Test IDs do not exactly cover executed methods")
    evidence = repo / "evidence/01_PT/009_NK-MED-001/evidence"
    for folder in ("logs", "output", "coverage"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    for name, report in clean_reports.items():
        report.write(evidence / "output" / name, encoding="UTF-8", xml_declaration=True)
    for module, directory in (("web", "src/schubert-nk-web"), ("protocol", "src/schubert-nk-protocol")):
        for suffix in ("csv", "xml"):
            shutil.copyfile(repo / directory / "target/site/jacoco" / ("jacoco." + suffix),
                            evidence / "coverage" / (module + "-jacoco." + suffix))
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                         "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MED-001", "programStatus": "IN_PROGRESS",
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods, "actual": "All seven independent assertion sets passed",
        "inputAndExpected": "001 PT specification and targetCommit's three named test classes: SS333 literal Range intervals/416 and 1MiB cap, literal UTF-8 percent header strings, independently patterned bytes and exact array slices. Production is never used to generate expected values.",
        "scope": "Pure Range selection/header factory and bounded copy only; not an authenticated HTTP delivery or a manifest/file-integrity check. Query/descriptor/auth/Inbox/secure asset resolver/20 permits/HTTP HEAD-download/full startup/actual NK CHR remain unimplemented or unconnected.",
        "relatedBug": [], "relatedSsc": [], "crossProgramRegressions": ["BUG-040/YKT-036 in 003 manifest"],
        "notRunCountedAsPass": 0, "redaction": "JUnit names/timing/counters only; no properties/stdout/stderr or raw logs/paths/credentials/master content.",
    })
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (evidence / "checksums.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
                                                     for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
