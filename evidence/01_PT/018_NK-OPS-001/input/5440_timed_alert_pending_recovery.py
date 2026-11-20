"""Run the fixed BUG-3415 monitoring tests without external inputs."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree

PACKAGE = "dev.codex.schubert.nk.batch.monitoring"
MODULE = Path("src/schubert-nk-batch/src")
PRODUCTION = MODULE / "main/java" / PACKAGE.replace(".", "/")
TEST = MODULE / "test/java" / PACKAGE.replace(".", "/")
MAIN_NAMES = (
    "AlertLifecycle", "AlertRegistry", "AlertThresholds", "ContinuousConditionWindow",
    "MonitoringModePolicy", "MonitoringPolicyEngine", "ObservationContext",
    "TimedDbPoolMonitor", "TimedFilesystemMonitor", "TimedJvmHeapMonitor", "TimedSyncLatencyMonitor",
    "package-info",
)
NEW_SUITE = "TimedAlertPendingRecoveryTest"
PRIOR_SUITES = (
    "AlertLifecycleTest", "AlertRegistryTest", "AlertThresholdsTest",
    "MonitoringPolicyEngineTest", "TimedDbPoolMonitorTest",
    "TimedFilesystemMonitorTest", "TimedJvmHeapMonitorTest", "TimedSyncLatencyMonitorTest",
)
CASES = dict(zip((
    "timedSyncLatencyDoesNotRecoverWhileLatencyRemainsAboveTwoSeconds",
    "timedFilesystemDoesNotRecoverWhileUsageRemainsAtEightyPercent",
    "timedHeapDoesNotRecoverWhileUsageRemainsAtSeventyFivePercent",
    "timedDbPoolDoesNotRecoverWhileUsageRemainsAtEightyPercent",
    "policySyncLatencyDoesNotCountPendingWarningAsRecovery",
    "policyFilesystemDoesNotCountPendingWarningAsRecovery",
    "policyHeapDoesNotCountPendingWarningAsRecovery",
    "policyDbPoolDoesNotCountPendingWarningAsRecovery",
), (f"PT-TIMED-RECOVERY-{i:03}" for i in range(1, 9))))


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {"path": str(path), "sha256": sha(path.read_bytes())}


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("before", "after"))
    parser.add_argument("source")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = git("rev-parse", args.source).decode().strip()
    is_after = args.phase == "after"
    suites = (NEW_SUITE, *PRIOR_SUITES) if is_after else (NEW_SUITE,)
    production_names = (*MAIN_NAMES, "MonitoringStatusText") if is_after else MAIN_NAMES
    main_paths = [PRODUCTION / f"{name}.java" for name in production_names]
    fixture = [TEST / f"{name}.java" for name in suites]
    for path in main_paths + (fixture if is_after else []):
        assert path.read_bytes() == git("show", f"{source}:{path}"), path
    toolchain = Path.cwd().parent / "toolchain"
    java = toolchain / "jdk-25.0.4/bin/java"
    javac = toolchain / "jdk-25.0.4/bin/javac"
    junit = toolchain / "junit-platform-console-standalone-1.13.4.jar"
    jsp = toolchain / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
    style = toolchain / "static-gates-20261015/checkstyle-14.3.0-all.jar"
    rules = Path("tools/quality/static/checkstyle.xml")
    formatter = toolchain / "google-java-format-1.36.1-all-deps.jar"
    agent = toolchain / "m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    jacoco = toolchain / "org.jacoco.cli-0.8.15-nodeps.jar"
    steps, observed_cases = {}, []
    result, coverage = 1, None
    terminal_tests = "NOT_RUN"
    started = now()
    args.output.mkdir()
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}

    def run(label, *values):
        cmd = list(map(str, values))
        execution = subprocess.run(cmd, capture_output=True, env=env, timeout=75)
        steps[label] = {"command": cmd, "exit": execution.returncode,
                        "stdoutSha256": sha(execution.stdout), "stderrSha256": sha(execution.stderr)}
        if execution.returncode and label != "unit":
            print(label, execution.returncode, execution.stderr.decode(errors="replace")[:1500])
        return execution.returncode

    with tempfile.TemporaryDirectory(prefix="pg40798-", dir="/dev/shm") as directory:
        tmp = Path(directory)
        product, tests = tmp / "product", tmp / "tests"
        product.mkdir()
        tests.mkdir()
        check_xml = tmp / "checkstyle.xml"
        runtime_data = tmp / "coverage.exec"
        coverage_xml = tmp / "coverage.xml"
        assert len(main_paths) == (13 if is_after else 12)
        style_paths = [*main_paths, fixture[0]] if is_after else fixture
        if (run("formatter", java, "-jar", formatter, "--skip-reflowing-long-strings",
                "--dry-run", "--set-exit-if-changed", *style_paths) == 0
            and run("checkstyle", java, "-jar", style, "-c", rules, "-f", "xml",
                    "-o", check_xml, *style_paths) == 0
            and run("mainCompile", javac, "--release", 25, "-Xlint:all", "-Werror",
                    "-g", "-proc:none", "-cp", jsp, "-d", product, *main_paths) == 0
            and run("testCompile", javac, "--release", 25, "-Xlint:all", "-Werror", "-g",
                    "-proc:none", "-cp", f"{product}:{junit}:{jsp}", "-d", tests, *fixture) == 0):
            assert not ElementTree.parse(check_xml).getroot().findall(".//error")
            report_dir = tmp / "reports"
            selectors = [value for suite in suites for value in ("--select-class", f"{PACKAGE}.{suite}")]
            agent_args = [f"-javaagent:{agent}=destfile={runtime_data},append=false,sessionid=PG40798"]
            result = run("unit", java, *(agent_args if is_after else []), "-jar", junit, "execute",
                         "--disable-banner", "--disable-ansi-colors", "--class-path", f"{product}:{tests}:{jsp}",
                         *selectors, "--reports-dir", report_dir, "--fail-if-no-tests")
            test_xml = report_dir / "TEST-junit-jupiter.xml"
            if test_xml.is_file():
                steps["unit"]["xmlSha256"] = sha(test_xml.read_bytes())
                for case in ElementTree.parse(test_xml).getroot().findall("testcase"):
                    row = case.attrib
                    clazz = row["classname"].rsplit(".", 1)[-1]
                    method = row["name"].removesuffix("()")
                    assert clazz in suites
                    test_id = CASES[method] if clazz == NEW_SUITE else f"{clazz}.{method}"
                    failed = next((tag for tag in ("failure", "error", "skipped") if case.find(tag) is not None), None)
                    evidence = dict(testId=test_id, method=method, suite=clazz, status=failed or "passed")
                    if failed:
                        failure = case.find(failed)
                        evidence["type"] = failure.attrib.get("type")
                        evidence["assertion"] = failure.attrib.get("message")
                    observed_cases.append(evidence)
            new_cases = [case for case in observed_cases if case["suite"] == NEW_SUITE]
            assert {case["testId"] for case in new_cases} == set(CASES.values())
            if is_after and result == 0:
                assert all(case["status"] == "passed" for case in observed_cases)
                terminal_tests = "PASS"
                result = run("coverage", java, "-jar", jacoco, "report", runtime_data,
                             "--classfiles", product, "--xml", coverage_xml)
                if result == 0:
                    document = ElementTree.parse(coverage_xml).getroot()
                    assert [x.attrib["id"] for x in document.findall("sessioninfo")] == ["PG40798"]
                    coverage = {x.attrib["type"]: dict(covered=int(x.attrib["covered"]), missed=int(x.attrib["missed"]))
                                for x in document.findall("counter")}
                    steps["coverage"]["xmlSha256"] = sha(coverage_xml.read_bytes())
            elif not is_after and result == 1:
                assert len(new_cases) == 8
                assert all(case["type"] == "org.opentest4j.AssertionFailedError"
                           and case["assertion"] == "expected: <true> but was: <false>" for case in new_cases)
                terminal_tests = "EXPECTED_REGRESSION_REPRODUCED"
            else:
                terminal_tests = "UNEXPECTED"
    record = dict(actualExit=result,source=source,phase=args.phase,startedAtUTC=started,terminalAtUTC=now(),
                  testState=terminal_tests,relatedBug="BUG-3415",relatedYkt="YKT-2738",
                  inputs=[ref(path) for path in [*main_paths,*fixture]],steps=steps,cases=observed_cases,
                  selectedJaCoCoDefaultCoverage=coverage,productionFullCoverage=None,
                  externalOperations=0,formalDelta=0,whole451=False)
    m = args.output / "manifest.json"
    m.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
    print(terminal_tests,len(observed_cases),result,sha(m.read_bytes()), coverage)
    return 0 if (result == 0 if is_after else terminal_tests == "EXPECTED_REGRESSION_REPRODUCED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
