"""Qualify the one changed API exchange owner in its proven local Java closure."""
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(content):
    return hashlib.sha256(content).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, record):
    with path.open("x") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


def main():
    group_file = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1398_*.json"))
    group = json.loads(group_file.read_bytes())
    context = group["values"]
    baseline = context["productionCoreMain"]
    source = git("rev-parse", "HEAD").decode().strip()
    ops = Path("evidence/01_PT/018_NK-OPS-001")
    evidence = ops / "evidence"
    prior_path = next(evidence.glob("PG40942*v2/manifest.json"))
    prior = json.loads(prior_path.read_bytes())
    prior_raw = json.loads(prior_path.with_name("raw-manifest.json").read_bytes())
    typed = json.loads(next(evidence.glob("PG40946*/manifest.json")).read_bytes())
    assert baseline == prior["source"] == prior_raw["source"] == typed["source"]
    assert prior["actualExit"] == typed["compilerExit"] == 0
    target_simple = "ApiMetricHttpHandler"
    prior_inputs = prior["inputPins"]
    sources = [Path(ref["path"]) for ref in prior_inputs if "/src/main/java/" in ref["path"]]
    fixtures = [Path(ref["path"]) for ref in prior_inputs if "/src/test/java/" in ref["path"]]
    changed_main, = [p for p in sources if p.name == target_simple + ".java"]
    owner_fixture, = [p for p in fixtures if p.name == target_simple + "Test.java"]
    run_name = context["run"].removesuffix("-v1") + "-v2"
    group_start = context["source"]
    source_differences = git("diff", "--name-only", group_start, source, "--", "src", "pom.xml")
    assert set(source_differences.decode().splitlines()) == {str(changed_main), str(owner_fixture)}
    old_main_diff = git("diff", "--name-only", baseline, source, "--", ":(glob)src/**/src/main/**", "pom.xml")
    assert old_main_diff.decode().splitlines() == [str(changed_main)]
    assert len(sources) == 23 and len(fixtures) == 2
    held = [b"TemporaryInfrastructureException", b"ResponseSnapshotCodec",
            b"FingerprintKeyRing", b"WebStartupException"]
    for p in sources + fixtures:
        payload = p.read_bytes()
        assert git("show", f"{source}:{p}") == payload
        assert not any(name in payload for name in held)
    pom = Path("pom.xml")
    assert pin(pom)["sha256"] == typed["parentPomSha256"]
    libraries = prior["dependencyPins"]
    assert len(libraries) == 16 and all(pin(Path(ref["path"])) == ref for ref in libraries)
    dep = [ref["path"] for ref in libraries if "junit-platform-console-" not in ref["path"]]
    junit, = [ref["path"] for ref in libraries if "junit-platform-console-" in ref["path"]]

    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    java = jdk / "bin/java"
    javac = jdk / "bin/javac"
    mvn = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    work = Path("../pgpt-runs/PG379").resolve() / run_name
    work.mkdir(mode=0o700)
    step_list = []
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}

    def run(name, args, timeout=45):
        command = list(map(str, args))
        started = utc()
        result = subprocess.run(command, env=env, capture_output=True, timeout=timeout, check=False)
        stdout = work / f"{name}.stdout"
        stderr = work / f"{name}.stderr"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        term = dict(stage=name, source=source, startedAtUTC=started, terminalAtUTC=utc(),
                    command=command, exitCode=result.returncode, stdout=pin(stdout), stderr=pin(stderr))
        step_list.append(term)
        write(work / f"{name}-terminal.json", term)
        if result.returncode:
            raise SystemExit(result.returncode)
        return result.stdout

    fmt = tc / "google-java-format-1.36.1-all-deps.jar"
    check = tc / "static-gates-20261015/checkstyle-14.3.0-all.jar"
    run("format", [java, "-jar", fmt, "--dry-run", "--set-exit-if-changed", changed_main, owner_fixture])
    cs = run("checkstyle", [java, "-jar", check, "-c", "tools/quality/static/checkstyle.xml",
                            "-f", "xml", changed_main, owner_fixture])
    assert not ET.fromstring(cs).findall("file/error")

    (work / "pom.xml").write_bytes(pom.read_bytes())
    harness_path = work / "compile/pom.xml"
    harness_path.parent.mkdir()
    dependencies = "".join(
        '<dependency><groupId>fixed.sdk</groupId><version>1</version><scope>system</scope>'
        f'<artifactId>sdk-{i}</artifactId><systemPath>{escape(path)}</systemPath></dependency>'
        for i, path in enumerate(dep)
    )
    harness_path.write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>local-api-monitoring-exchange-owner</artifactId>'
        f'<dependencies>{dependencies}</dependencies></project>\n'
    )
    for p in sources:
        copied = harness_path.parent / "src/main/java" / str(p).split("/src/main/java/", 1)[1]
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(p.read_bytes())
    log = run("maven-compile", [mvn, "-o", "-B", "-ntp", "-N", "-X", "-f", harness_path,
                                f"-Dmaven.repo.local={tc}/m2/repository", "compile"], timeout=85)
    controls = [b"-Xep:NullAway:ERROR", b"-XepOpt:NullAway:JSpecifyMode=true", b"-Werror",
                b"Compiling 23 source files"]
    assert all(mark in log for mark in controls) and b"[NullAway]" not in log
    classes = harness_path.parent / "target/classes"
    physical = {str(p.relative_to(classes)): pin(p)["sha256"] for p in classes.rglob("*.class")}
    previous_physical = {row["classPath"]: row["sha256"] for row in typed["generatedPhysical"]}
    exact_target, = [name for name in physical if name.endswith("/" + target_simple + ".class")]
    assert len(physical) == 30 and physical.keys() == previous_physical.keys()
    assert sum(physical[name] != previous_physical[name] for name in physical) == 1
    target = classes / exact_target
    old_class = Path(prior_raw["target"]["path"])
    assert pin(old_class) == prior_raw["target"]
    javap = jdk / "bin/javap"
    old_abi = run("abi-before", [javap, "-public", "-s", old_class])
    new_abi = run("abi-after", [javap, "-public", "-s", target])
    assert old_abi == new_abi

    test_classes = work / "test-classes"
    classpath = ":".join([str(classes), *dep, junit])
    run("compile-test", [javac, "--release", "25", "-g", "-proc:none", "-Xlint:all", "-Werror",
                         "-implicit:none", "-sourcepath", "", "-cp", classpath, "-d",
                         test_classes, *fixtures])
    (test_classes / "prometheus.properties").touch()
    config = work / "empty-prometheus.properties"
    config.touch()
    reports = work / "reports"
    exec_data = work / "unit.exec"
    init = work / "class-init.log"
    agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    session = "PG40958-API-METRIC-EXCHANGE-25"
    selected = "dev.codex.schubert.nk.api.monitoring.ApiMetricHttpHandlerTest"
    run("unit", [java, f"-Djava.io.tmpdir={work}", f"-Dprometheus.config={config}",
                 "-Djunit.jupiter.execution.parallel.enabled=false",
                 "-Djunit.jupiter.extensions.autodetection.enabled=false",
                 f"-Xlog:class+init=info:file={init}",
                 f"-javaagent:{agent}=destfile={exec_data},sessionid={session},append=false,"
                 "includes=dev.codex.schubert.nk.api.monitoring.*",
                 "-jar", junit, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                 "--class-path", f"{test_classes}:{classpath}", "--select-class", selected,
                 "--reports-dir", reports], timeout=70)
    assert not any(name in init.read_bytes() for name in held)
    xml = reports / "TEST-junit-jupiter.xml"
    report = ET.parse(xml).getroot()
    counts = {key: int(report.attrib[key]) for key in ("tests", "errors", "failures", "skipped")}
    assert counts == dict(tests=25, errors=0, failures=0, skipped=0)
    actual_tests = {(n.attrib["classname"], n.attrib["name"].removesuffix("()")) for n in report.findall("testcase")}
    expected_tests = {(n["className"], n["method"]) for n in prior["actualCases"]}
    expected_tests.update((selected, name) for name in (
        "apimhttp024OwnedCloseFailureKeepsThePrimaryWriteOutcome",
        "apimhttp025SameFailureOnReadinessAndCloseKeepsJdkSelfSuppression",
    ))
    assert len(expected_tests) == 25 and actual_tests == expected_tests

    measurement = work / "UnfilteredCodeMeasurement.java"
    measurement.write_bytes(git("show", "c5674055a6:tools/quality/jacoco/UnfilteredCodeMeasurement.java"))
    reference = json.loads(next(evidence.glob("PG40904*/manifest.json")).read_bytes())
    assert reference["unfilteredToolSha256"] == pin(measurement)["sha256"]
    raw_cc = prior_raw["compileCommand"]
    raw_cp = raw_cc[raw_cc.index("-cp") + 1]
    raw_tool = work / "raw-tool"
    run("compile-raw", [*raw_cc[:raw_cc.index("-d")], "-d", raw_tool, measurement])
    table = run("raw", [java, "-cp", f"{raw_tool}:{raw_cp}", prior_raw["rawCommand"][3], exec_data, target])
    row, = (line.split("\t") for line in table.decode().splitlines() if line.startswith("CLASS\t"))
    assert row[1] == exact_target.removesuffix(".class") and row[3] == "true"
    counters = [dict(kind=k, missed=int(m), covered=int(c))
                for k, m, c in (cell.split(":") for cell in row[6:])]
    default_cli = tc / "org.jacoco.cli-0.8.15-nodeps.jar"
    details = work / "coverage.xml"
    run("default-coverage", [java, "-jar", default_cli, "report", exec_data,
                             "--classfiles", target, "--xml", details])
    coverage_xml = ET.parse(details).getroot()
    assert [s.attrib["id"] for s in coverage_xml.findall("sessioninfo")] == [session]
    node, = coverage_xml.findall("./package/class")
    default_counts = [item.attrib for item in node.findall("counter")]
    wanted = {"LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION"}
    at_zero = {value["kind"] for value in counters if value["missed"] == 0 and value["covered"] > 0}
    complete = wanted <= at_zero
    output = evidence / run_name
    output.mkdir()
    (output / "unfiltered.tsv").write_bytes(table)
    (output / "coverage.xml").write_bytes(details.read_bytes())
    write(output / "manifest.json", dict(
        source=source, beforeSource=baseline, startEvent=group["eventId"], run=run_name,
        terminalAtUTC=utc(), actualExit=0 if complete else 1, testCounts=counts,
        repeatRequiredByChange=24, newPassingTest="APIMHTTP025", cases=sorted(actual_tests),
        inputs=[pin(p) for p in sources + fixtures], sdk=libraries, rootPom=pin(pom),
        testSpec=pin(next(ops.glob("5517_*.md"))), junit=pin(xml), execData=pin(exec_data),
        steps=step_list, nullAwayFindings=0, compileControls=[item.decode() for item in controls],
        physicalFiles=len(physical), differentPhysical=[exact_target], publicAbiUnchanged=True,
        publicAbiSha256=sha(new_abi), currentPhysical=pin(target), crc64=row[2], session=session,
        defaultCounters=default_counts, unfilteredCounters=counters,
        unfilteredReport=pin(output / "unfiltered.tsv"), coverageXml=pin(output / "coverage.xml"),
        scopedCoverageComplete=complete, heapHoldTypesInitialized=0,
        externalOperations=0, wholeF03=False, whole451=False, formalDelta=0,
        previousPreparation=dict(exit=1, launchedMaven=False, testsStarted=0, bug="BUG-3431"),
    ))
    print(counts, counters)
    raise SystemExit(0 if complete else 1)


if __name__ == "__main__":
    main()
