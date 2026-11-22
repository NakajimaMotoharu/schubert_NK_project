#!/usr/bin/env python3
"""PG188: public receipt identifier slice; never a Question acceptance certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

CLASS = "dev.codex.schubert.nk.api.application.question.QuestionReceiptIdTest"
METHODS = ("exactAlphabet", "lengthBoundaries", "characterBoundaries", "independentRandomVector",
           "randomFailure", "nullAndFactory", "concurrentCalls", "equalityAndPublicEvidence")
SUBMIT_CLASS = "dev.codex.schubert.nk.api.application.question.QuestionSubmitRequestTest"
SUBMIT_METHODS = ("literalWireAndCanonical", "byteAndUnicodeBoundaries", "protocolRejection",
                  "fingerprintBinding", "ownershipAndClose", "nullContracts", "concurrentScopes",
                  "publicEvidenceAndRedaction")
SUBJECTS = tuple("dev/codex/schubert/nk/api/application/question/" + name
                 for name in ("QuestionReceiptId", "QuestionReceiptIdGenerator", "QuestionSubmitRequest"))
TRACES = {"PT-QST-RID008.txt": b"forward=0123456789ABCDEFGHJKMNPQRS\nreverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\nrandomDrawsPerId=26\nownerOrTimeInput=false\n"}
TRACES["PT-QST-SUB008.txt"] = b"layout=QSBREQ01\ninteraction=A\ndataLength=4144\ncanonicalFieldCount=1\ncanonicalField=question/X1\ntarget=QUESTION:NEW\nmetadataExcluded=true\nrawBodySaved=false\n"


def validate_suite(suite):
    cls = suite.get("name")
    if cls not in (CLASS, SUBMIT_CLASS):
        raise ValueError("unknown question test class")
    expected = METHODS if cls == CLASS else SUBMIT_METHODS
    prefix = "RID" if cls == CLASS else "SUB"
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("tests") != "8"
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != 8 or len(set(names)) != 8 or set(names) != set(expected)
            or any(case.get("classname") != cls or
                   any(child.tag not in ("system-out", "system-err") for child in case) for case in cases)):
        raise ValueError("missing or nonpassing receipt identifier tests")
    return {f"PT-QST-{prefix}{i:03}": cls + "#" + name for i, name in enumerate(expected, 1)}


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("missing, additional or invalid receipt trace")


def validate_coverage(report):
    result = {}
    for cls in report.iter("class"):
        if cls.get("name") in SUBJECTS:
            result[cls.get("name")] = {counter.get("type"): {
                "missed": int(counter.get("missed")), "covered": int(counter.get("covered"))
            } for counter in cls.findall("counter")}
    if set(result) != set(SUBJECTS) or any(
            not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
            or any(value["missed"] for value in counters.values()) for counters in result.values()):
        raise ValueError("missing or incomplete receipt coverage")
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
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    methods = {}
    for cls in (CLASS, SUBMIT_CLASS):
        methods.update(validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + cls + ".xml")).getroot()))
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    traces = {}
    for folder in ("question-receipt-traces", "question-submit-traces"):
        trace_root = target / folder
        for path in trace_root.rglob("*"):
            if path.is_file():
                name = str(path.relative_to(trace_root))
                if name in traces:
                    raise ValueError("duplicate question trace")
                traces[name] = path.read_bytes()
    validate_traces(traces)
    program = repo / "evidence/01_PT/011_NK-QST-001"
    evidence = program / "evidence"
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    (evidence / "logs").mkdir(exist_ok=True)
    for name in ("001_NK-QST-001_受付ID単体テスト仕様書.md", "002_NK-QST-001_受付ID実行結果.md",
                 "003_NK-QST-001_質問送信入力単体テスト仕様書.md", "004_NK-QST-001_質問送信入力実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    suite = ET.Element("testsuite", name="NK-QST-001-input", tests="16", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/java" / (subject + ".java") for subject in SUBJECTS]
    sources += [repo / "src/schubert-nk-api/src/test/java" / (cls.replace(".", "/") + ".java") for cls in (CLASS, SUBMIT_CLASS)]
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-QST-001", "scopeResult": "PASS_QUESTION_INPUT_BOUNDARIES_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0, "classCoverage": coverage,
        "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["PG-D-188", "PG-D-189", "SSC-070", "BUG-211", "YKT-167"],
        "fixture": "Public literal alphabet/index vectors; no real user IDs or credentials.",
        "oracle": "001/RID001..008:32 permitted letters at every leading value; exact26 length, all forbidden ASCII at26 positions; independent forward/reverse vectors and16 fixed cyclic values in64 concurrent calls, every26 provider failure position, invalid provider index and null contracts. Factory uses SecureRandom; no probabilistic uniqueness assertion.",
        "limitations": "No DB uniqueness/retry, owner authorization, Submit/Outbox/Inbox replay, async worker, actual NK CHR or IT/ST certification.",
        "sourceFiles": [{"path": str(path.relative_to(repo)), "sha256": digest(path)} for path in sources]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": 16, "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
