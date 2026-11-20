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
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
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
    java, javac, javap = (jdk / "bin" / tool for tool in ("java", "javac", "javap"))
    junit = tc / "junit-platform-console-standalone-1.13.4.jar"
    agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    deps = original["begin"]["dependencyHashes"]
    jspecify, = [Path(p) for p in deps if p.endswith("jspecify-1.0.1.jar")]
    micrometer, = [Path(p) for p in deps if p.endswith("micrometer-core-1.17.1.jar")]
    assert all(pin(p)["sha256"] == deps[str(p)] for p in (jspecify, micrometer))
    work = Path("../pgpt-runs/PG379").resolve() / v["run"]
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

    run("format", [java, "-jar", tc / "google-java-format-1.36.1-all-deps.jar",
                   "--dry-run", "--set-exit-if-changed", target])
    style = run("checkstyle", [java, "-jar", tc / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                               "-c", "tools/quality/static/checkstyle.xml", "-f", "xml", target])
    assert not ET.fromstring(style).findall("file/error")
    (work / "pom.xml").write_bytes(Path("pom.xml").read_bytes())
    scope = work / "scope"
    scope.mkdir()
    (scope / "pom.xml").write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>mode-policy-value-scope</artifactId><dependencies>'
        '<dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency>'
        '</dependencies></project>\n'
    )
    for p in (target, package):
        dest = scope / "src/main/java" / p.relative_to(project / "main/java")
        dest.parent.mkdir(exist_ok=True, parents=True)
        dest.write_bytes(p.read_bytes())
    maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    log = run("typed", [maven, "-o", "-N", "-B", "-ntp", "-X", "-f", scope / "pom.xml",
                         f"-Dmaven.repo.local={tc}/m2/repository", "compile"])
    assert all(word in log for word in (b"-Xep:NullAway:ERROR", b"-Werror", b"Compiling 2 source files"))
    assert b"[NullAway]" not in log
    typed = scope / "target/classes"
    mode_prefix = BASE + "/monitoring/MonitoringModePolicy"
    mode_paths = [typed / (mode_prefix + suffix + ".class")
                  for suffix in ("", "$DetailService", "$RetentionConfiguration")]
    expected_physical = {p.relative_to(typed) for p in mode_paths} | {
        Path(BASE + "/monitoring/package-info.class")}
    assert {p.relative_to(typed) for p in typed.rglob("*.class")} == expected_physical
    for previous, current in zip(before["physical"], mode_paths, strict=True):
        assert pin(Path(previous["path"])) == previous
        assert run("before-public-" + current.stem, [javap, "-public", "-s", previous["path"]]) == run(
            "current-public-" + current.stem, [javap, "-public", "-s", current])
    bytecode = run("current-mode-bytecode", [javap, "-c", "-p", mode_paths[0]])
    parse_body = bytecode.split(b" parse(java.lang.String)", 1)[1].split(b"  public boolean", 1)[0]
    assert b"lookupswitch" not in parse_body and b"tableswitch" not in parse_body
    assert parse_body.count(b"java/lang/String.equals") == 2

    strict = [javac, "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none",
              "-implicit:none", "-sourcepath", ""]
    helpers, tests = work / "helpers", work / "tests"
    run("helper-compile", [*strict, "-cp", f"{typed}:{jspecify}:{micrometer}",
                           "-d", helpers, *support])
    run("test-compile", [*strict, "-cp", f"{typed}:{helpers}:{jspecify}:{micrometer}:{junit}",
                         "-d", tests, *fixtures])
    reports, stream = work / "reports", work / "unit.exec"
    session = "PG40986-EXPLICIT-MODE-COMPARISON"
    run("unit", [java, f"-javaagent:{agent}=destfile={stream},sessionid={session},append=false",
                 "-jar", junit, "execute", "--fail-if-no-tests", "--disable-ansi-colors",
                 "--class-path", f"{typed}:{helpers}:{tests}:{jspecify}:{micrometer}",
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
    out = op / v["run"]
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
        source=source, beforeSource=v["productionCoreMain"], run=v["run"], startEvent=start["eventId"],
        actualExit=0 if passed else 1, terminalAtUTC=utc(), os="Linux", java="25.0.4", maven="3.9.12",
        testCounts=counts, exactCases=sorted(actual), newTestDefinitions=0, affectedPriorRequalifications=32,
        sourceInputs=[pin(p) for p in paths], dependencyInputs=[pin(jspecify), pin(micrometer)],
        javapDirectEqualsCalls=2, previousRaw=refs[1], unchangedPublicAbi=True, actualPhysical=[pin(p) for p in observed_targets],
        rawOutput=pin(out / "unfiltered.tsv"), raw=rows, fullRawForMeasuredClasses=complete,
        originalCoverageCombined=False, junitXml=pin(jxml), execData=pin(stream), session=session,
        nullAwayFindings=0, spotbugs=dict(report=pin(sb), findings=sb_count, errors=sb_errors),
        pmd=dict(report=pin(pmd), errors=pmd_errors, findings=pmd_rules, requiresDisposition=bool(pmd_rules)),
        steps=steps, fullBatchPackageUpdated=False, realOperations=0, wholeF03=False, whole451=False, formalDelta=0,
    ))
    print(counts, complete, sb_count, sb_errors, pmd_rules)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
