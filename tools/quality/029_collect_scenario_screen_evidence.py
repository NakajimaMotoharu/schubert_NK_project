#!/usr/bin/env python3
"""PG194: certify Scenario hierarchy HTTP slice, never the complete Web/PGPT phase."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

CLASS = "dev.codex.schubert.nk.web.session.ScenarioControllerTest"
DETAIL_CLASS = "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest"
SCRIPT_CLASS = "dev.codex.schubert.nk.web.view.ScenarioSearchScriptTest"
SCRIPT_PATH = "src/schubert-nk-web/src/main/resources/static/js/search-speaker-submit.js"
DETAIL_METHODS = ("detail017HeaderAndCommonLayout", "detail018PreviousNext", "detail019EntriesAndVoices",
                  "detail020EmptyScenario", "detail021HtmlAndUrlSafety", "detail022MaximumRecordsAndVoices",
                  "detail023CssAndViewBoundary", "detail024ConcurrentRendering")
METHODS = ("screens001GamesSuccess", "screens002RoutesSuccess", "screens003FilesSuccess",
           "screens004EmptyHierarchy", "screens005AllResultCodes", "screens006InvalidSessionTerminal",
           "screens007WireAndBindingFailure", "screens008NullAndForeignPrincipal",
           "screens009ClosedRoutesAndRequests", "screens010RealTemplatesAndNavigation",
           "screens011HtmlEscaping", "screens012CompatibilityObservations", "screens013ConcurrentQueries",
           "screens014FailurePropagation", "screens015MvcConfiguration", "screens016RealHttpSecurityAndTerminal")
SUBJECTS = ("dev/codex/schubert/nk/web/controller/ScenarioController",
            "dev/codex/schubert/nk/web/config/ScenarioMvcConfiguration",
            "dev/codex/schubert/nk/web/config/WebMvcConfiguration")
TRACES = {"PT-SCR-012.txt": b"cases=CHR-S05|CHR-S06\nfixture=public-synthetic\ngames=2\nroutes=2\nfiles=2\norderAndText=PASS\nactualNkGate=false\n",
          "PT-SCR-024.txt": b"template=scenario\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumEntries=10000\nmaximumVoices=999\nactualNkGate=false\n"}
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
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/EmbeddedWebSecurityTest.java",
    "src/schubert-nk-web/src/main/resources/templates/scenario.html",
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/ScenarioDetailViewModel.java",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioDetailTemplateTest.java",
    SCRIPT_PATH,
    "src/schubert-nk-web/src/test/javascript/search-speaker-submit.test.cjs",
    "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioSearchScriptTest.java")


def validate_suite(suite, detail=False):
    classname, methods, first = (DETAIL_CLASS, DETAIL_METHODS, 17) if detail else (CLASS, METHODS, 1)
    return validate_named_suite(suite, classname, methods, first)


def validate_script_suite(suite):
    return validate_named_suite(suite, SCRIPT_CLASS, ("search025BrowserInputScript",), 25)


def validate_named_suite(suite, classname, methods, first):
    cases = suite.findall("testcase")
    names = [case.get("name") for case in cases]
    if (suite.get("name") != classname or suite.get("tests") != str(len(methods))
            or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
            or len(names) != len(methods) or len(set(names)) != len(methods) or set(names) != set(methods)
            or any(case.get("classname") != classname or
                   any(child.tag not in ("system-out", "system-err") for child in case) for case in cases)):
        raise ValueError("missing or nonpassing hierarchy screen tests")
    return {f"PT-SCR-{i:03}": classname + "#" + name for i, name in enumerate(methods, first)}


def validate_script_trace(trace, script_hash):
    expected = {"testId": "PT-SCR-025", "nodeVersion": "v24.19.0", "subcases": 8,
                "failed": 0, "skipped": 0, "todo": 0, "syntaxExit": 0, "testExit": 0,
                "lineCoverage": 100, "functionCoverage": 100, "branchCoverage": 100,
                "productionFiles": 1, "scriptSha256": script_hash,
                "browserDom": "deterministic-event-double", "actualNkGate": False}
    if trace != expected or any(type(trace[key]) is not type(value) for key, value in expected.items()):
        raise ValueError("invalid or incomplete browser script evidence")


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
    methods.update(validate_suite(ET.parse(target / "surefire-reports" / ("TEST-" + DETAIL_CLASS + ".xml")).getroot(), True))
    methods.update(validate_script_suite(ET.parse(target / "surefire-reports" / ("TEST-" + SCRIPT_CLASS + ".xml")).getroot()))
    script_trace = json.loads((target / "pt-search-script/PT-SCR025-node.json").read_text())
    validate_script_trace(script_trace, digest(repo / SCRIPT_PATH))
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
    (evidence / "output/PT-SCR025-node.json").write_text(json.dumps(script_trace, indent=2) + "\n")
    for name in ("001_NK-WEB-002_Scenario階層画面単体テスト仕様書.md", "002_NK-WEB-002_Scenario階層画面実行結果.md",
                 "003_NK-WEB-002_Scenario本文template単体テスト仕様書.md", "004_NK-WEB-002_Scenario本文template実行結果.md",
                 "005_NK-WEB-002_検索ブラウザ入力単体テスト仕様書.md", "006_NK-WEB-002_検索ブラウザ入力実行結果.md"):
        (evidence / "logs" / name).write_bytes((program / name).read_bytes())
    suite = ET.Element("testsuite", name="NK-WEB-002-screen-slices", tests="25", failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(suite, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(suite).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    (evidence / "coverage").mkdir(exist_ok=True)
    (evidence / "coverage/class-counters.json").write_text(json.dumps(coverage, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt",
                "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-WEB-002", "scopeResult": "PASS_HIERARCHY_HTTP_DETAIL_TEMPLATE_SEARCH_SCRIPT_ONLY", "programComplete": False,
        "javascript": script_trace,
        "javascriptCommand": {
            "cwd": "src/schubert-nk-web",
            "syntax": ["/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node", "--check", str(repo / SCRIPT_PATH)],
            "test": ["/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node", "--test", "--experimental-test-coverage",
                     "--test-reporter=tap", "--test-coverage-lines=100", "--test-coverage-functions=100", "--test-coverage-branches=100",
                     "--test-coverage-include=" + str(repo / SCRIPT_PATH),
                     str(repo / "src/schubert-nk-web/src/test/javascript/search-speaker-submit.test.cjs")]},
        "javascriptOracle": "005/PT-SCR025-A..H:8 Node cases inside1 JUnit, independent DOM event double and literals for missing structure,UTF8/NFC/ASCII trim/Unicode controls/surrogates/BOM/byte boundaries,all errors,input recovery and native requestSubmit. Exact Production1file coverage inclusion,syntax/version/exit/skipped/todo checks. Not live Browser/HTTP certificate.",
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0, "classCoverage": coverage,
        "coverageNotes": "Only configuration classes have zero conditional branches; controller branches all covered. No exclusion. Template condition/iteration/text branches verified by SCR001..024. SCR025 executes8 Node subcases; JavaScript1file line/function/branch100, no JS class declaration and no exclusion; not8 additional JUnit tests.",
        "staticAnalysis": verified["modules"]["web"]["spotbugs"],
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["PG-D-194", "PG-D-195", "PG-D-196", "PG-D-201", "SSC-071", "SSC-072", "BUG-213", "BUG-214", "BUG-215", "YKT-169", "YKT-170", "YKT-171"],
        "fixture": "Public synthetic independent UI232/234 byte vectors, isolated PostgreSQL encrypted sessions, loopback Tomcat and actual security/MVC. No raw session/cookie/token or master data saved.",
        "oracle": "001/SCR001..016: explicit status/DOM/order/URLs,0/max/null/foreign identity,all result codes,SCF binding,0102 terminal,100 concurrent correlations,unknown failure identity.012 is a synthetic display projection comparison, not the actual NK CHR gate.",
        "detailTemplateOracle": "003/SCR017..024: Production scenario template via resolver, independent heading/navigation/entry/audio/URLs,0/10000 entries/999 voices,all conditionals,escaping,64 renders and full new CSS declaration table/900px/target highlighting. Not a browser screenshot or a registered detail HTTP endpoint.",
        "limitations": "No detail controller/file port/readiness binding/final bootstrap/live broker/full screens/production request logging/actual NK CHR/IT/ST certificate.",
        "sourceFiles": [{"path": path, "sha256": digest(repo / path)} for path in SOURCE_PATHS]})
    manifest["files"] = [{"path": str(path.relative_to(evidence)), "sha256": digest(path)}
                         for path in sorted(evidence.rglob("*")) if path.is_file()
                         and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (evidence / "checksums.sha256").write_text("".join(
        digest(path) + "  " + str(path.relative_to(evidence)) + "\n"
        for path in sorted(evidence.rglob("*")) if path.is_file() and path.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": len(methods), "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
