#!/usr/bin/env python3
"""Certify executed Web PT IDs against the verified full reactor; omit raw session and JVM data."""

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
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json").read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("collect the matching full verified reactor first")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    expected = {}
    groups = {
        "dev.codex.schubert.nk.web.session.WebSessionIdTest": (
            (1, "web001CanonicalIdsAndIndependentHashes"),
            (2, "web002NullLengthAlphabetAndUnusedBitsReject"),
            (3, "web003GenerationOwnsAndErasesRandomBuffers"),
            (4, "web004ConcurrentIdsAndHashesShareNoMutableDigest")),
        "dev.codex.schubert.nk.web.security.SavedRequestTargetTest": (
            (5, "web005SafeGetTargetsPreservePathAndQuery"),
            (6, "web006ExternalMalformedAndStateChangingTargetsReject"),
            (7, "web007Utf8LimitAndUnicodeBoundariesAreExact"),
            (8, "web008ConcurrentTargetsRemainIndependent")),
    }
    methods, reports = [], {}
    for classname, cases in groups.items():
        expected.update({f"PT-WEB-{i:03d}": classname + "#" + name for i, name in cases})
        report = repo / "src/schubert-nk-web/target/surefire-reports" / ("TEST-" + classname + ".xml")
        suite = ET.parse(report).getroot()
        actual = suite.findall("testcase")
        if any(int(suite.get(key, "0")) for key in ("errors", "failures", "skipped")):
            raise SystemExit("nonpassing Web PT")
        if int(suite.get("tests", "0")) != len(actual):
            raise SystemExit("inconsistent Web PT count")
        clean = ET.Element("testsuite", {key: suite.get(key) for key in
                                        ("name", "time", "tests", "errors", "failures", "skipped")})
        for case in actual:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("failed/skipped/flaky/rerun Web case")
            attributes = {key: case.get(key) for key in ("name", "classname", "time")}
            methods.append(attributes["classname"] + "#" + attributes["name"])
            ET.SubElement(clean, "testcase", attributes)
        ET.indent(clean)
        reports[report.name] = ET.ElementTree(clean)
    if set(methods) != set(expected.values()) or len(methods) != len(expected):
        raise SystemExit("Web Test IDs do not exactly cover executed methods")
    evidence = repo / "evidence/01_PT/015_NK-WEB-001/evidence"
    for name in ("logs", "output", "coverage"):
        (evidence / name).mkdir(parents=True, exist_ok=True)
    for name, report in reports.items():
        report.write(evidence / "output" / name, encoding="UTF-8", xml_declaration=True)
    for suffix in ("csv", "xml"):
        shutil.copyfile(repo / "src/schubert-nk-web/target/site/jacoco" / ("jacoco." + suffix),
                        evidence / "coverage" / ("web-jacoco." + suffix))
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                              "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-WEB-001", "programStatus": "IN_PROGRESS",
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods,
        "inputAndExpected": "PT-WEB-001..008 / PG-D-093: synthetic 32-byte zero/sequence/FF CSPRNG data with independent Python base64/hashlib fixed vectors; canonical unpadded43-character base64url and raw-ASCII SHA256 lookup, temporary random/decode/hash arrays erased. Null/length/alphabet/padding/unused-bits negatives, provider failure and100 concurrent random IDs/per-call hashes. Explicit GET URL strings preserve path/query/Unicode and valid query escapes with no trim/decode; reject schemes/authority/fragment/malformed/control/dot-segments/encoded path delimiters and nonGET. Exact2047/2048/2049 UTF8-byte, malformed surrogate and100 independent query cases. toString and validation errors contain no values.",
        "actual": "All mapped independent assertion sets passed; no failed/skipped/flaky/not-run counted",
        "scope": "Web value boundary only. Session encryption/JSON/repository/fixation/CSRF/security/SavedRequest route allowlist/HTTP/startup/actual NK Characterization remain required and incomplete; no IT/ST claim.",
        "relatedBug": [], "relatedSsc": [], "relatedYkt": [],
        "notRunCountedAsPass": 0,
        "redaction": "Only allowlisted method names/timing/counters/coverage and metadata. No JVM properties/stdout/stderr, raw cookie/session/context/token/key or database dump.",
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
