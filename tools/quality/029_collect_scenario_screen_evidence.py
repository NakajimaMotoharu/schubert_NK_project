#!/usr/bin/env python3
"""PG194: certify Scenario hierarchy HTTP slice, never the complete Web/PGPT phase."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

CLASS = "dev.codex.schubert.nk.web.session.ScenarioControllerTest"
METHODS = ("screens001GamesSuccess", "screens002RoutesSuccess", "screens003FilesSuccess",
           "screens004EmptyHierarchy", "screens005AllResultCodes", "screens006InvalidSessionTerminal",
           "screens007WireAndBindingFailure", "screens008NullAndForeignPrincipal",
           "screens009ClosedRoutesAndRequests", "screens010RealTemplatesAndNavigation",
           "screens011HtmlEscaping", "screens012CompatibilityObservations", "screens013ConcurrentQueries",
           "screens014FailurePropagation", "screens015MvcConfiguration", "screens016RealHttpSecurityAndTerminal")
SUBJECTS = ("dev/codex/schubert/nk/web/controller/ScenarioController",
            "dev/codex/schubert/nk/web/config/ScenarioMvcConfiguration",
            "dev/codex/schubert/nk/web/config/WebMvcConfiguration")
TRACES = {"PT-SCR-012.txt": b"cases=CHR-S05|CHR-S06\nfixture=public-synthetic\ngames=2\nroutes=2\nfiles=2\norderAndText=PASS\nactualNkGate=false\n"}
SOURCE_PATHS = (
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/ScenarioController.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/ScenarioMvcConfiguration.java",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/WebMvcConfiguration.java",
    "src/schubert-nk-web/src/main/resources/templates/scenarios.html",
    "src/schubert-nk-web/src/main/resources/templates/scenario-routes.html",
    "src/schubert-nk-web/src/main/resources/templates/scenario-files.html",
    "src/schubert-nk-web/src/main/resources/templates/fragments/layout.html",
    "src/schubert-nk-web/src/main/resources/static/css/schubert.css",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ScenarioControllerTest.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ApiSessionInvalidTest.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/EmbeddedWebSecurityTest.java")


def validate_suite(suite):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != CLASS or suite.get("tests") != "16"
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != 16 or len(set(names)) != 16 or set(names) != set(METHODS)
            or any(case.get("classname") != CLASS or
                   any(child.tag not in ("system-out", "system-err") for child in case) for case in cases)):
        raise ValueError("missing or nonpassing hierarchy screen tests")
    return {f"PT-SCR-{i:03}": CLASS + "#" + name for i, name in enumerate(METHODS, 1)}


def validate_traces(traces):
    if traces != TRACES:
        raise ValueError("invalid hierarchy screen trace")


def validate_coverage(report):
    result = {}
    for cls in report.iter("class"):
        if cls.get("name") in SUBJECTS:
            counters = {counter.get("type"): {
                "missed": int(counter.get("missed")), "covered": int(counter.get("covered"))
            } for counter in cls.findall("counter")}
            # Only the two explicit composition classes are branchless; no exclusion.
            if cls.get("name") in SUBJECTS[1:]:
                counters.setdefault("BRANCH", {"missed": 0, "covered": 0})
            result[cls.get("name")] = counters
    if set(result) != set(SUBJECTS) or any(
            not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
            or any(value["missed"] for value in counters.values())
            or any(counters[kind]["covered"] <= 0 for kind in ("LINE", "METHOD", "CLASS"))
            for counters in result.values()) or result[SUBJECTS[0]]["BRANCH"]["covered"] <= 0:
        raise ValueError("missing or incomplete hierarchy screen coverage")
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
    target = repo / "src/schubert-nk-web/target"
    methods = validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + CLASS + ".xml")).getroot())
    coverage = validate_coverage(ET.parse(target / "site/jacoco/jacoco.xml").getroot())
    trace_root = target / "scenario-screen-traces"
    traces = {str(path.relative_to(trace_root)): path.read_bytes() for path in trace_root.rglob("*") if path.is_file()}
    validate_traces(traces)
    program = repo / "evidence/01_PT/016_NK-WEB-002"
    evidence = program / "evidence"
    for folder, values in (("input", TRACES), ("output", traces)):
        directory = evidence / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (directory / name).write_bytes(value)
    (evidence / "logs").mkdir(exist_ok=True)
    for name in ("001_NK-WEB-002_Scenario階層画面単体テスト仕様書.md", "002_NK-WEB-002_Scenario階層画面実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    suite = ET.Element("testsuite", name="NK-WEB-002-hierarchy", tests="16", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=CLASS, name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage").mkdir(exist_ok=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-WEB-002", "scopeResult": "PASS_SCENARIO_HIERARCHY_HTTP_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0, "classCoverage": coverage,
        "coverageNotes": "Only configuration classes have zero conditional branches; controller branches all covered. No exclusion. Template condition/iteration/text branches verified by SCR001..016.",
        "staticAnalysis": verified["modules"]["web"]["spotbugs"],
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["PG-D-194", "SSC-071", "BUG-213", "BUG-214", "BUG-215", "YKT-169", "YKT-170", "YKT-171"],
        "fixture": "Public synthetic independent UI232/234 byte vectors, isolated PostgreSQL encrypted sessions, loopback Tomcat and actual security/MVC. No raw session/cookie/token or master data saved.",
        "oracle": "001/SCR001..016: explicit status/DOM/order/URLs,0/max/null/foreign identity,all result codes,SCF binding,0102 terminal,100 concurrent correlations,unknown failure identity.012 is a synthetic display projection comparison, not the actual NK CHR gate.",
        "limitations": "No final bootstrap/live broker/full screens/production request logging/actual NK CHR/IT/ST certificate.",
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCE_PATHS]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (evidence / "checksums.sha256").write_text("".join(
        digest(path) + "  " + str(path.relative_to(evidence)) + "\n"
        for path in sorted(evidence.rglob("*")) if path.is_file() and path.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": 16, "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
