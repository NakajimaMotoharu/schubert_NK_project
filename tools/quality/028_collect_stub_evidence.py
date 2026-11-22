#!/usr/bin/env python3
"""PG190 / BUG-3600: verified empty-answer provider and fixed failure value."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root

CLASS = "dev.codex.schubert.nk.api.application.question.StubAnswerProviderTest"
METHODS = ("emptyAnswerAndClock", "nullContracts", "clockFailures", "resultValueAndRedaction",
           "concurrentCallsAndEvidence", "fixedBusinessFailureValue")
SUBJECTS = tuple("dev/codex/schubert/nk/api/application/question/" + name
                 for name in ("AnswerResult", "StubAnswerProvider", "AnswerBusinessException"))
TRACE = b"provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n"
TRACES = {"PT-ASY-STB005.txt": TRACE}


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != str(len(METHODS))
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != len(METHODS) or set(names) != set(METHODS)
            or any(case.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case) for case in cases)):
        raise ValueError("missing or nonpassing stub tests")
    return {f"PT-ASY-STB{i:03}": CLASS + "#" + name for i, name in enumerate(METHODS, 1)}


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("invalid stub trace")


def validate_coverage(report):
    result = {}
    for cls in report.iter("class"):
        if cls.get("name") in SUBJECTS:
            counters = {counter.get("type"): {
                "missed": int(counter.get("missed")), "covered": int(counter.get("covered"))
            } for counter in cls.findall("counter")}
            # The three executable classes contain no conditional instructions.
            counters.setdefault("BRANCH", {"missed": 0, "covered": 0})
            result[cls.get("name")] = counters
    if set(result) != set(SUBJECTS) or any(
            not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
            or any(value["missed"] for value in counters.values())
            or any(counters[kind]["covered"] <= 0 for kind in ("LINE", "METHOD", "CLASS"))
            for counters in result.values()):
        raise ValueError("missing or incomplete stub coverage")
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = evidence_output_root(repo) / "008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    trace_root = target / "question-stub-traces"
    traces = {str(path.relative_to(trace_root)): path.read_bytes() for path in trace_root.rglob("*") if path.is_file()}
    validate_traces(traces)
    program = repo / "evidence/01_PT/012_NK-ASY-001"
    evidence = evidence_output_root(repo) / "012_NK-ASY-001/evidence"
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    (evidence / "logs").mkdir(exist_ok=True)
    for name in ("001_NK-ASY-001_空回答provider単体テスト仕様書.md", "002_NK-ASY-001_空回答provider実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    suite = ET.Element("testsuite", name="NK-ASY-001-stub", tests=str(len(methods)),
                       failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS, name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/java" / (subject + ".java") for subject in SUBJECTS]
    sources += [repo / "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/AnswerProvider.java",
                repo / "src/schubert-nk-api/src/test/java" / (CLASS.replace(".", "/") + ".java")]
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-ASY-001", "scopeResult": "PASS_STUB_PROVIDER_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0, "classCoverage": coverage,
        "coverageNotes": "The three executable classes have zero conditional branches (0/0). "
                         "AnswerProvider contains only its abstract method.",
        "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["PG-D-190", "BUG-3600"],
        "fixture": "Public synthetic question and fixed/atomic test Clock; no real question or secret.",
        "oracle": "STB001..006: empty string, literal Instant, clock failures, record values, "
                  "64 concurrent clock observations, and the fixed business failure with no cause or suppression.",
        "limitations": "No worker DB state, JMS acknowledgment, FIFO delivery, external AI, actual NK CHR or IT/ST certificate.",
        "sourceFiles": [{"path": str(path.relative_to(repo)), "sha256": digest(path)} for path in sources]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": len(methods), "scopeResult": manifest["scopeResult"],
                      "programComplete": False}))


if __name__ == "__main__":
    main()
