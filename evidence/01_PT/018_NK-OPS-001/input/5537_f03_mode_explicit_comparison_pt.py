"""Build and test the changed mode policy and its admitted pure fixture closure."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(p):
    return dict(path=str(p), sha256=sha256(p.read_bytes()).hexdigest())


def json_file(path, value):
    with path.open("x") as out:
        out.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


BASE = "dev/codex/schubert/nk/batch"
PACKAGE = BASE.replace("/", ".") + ".monitoring."
SUPPORT = (
    "AlertLifecycle", "AlertRegistry", "AlertThresholds", "MonitoringPolicyEngine",
    "ObservationContext", "BatchMetricContract", "MetricContract", "ContinuousConditionWindow",
    "TransferMetricRecorder", "TransferHealthMonitor", "TimedFilesystemMonitor",
    "TimedJvmHeapMonitor", "TimedDbPoolMonitor", "TimedSyncLatencyMonitor", "MonitoringPoller",
    "MonitoringObservationClock", "FilesystemHealthObservation", "JvmHeapHealthObservation",
    "HealthUsageRatio",
)
SUITES = ("MonitoringModePolicyTest", "MonitoringRetentionConfigurationTest",
          "GeneratedBatchValueContractTest", "MonitoringPolicyEngineTest")


def main():
    checkpoint = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1440_*.json"))
    start = json.loads(checkpoint.read_bytes())
    v = start["values"]
    refs = v["oracleReferences"]
    assert all(pin(Path(row["path"])) == row for row in refs)
    before, engine, original = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:4]]
    assert before["actualExit"] == engine["actualExit"] == original["actualExit"] == 0
    source = "af6db98d62e83ed4dd19d623034373365027dce3"
    assert not subprocess.check_output(["git", "diff", "--name-only", source, "HEAD", "--", "src", "pom.xml"])
    project = Path("src/schubert-nk-batch/src")
    prefix = project / "main/java" / BASE
    target = prefix / "monitoring/MonitoringModePolicy.java"
    package = target.parent / "package-info.java"
    support = [target.parent / (name + ".java") for name in SUPPORT]
    support.append(prefix / "repository/BatchStep.java")
    fixtures = [project / "test/java" / BASE / "monitoring" / (name + ".java") for name in SUITES]
    paths = [target, package, *support, *fixtures]
    assert subprocess.check_output(["git", "diff", "--name-only", v["source"], source, "--", "src"],
                                   text=True).splitlines() == [str(target)]
    for path in paths:
        assert subprocess.check_output(["git", "show", f"{source}:{path}"]) == path.read_bytes()

    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    java, javac = (jdk / "bin" / tool for tool in ("java", "javac"))
    junit = tc / "junit-platform-console-standalone-1.13.4.jar"
    agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    deps = original["begin"]["dependencyHashes"]
    jspecify, = [Path(p) for p in deps if p.endswith("jspecify-1.0.1.jar")]
    sdk = [Path(path) for path in sorted(deps) if path.endswith((
        "micrometer-core-1.17.1.jar", "micrometer-commons-1.17.1.jar",
        "micrometer-observation-1.17.1.jar"))]
    assert len(sdk) == 3 and all(pin(p)["sha256"] == deps[str(p)] for p in (jspecify, *sdk))
    sdk_cp = ":".join(map(str, sdk))
    work_root = Path("../pgpt-runs/PG379").resolve()
    original_work = work_root / v["run"]
    run_name = v["run"].removesuffix("-v1") + "-v2"
    work = work_root / run_name
    work.mkdir(mode=0o700)
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    steps = []

    def run(name, argv, allowed=(0,)):
        command = list(map(str, argv))
        begin = utc()
        result = subprocess.run(command, env=env, capture_output=True, timeout=90, check=False)
        stdout, stderr = work / (name + ".stdout"), work / (name + ".stderr")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        terminal = dict(step=name, command=command, exitCode=result.returncode, startedAtUTC=begin,
                        terminalAtUTC=utc(), stdout=pin(stdout), stderr=pin(stderr))
        json_file(work / (name + "-terminal.json"), terminal)
        steps.append(terminal)
        if result.returncode not in allowed:
            raise SystemExit(result.returncode)
        return result.stdout

    typed = original_work / "scope/target/classes"
    mode_prefix = BASE + "/monitoring/MonitoringModePolicy"
    mode_paths = [typed / (mode_prefix + suffix + ".class")
                  for suffix in ("", "$DetailService", "$RetentionConfiguration")]
    assert {p.relative_to(typed) for p in typed.rglob("*.class")} == (
        {p.relative_to(typed) for p in mode_paths} | {Path(BASE + "/monitoring/package-info.class")})
    assert (original_work / "pom.xml").read_bytes() == Path("pom.xml").read_bytes()
    for p in (target, package):
        snapshot = original_work / "scope/src/main/java" / p.relative_to(project / "main/java")
        assert snapshot.read_bytes() == p.read_bytes()
    retained = []
    for path in sorted(original_work.glob("*-terminal.json")):
        receipt = json.loads(path.read_bytes())
        for key in ("stdout", "stderr"):
            assert pin(Path(receipt[key]["path"])) == receipt[key]
        if receipt["step"] == "helper-compile":
            assert receipt["exitCode"] == 1
            diagnostic = Path(receipt["stderr"]["path"]).read_text()
            assert "io.micrometer.common.lang.internal.Contract not found" in diagnostic
            assert "warnings found and -Werror specified" in diagnostic
        else:
            assert receipt["exitCode"] == 0
        retained.append(dict(receipt=pin(path), step=receipt["step"], exitCode=receipt["exitCode"]))
    assert not (original_work / "unit-terminal.json").exists()
    log = (original_work / "typed.stdout").read_bytes()
    assert all(flag in log for flag in (b"-Xep:NullAway:ERROR", b"-Werror", b"Compiling 2 source files"))
    assert b"[NullAway]" not in log
    assert not ET.parse(original_work / "checkstyle.stdout").getroot().findall("file/error")
    for path in mode_paths:
        assert (original_work / ("before-public-" + path.stem + ".stdout")).read_bytes() == (
            original_work / ("current-public-" + path.stem + ".stdout")).read_bytes()
    bytecode = (original_work / "current-mode-bytecode.stdout").read_bytes()
    parse_body = bytecode.split(b" parse(java.lang.String)", 1)[1].split(b"  public boolean", 1)[0]
    assert b"lookupswitch" not in parse_body and b"tableswitch" not in parse_body
    assert parse_body.count(b"java/lang/String.equals") == 2
    strict = [javac, "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none",
              "-implicit:none", "-sourcepath", ""]
    helpers, tests = work / "helpers", work / "tests"
    run("helper-compile", [*strict, "-cp", f"{typed}:{jspecify}:{sdk_cp}",
                           "-d", helpers, *support])
    run("test-compile", [*strict, "-cp", f"{typed}:{helpers}:{jspecify}:{sdk_cp}:{junit}",
                         "-d", tests, *fixtures])
    reports, stream = work / "reports", work / "unit.exec"
    session = "PG40986-EXPLICIT-MODE-COMPARISON"
    run("unit", [java, f"-javaagent:{agent}=destfile={stream},sessionid={session},append=false",
                 "-jar", junit, "execute", "--fail-if-no-tests", "--disable-ansi-colors",
                 "--class-path", f"{typed}:{helpers}:{tests}:{jspecify}:{sdk_cp}",
                 "--reports-dir", reports,
                 *(arg for name in SUITES for arg in ("--select-class", PACKAGE + name))])
    jxml = reports / "TEST-junit-jupiter.xml"
    root = ET.parse(jxml).getroot()
    counts = {k: int(root.attrib[k]) for k in ("tests", "errors", "failures", "skipped")}
    assert counts == dict(tests=32, errors=0, failures=0, skipped=0)
    actual = {(row.attrib["classname"], row.attrib["name"].removesuffix("()"))
              for row in root.findall("testcase")}
    expected = {(row["classname"], row["name"]) for row in original["cases"]
                if row["classname"] in {PACKAGE + suite for suite in SUITES[:3]}}
    expected.update((PACKAGE + SUITES[3], name.removesuffix("()")) for name in engine["exactMethods"])
    assert actual == expected

    op = Path("evidence/01_PT/018_NK-OPS-001/evidence")
    out = op / run_name
    out.mkdir()
    command = before["rawCommand"][:4]
    observed_targets = [*mode_paths, helpers / (BASE + "/monitoring/ObservationContext.class")]
    table = run("raw", [*command, stream, *observed_targets])
    rows = {}
    for line in table.decode().splitlines():
        if line.startswith("CLASS\t"):
            row = line.split("\t")
            assert row[3] == "true"
            rows[row[1]] = dict(crc64=row[2], counters={
                kind: dict(missed=int(m), covered=int(c))
                for kind, m, c in (item.split(":") for item in row[6:])})
    assert len(rows) == len(observed_targets)
    (out / "unfiltered.tsv").write_bytes(table)
    known = json.loads(next(op.glob("PG40880*/manifest.json")).read_bytes())
    sb, pmd = out / "spotbugs.xml", out / "pmd.xml"
    aux = f"{typed}:{jspecify}"
    run("spotbugs", [java, "-Xmx1g", "-cp", known["steps"]["spotbugs"]["command"][3],
                     "edu.umd.cs.findbugs.FindBugs2", "-effort:max", "-low", "-xml:withMessages",
                     "-exitcode", "-auxclasspath", aux, "-output", sb, *mode_paths], allowed=(0, 1))
    run("pmd", [java, "-cp", known["steps"]["pmd"]["command"][2], "net.sourceforge.pmd.cli.PmdCli",
                "check", "--dir", target, "--rulesets", "tools/quality/static/pmd.xml",
                "--use-version", "java-25", "--aux-classpath", f"{aux}:{jdk}/lib/jrt-fs.jar",
                "--no-cache", "--format", "xml", "--report-file", pmd], allowed=(0, 4))
    sbx, pmx = ET.parse(sb).getroot(), ET.parse(pmd).getroot()
    sb_count = len(sbx.findall(".//BugInstance"))
    sb_errors = len(sbx.findall(".//Error")) + len(sbx.findall(".//MissingClass"))
    pmd_rules = [dict(rule=item.attrib["rule"], line=int(item.attrib["beginline"]))
                 for item in pmx.findall("p:file/p:violation", {"p": "http://pmd.sourceforge.net/report/2.0.0"})]
    pmd_errors = len(pmx.findall("p:error", {"p": "http://pmd.sourceforge.net/report/2.0.0"}))
    complete = all(counter["missed"] == 0 for row in rows.values() for counter in row["counters"].values())
    passed = complete and not sb_count and not sb_errors and not pmd_errors
    json_file(out / "manifest.json", dict(
        source=source, beforeSource=v["productionCoreMain"], run=run_name, startEvent=start["eventId"],
        actualExit=0 if passed else 1, terminalAtUTC=utc(), os="Linux", java="25.0.4", maven="3.9.12",
        testCounts=counts, exactCases=sorted(actual), newTestDefinitions=0, affectedPriorRequalifications=32,
        sourceInputs=[pin(p) for p in paths], dependencyInputs=[pin(jspecify), *(pin(path) for path in sdk)],
        javapDirectEqualsCalls=2, previousRaw=refs[1], unchangedPublicAbi=True, actualPhysical=[pin(p) for p in observed_targets],
        rawOutput=pin(out / "unfiltered.tsv"), raw=rows, fullRawForMeasuredClasses=complete,
        originalCoverageCombined=False, junitXml=pin(jxml), execData=pin(stream), session=session,
        nullAwayFindings=0, spotbugs=dict(report=pin(sb), findings=sb_count, errors=sb_errors),
        pmd=dict(report=pin(pmd), errors=pmd_errors, findings=pmd_rules, requiresDisposition=bool(pmd_rules)),
        steps=steps, retainedSuccessfulPreparation=retained, priorFixtureFailure="BUG-3439", fullBatchPackageUpdated=False, realOperations=0, wholeF03=False, whole451=False, formalDelta=0,
    ))
    print(counts, complete, sb_count, sb_errors, pmd_rules)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
