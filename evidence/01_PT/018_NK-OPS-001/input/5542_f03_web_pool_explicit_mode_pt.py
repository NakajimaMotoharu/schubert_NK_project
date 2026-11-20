"""Prove the Web pool mode change using the entire existing in-memory registry suite."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}


def write(path, value):
    with path.open("x") as output:
        output.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    start = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1452_*.json"))
    g = json.loads(start.read_bytes())
    scope = g["values"]
    refs = scope["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in refs)
    before, prior = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:]]
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    base = "dev/codex/schubert/nk/web/monitoring"
    main_name, test_name = "WebDbPoolMetricRecorder", "WebDbPoolMetricRecorderTest"
    src = Path("src/schubert-nk-web/src")
    main = src / "main/java" / base / (main_name + ".java")
    package = main.with_name("package-info.java")
    test = src / "test/java" / base / (test_name + ".java")
    assert subprocess.check_output(["git", "diff", "--name-only", scope["source"], source, "--", "src"],
                                   text=True).splitlines() == [str(main)]
    for path in (main, package, test):
        assert path.read_bytes() == subprocess.check_output(["git", "show", f"{source}:{path}"])

    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    java, javac, javap = (jdk / "bin" / note for note in ("java", "javac", "javap"))
    deps = prior["begin"]["dependencyHashes"]
    dependencies = [Path(path) for path in sorted(deps) if path.endswith((
        "micrometer-core-1.17.1.jar", "micrometer-commons-1.17.1.jar",
        "micrometer-observation-1.17.1.jar", "jspecify-1.0.1.jar"))]
    assert len(dependencies) == 4 and all(pin(path)["sha256"] == deps[str(path)] for path in dependencies)
    sdk = ":".join(map(str, dependencies))
    junit = tc / "junit-platform-console-standalone-1.13.4.jar"
    agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    work = Path("../pgpt-runs/PG379").resolve() / scope["run"]
    work.mkdir(mode=0o700)
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    steps = []

    def run(name, argv, allowed=(0,)):
        command = list(map(str, argv))
        started = utc()
        result = subprocess.run(command, env=env, capture_output=True, timeout=90, check=False)
        out, err = work / (name + ".stdout"), work / (name + ".stderr")
        out.write_bytes(result.stdout)
        err.write_bytes(result.stderr)
        receipt = dict(step=name, command=command, exitCode=result.returncode, startedAtUTC=started,
                       terminalAtUTC=utc(), stdout=pin(out), stderr=pin(err))
        write(work / (name + "-terminal.json"), receipt)
        steps.append(receipt)
        if result.returncode not in allowed:
            raise SystemExit(result.returncode)
        return result.stdout

    run("format", [java, "-jar", tc / "google-java-format-1.36.1-all-deps.jar",
                   "--dry-run", "--set-exit-if-changed", main])
    style = run("checkstyle", [java, "-jar", tc / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                               "-c", "tools/quality/static/checkstyle.xml", "-f", "xml", main])
    assert not ET.fromstring(style).findall("file/error")
    (work / "pom.xml").write_bytes(Path("pom.xml").read_bytes())
    sub = work / "scope"
    staged = sub / "src/main/java" / base
    staged.mkdir(parents=True)
    for p in (main, package):
        (staged / p.name).write_bytes(p.read_bytes())
    (sub / "pom.xml").write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>web-pool-mode-limited</artifactId><dependencies>'
        '<dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency>'
        '<dependency><groupId>io.micrometer</groupId><artifactId>micrometer-core</artifactId>'
        '<version>1.17.1</version></dependency></dependencies></project>\n'
    )
    maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    log = run("typed", [maven, "-o", "-N", "-B", "-ntp", "-X", "-f", sub / "pom.xml",
                         f"-Dmaven.repo.local={tc}/m2/repository", "compile"])
    assert all(flag in log for flag in (b"-Xep:NullAway:ERROR", b"-Werror", b"Compiling 2 source files"))
    assert b"[NullAway]" not in log
    for p in dependencies:
        assert str(p).encode() in log

    typed = sub / "target/classes"
    analyze = [typed / base / (main_name + suffix + ".class") for suffix in ("", "$Counts", "$State")]
    assert set(typed.rglob("*.class")) == {*analyze, typed / base / "package-info.class"}
    for old, new in zip(before["physical"], analyze, strict=True):
        suffix = new.stem
        assert pin(Path(old["path"])) == old
        assert run("before-" + suffix, [javap, "-public", "-s", old["path"]]) == run(
            "after-" + suffix, [javap, "-public", "-s", new])
    assert [pin(p)["sha256"] for p in analyze[1:]] == [row["sha256"] for row in before["physical"][1:]]
    tests = work / "tests"
    run("compile-test", [javac, "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none",
                         "-implicit:none", "-sourcepath", "", "-cp", f"{typed}:{sdk}:{junit}",
                         "-d", tests, test])
    reports, exec_data = work / "reports", work / "unit.exec"
    owner = base.replace("/", ".") + "." + test_name
    session = "PG40994-WEB-POOL-MODE-EIGHT"
    run("unit", [java, f"-javaagent:{agent}=destfile={exec_data},sessionid={session},append=false",
                 "-jar", junit, "execute", "--fail-if-no-tests", "--disable-ansi-colors",
                 "--class-path", f"{typed}:{tests}:{sdk}", "--reports-dir", reports, "--select-class", owner])
    xml = reports / "TEST-junit-jupiter.xml"
    root = ET.parse(xml).getroot()
    counts = {k: int(root.attrib[k]) for k in ("tests", "failures", "errors", "skipped")}
    actual = {e.attrib["name"].removesuffix("()") for e in root.findall("testcase")}
    expected = {row["name"] for row in prior["cases"] if row["classname"] == owner}
    assert counts == dict(tests=8, failures=0, errors=0, skipped=0) and actual == expected
    workspace = Path("evidence/01_PT/018_NK-OPS-001/evidence")
    out = workspace / scope["run"]
    out.mkdir()
    table = run("raw", [*before["rawCommand"][:4], exec_data, *analyze])
    (out / "unfiltered.tsv").write_bytes(table)
    counters = {}
    for line in table.decode().splitlines():
        if line.startswith("CLASS\t"):
            cells = line.split("\t")
            assert cells[3] == "true"
            counters[cells[1]] = dict(crc64=cells[2], counts={
                kind: dict(missed=int(missed), covered=int(covered))
                for kind, missed, covered in (item.split(":") for item in cells[6:])})
    assert len(counters) == 3
    tool = json.loads(next(workspace.glob("PG40880*/manifest.json")).read_bytes())
    spotbugs, pmd = out / "spotbugs.xml", out / "pmd.xml"
    run("spotbugs", [java, "-Xmx1g", "-cp", tool["steps"]["spotbugs"]["command"][3],
                     "edu.umd.cs.findbugs.FindBugs2", "-effort:max", "-low", "-xml:withMessages",
                     "-exitcode", "-auxclasspath", f"{typed}:{sdk}", "-output", spotbugs, *analyze],
        allowed=(0, 1))
    run("pmd", [java, "-cp", tool["steps"]["pmd"]["command"][2], "net.sourceforge.pmd.cli.PmdCli",
                "check", "--dir", main, "--rulesets", "tools/quality/static/pmd.xml", "--use-version",
                "java-25", "--aux-classpath", f"{typed}:{sdk}:{jdk}/lib/jrt-fs.jar", "--no-cache",
                "--format", "xml", "--report-file", pmd], allowed=(0, 4))
    sx, px = ET.parse(spotbugs).getroot(), ET.parse(pmd).getroot()
    sb_findings = len(sx.findall(".//BugInstance"))
    sb_errors = len(sx.findall(".//Error")) + len(sx.findall(".//MissingClass"))
    ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
    violations = [dict(rule=e.attrib["rule"], line=int(e.attrib["beginline"]))
                  for e in px.findall("p:file/p:violation", ns)]
    pmd_errors = len(px.findall("p:error", ns))
    scope_ok = len(sx.findall(".//ClassStats")) == len(analyze)
    outer = counters[base + "/" + main_name]["counts"]
    complete = scope_ok and not any((sb_findings, sb_errors, pmd_errors)) and all(
        row["missed"] == 0 for row in outer.values())
    write(out / "manifest.json", dict(
        source=source, beforeSource=scope["productionCoreMain"], startEvent=g["eventId"], run=scope["run"],
        terminalAtUTC=utc(), actualExit=0 if complete else 1, os="Linux", java="25.0.4", maven="3.9.12",
        testCounts=counts, methods=sorted(actual), affectedPriorRegressions=8, newTestDefinitions=0,
        sourceInputs=[pin(x) for x in (main, package, test)], currentAbiUnchanged=True,
        dependencies=[pin(x) for x in dependencies], nullAwayFindings=0, physical=[pin(x) for x in analyze],
        raw=counters, outerRawComplete=complete, xml=pin(xml), unitExec=pin(exec_data), session=session,
        priorRaw=refs[1], rawOutput=pin(out / "unfiltered.tsv"),
        spotbugs=dict(report=pin(spotbugs), findings=sb_findings, errors=sb_errors),
        pmd=dict(report=pin(pmd), findings=violations, errors=pmd_errors),
        steps=steps, liveEnvironmentOperations=0, combinedHistoricalEvidence=False,
        wholeF03=False, whole451=False, formalDelta=0,
    ))
    print(counts, complete, sb_findings, sb_errors, violations)
    raise SystemExit(0 if complete else 1)


if __name__ == "__main__":
    main()
