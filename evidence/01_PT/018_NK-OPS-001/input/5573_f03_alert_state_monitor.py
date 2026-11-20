"""Run the closed alert scope once with the product compiler and one unmerged JaCoCo stream."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


ROOT = Path.cwd()
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
SDK = ROOT.parent / "toolchain"
M2 = SDK / "m2/repository"
JAVA = SDK / "jdk-25.0.4/bin/java"
SPECIFY = M2 / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
MAVEN = SDK / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
NAMESPACE = "dev.codex.schubert.nk.batch.monitoring."
RAW_SOURCE = "e02e75b21d82f903b886ba8951e04da15c643489"
ENV = {"PATH": str(JAVA.parent) + ":" + os.defpath, "JAVA_HOME": str(JAVA.parent.parent),
       "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
POM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
<modelVersion>4.0.0</modelVersion>
<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>
<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>
<artifactId>alert-state-closed-scope</artifactId>
<dependencies><dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency></dependencies>
</project>
"""


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], timeout=30)


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def find(prefix, filename="manifest.json"):
    result, = OPS.glob(f"{prefix}-*/{filename}")
    return result


def main():
    run_id = "PG41070-f03-alert-owner-state-final-v1"
    session = "PG41070"
    start_file, = Path("documents/400_PGPT/470_PMO").glob("601_*/1519_*")
    start = read(start_file)
    plan = start["values"]
    core = git("rev-parse", "HEAD").decode().strip()
    assert all(pin(Path(ref["path"])) == ref for ref in plan["oracleReferences"])
    one_main = "AlertLifecycle.java"
    one_test = "AlertLifecycleTest.java"
    before, timed = read(find("PG40828")), read(OPS / "PG40798-timed-alert-pending-recovery-v2/manifest.json")
    static = read(find("PG40800"))
    mode = read(OPS / "PG40986-f03-mode-policy-explicit-comparison-v2/manifest.json")
    pipe = read(find("PG40938"))
    recent = [row for row in mode["sourceInputs"] if row["path"].endswith("/MonitoringModePolicy.java")]
    assert len(recent) == 1
    inputs = {p["path"]: p for p in [*timed["inputs"], *before["sources"], *recent, pipe["test"]]}
    inputs = {Path(k): v for k, v in inputs.items()}
    for path, entry in inputs.items():
        data = path.read_bytes()
        assert data == git("show", f"{core}:{path}")
        assert sha(data) == entry["sha256"] if path.name not in (one_main, one_test) else sha(data) != entry["sha256"]
    prod = sorted(p for p in inputs if "/src/main/" in str(p))
    fixture = sorted(p for p in inputs if "/src/test/" in str(p))
    suites = {p.stem for p in fixture}
    expected = {(row["suite"], row["method"]) for row in timed["cases"]} | {
        (row["owner"], row["method"].removesuffix("()")) for row in before["cases"]
    }
    expected.add(("MonitoringPolicyEngineTest", "monPipe008MissingObservationResetsOnlyItsConditionAndService"))
    assert len(prod) == 13 and len(suites) == 11 and len(expected) == 84
    modified = git("diff", "--name-only", plan["productionCoreMain"], core, "--", "src").decode().splitlines()
    assert set(map(Path, modified)) == {p for p in inputs if p.name in (one_main, one_test)}
    tools = {Path(path).name: Path(path) for path in (p["path"] for p in before["tools"])}
    assert all(pin(Path(row["path"])) == row for row in before["tools"])
    deps = read(find("PG31432", "compile.json"))["dependencies"]
    assert all(pin(Path(ref["path"])) == ref for ref in deps)
    raw_cp = os.pathsep.join(row["path"] for row in deps)
    format_jar = tools["google-java-format-1.36.1-all-deps.jar"]
    check_jar = tools["checkstyle-14.3.0-all.jar"]
    check_rules = tools["checkstyle.xml"]
    junit = tools["junit-platform-console-standalone-1.13.4.jar"]
    agent = tools["org.jacoco.agent-0.8.15-runtime.jar"]
    jacoco = tools["org.jacoco.cli-0.8.15-nodeps.jar"]
    out = OPS / run_id
    out.mkdir()
    preserve = ROOT.parent / "pgpt-runs/PG379" / run_id
    preserve.mkdir()
    steps, cases = {}, []
    started = utc()

    def run(label, *parts):
        cmd = list(map(str, parts))
        step = subprocess.run(cmd, env=ENV, capture_output=True, timeout=100)
        (preserve / (label + ".stdout")).write_bytes(step.stdout)
        (preserve / (label + ".stderr")).write_bytes(step.stderr)
        steps[label] = dict(command=cmd, actualExit=step.returncode, stdoutSha256=sha(step.stdout),
                            stderrSha256=sha(step.stderr), terminalAtUTC=utc())
        return step

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-alert-state-") as folder:
        tmp = Path(folder)
        scope = tmp / "scope"
        java_input = scope / "src/main/java"
        java_input.mkdir(parents=True)
        original_pom = Path("pom.xml")
        assert pin(original_pom)["sha256"] == static["rootPomSha256"]
        (tmp / "pom.xml").write_bytes(original_pom.read_bytes())
        scoped = scope / "pom.xml"
        scoped.write_text(POM)
        for source in prod:
            copied = java_input / str(source).split("/src/main/java/", 1)[1]
            copied.parent.mkdir(parents=True, exist_ok=True)
            copied.write_bytes(source.read_bytes())
        compiled = scope / "target/classes"
        check = run("maven-compile", MAVEN, "-o", "-B", "-ntp", "-N", "-X", "-f", scoped,
                    f"-Dmaven.repo.local={M2}", "compile")
        log = check.stdout.decode()
        markers = ("-Xep:NullAway:ERROR", "-XepOpt:NullAway:JSpecifyMode=true", "-Werror",
                   "-Xplugin:ErrorProne", "Compiling 13 source files")
        assert check.returncode == 0 and all(marker in log for marker in markers)
        physical = {str(p.relative_to(compiled)): p for p in compiled.rglob("*.class")}
        old_physical = static["exactLocalClassFiles"]
        assert set(physical) == set(old_physical) | {
            NAMESPACE.replace(".", "/") + "AlertLifecycle$State.class"
        }
        delta = [name for name, path in physical.items()
                 if name in old_physical and pin(path)["sha256"] != old_physical[name]]
        assert {Path(name).stem for name in delta} == {"AlertLifecycle", "MonitoringModePolicy"}
        current_mode = next(p for name, p in physical.items() if name.endswith("/MonitoringModePolicy.class"))
        previous_mode = next(p for p in mode["actualPhysical"] if p["path"].endswith("/MonitoringModePolicy.class"))
        assert pin(current_mode)["sha256"] == previous_mode["sha256"]
        change = [p for p in (*prod, *fixture) if p.name in (one_main, one_test)]
        assert run("format", JAVA, "-jar", format_jar, "--skip-reflowing-long-strings",
                   "--dry-run", "--set-exit-if-changed", *change).returncode == 0
        checkstyle = preserve / "checkstyle.xml"
        assert run("checkstyle", JAVA, "-jar", check_jar, "-c", check_rules,
                   "-f", "xml", "-o", checkstyle, *change).returncode == 0
        assert not ET.parse(checkstyle).getroot().findall(".//error")
        test_class = tmp / "tests"
        classpath = os.pathsep.join(map(str, (compiled, junit, SPECIFY)))
        assert run("test-compile", JAVA.with_name("javac"), "--release", 25, "-g", "-Werror",
                   "-Xlint:all", "-proc:none", "-cp", classpath, "-d", test_class, *fixture).returncode == 0
        selectors = [token for name in sorted(suites) for token in ("--select-class", NAMESPACE + name)]
        exec_data = preserve / "coverage.exec"
        reports = preserve / "junit"
        assert run("junit", JAVA, f"-javaagent:{agent}=destfile={exec_data},append=false,sessionid={session}",
                   "-jar", junit, "execute", "--disable-banner", "--disable-ansi-colors",
                   "--class-path", os.pathsep.join(map(str, (compiled, test_class, SPECIFY))),
                   *selectors, "--reports-dir", reports, "--fail-if-no-tests").returncode == 0
        xml = reports / "TEST-junit-jupiter.xml"
        rows = ET.parse(xml).getroot().findall("testcase")
        for row in rows:
            suite = row.attrib["classname"].rsplit(".", 1)[1]
            method = row.attrib["name"].removesuffix("()")
            assert {child.tag for child in row}.isdisjoint({"failure", "error", "skipped"})
            cases.append(dict(suite=suite, method=method, outcome="PASSED"))
        assert len(cases) == len(expected) and {(c["suite"], c["method"]) for c in cases} == expected
        coverage = preserve / "coverage.xml"
        assert run("report", JAVA, "-jar", jacoco, "report", exec_data,
                   "--classfiles", compiled, "--xml", coverage).returncode == 0
        cv = ET.parse(coverage).getroot()
        assert [session.attrib["id"] for session in cv.findall("sessioninfo")] == [session]
        path = tmp / "UnfilteredCodeMeasurement.java"
        path.write_bytes(git("show", f"{RAW_SOURCE}:tools/quality/jacoco/{path.name}"))
        raw_classes = tmp / "raw"
        assert run("raw-compile", JAVA.with_name("javac"), "--release", 25, "-Werror", "-Xlint:all",
                   "-cp", raw_cp, "-d", raw_classes, path).returncode == 0
        measured = run("raw-measurement", JAVA, "-cp", f"{raw_classes}:{raw_cp}",
                       "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                       exec_data, *[p for _, p in sorted(physical.items())])
        assert measured.returncode == 0
        tsv = out / "unfiltered.tsv"
        tsv.write_bytes(measured.stdout)
        source_prefix = NAMESPACE.replace(".", "/") + "AlertLifecycle"
        raw = []
        for line in measured.stdout.decode().splitlines():
            row = line.split("\t")
            if row[0] == "CLASS":
                counts = {k: dict(missed=int(m), covered=int(c))
                          for k, m, c in (part.split(":") for part in row[6:])}
                raw.append(dict(className=row[1], crc64=row[2], matched=row[3]=="true", counters=counts))
        primary = [row for row in raw if row["className"].startswith(source_prefix)]
        assert len(raw) == len(physical) and len(primary) == 7 and all(c["matched"] for c in primary)
        aggregate = {key: dict(covered=sum(c["counters"][key]["covered"] for c in primary),
                               missed=sum(c["counters"][key]["missed"] for c in primary))
                     for key in primary[0]["counters"]}
        assert all(value["missed"] == 0 for value in aggregate.values()), aggregate
        # Inspect the owned monitor identity with an independent javap representation.
        prefix = NAMESPACE + "AlertLifecycle"
        baseline = tmp / "baseline"
        old_source = tmp / one_main
        old_source.write_bytes(git("show", f"{plan['productionCoreMain']}:{next(p for p in prod if p.name==one_main)}"))
        observation = next(p for p in prod if p.stem == "ObservationContext")
        assert run("old-abi-compile", JAVA.with_name("javac"), "--release", 25, "-Werror",
                   "-Xlint:all", "-cp", SPECIFY, "-d", baseline, old_source, observation).returncode == 0
        javap = JAVA.with_name("javap")
        for suffix in ("", "$Event", "$Condition", "$Service", "$Severity", "$CauseClearance"):
            a = run("old-abi" + suffix, javap, "-public", "-s", "-classpath", baseline, prefix + suffix)
            b = run("new-abi" + suffix, javap, "-public", "-s", "-classpath", compiled, prefix + suffix)
            assert a.returncode == b.returncode == 0 and a.stdout == b.stdout
        details = run("monitor", javap, "-p", "-v", "-classpath", compiled, prefix + "$State")
        outer = run("consumer", javap, "-p", "-c", "-classpath", compiled, prefix)
        assert details.returncode == outer.returncode == 0
        state_text, consumer = details.stdout.decode(), outer.stdout.decode()
        assert state_text.count("ACC_SYNCHRONIZED") == 4 and "monitorenter" not in consumer
        assert consumer.count("Field state:") == 5
        for action in ("snapshot", "interrupt", "violation", "normal"):
            assert f"State.{action}:" in consumer
        assert "Field lastElapsed:" not in consumer
        for label in ("monitor", "consumer"):
            (out / (label + ".txt")).write_bytes((preserve / (label + ".stdout")).read_bytes())
        aux = tmp / "spotbugs-aux.txt"
        aux.write_text(str(SPECIFY) + "\n")
        sb = out / "spotbugs.xml"
        tool_cp = static["steps"]["spotbugs"]["command"][3]
        pmd_cp = static["steps"]["pmd"]["command"][2]
        assert all(Path(p).is_file() and Path(p).is_relative_to(SDK)
                   for p in (tool_cp + ":" + pmd_cp).split(":"))
        assert run("spotbugs", JAVA, "-Xmx1g", "-cp", tool_cp, "edu.umd.cs.findbugs.FindBugs2",
                   "-effort:max", "-low", "-xml:withMessages", "-exitcode", "-auxclasspathFromFile",
                   aux, "-output", sb, compiled).returncode == 0
        bugs = ET.parse(sb).getroot()
        assert not any(bugs.findall(tag) for tag in ("BugInstance", ".//MissingClass", ".//Error"))
        pmd = out / "pmd.xml"
        pmd_step = run("pmd", JAVA, "-cp", pmd_cp, "net.sourceforge.pmd.cli.PmdCli", "check",
                       "-d", java_input, "--rulesets", "tools/quality/static/pmd.xml",
                       "--use-version", "java-25", "--aux-classpath",
                       f"{compiled}:{SPECIFY}:{JAVA.parent.parent/'lib/jrt-fs.jar'}",
                       "--no-cache", "--format", "xml", "--report-file", pmd)
        policy = ET.parse(pmd).getroot()
        ns = {"r": policy.tag.partition("}")[0].removeprefix("{")}
        messages = [dict(name=Path(file.attrib["name"]).name, rule=v.attrib["rule"],
                         line=int(v.attrib["beginline"]), message=(v.text or "").strip())
                    for file in policy.findall("r:file", ns) for v in file.findall("r:violation", ns)]
        key = lambda row: (row.get("source", row.get("name")), row["rule"], row["message"])
        assert pmd_step.returncode in (0, 4) and not policy.findall("r:error", ns)
        counters = Counter(map(key, messages))
        old_counters = Counter(map(key, static["pmdFindings"]))
        info = dict(actualExit=0, startedAtUTC=started, terminalAtUTC=utc(), source=core,
                    previousSource=plan["productionCoreMain"], session=session, run=run_id,
                    rejectedStaticRound=pin(find("PG41068", "receipt.json")), tools=[pin(p) for p in tools.values()],
                    inputs=[pin(p) for p in (*prod, *fixture)], cases=cases, suites=len(suites),
                    passed=len(cases), failed=0, errors=0, skipped=0, notRun=0,
                    originalJunitXml=pin(xml), originalCoverageXml=pin(coverage), execData=pin(exec_data),
                    rawToolSource=RAW_SOURCE, rawTsv=pin(tsv), rawAlertLifecycle=aggregate, rawAll=raw,
                    packagePhysical=len(physical), affectedPublicAbiSame=6,
                    physicalDelta=delta, physicalAdded="AlertLifecycle$State.class",
                    snapshotAndUpdatesSamePrivateMonitor=True, compilerControls=list(markers),
                    spotbugs=dict(report=pin(sb), exit=0, findings=0, missing=0, errors=0),
                    sameByteRecentInputs=[pin(OPS / "PG40986-f03-mode-policy-explicit-comparison-v2/manifest.json"),
                                          pin(find("PG40938"))],
                    pmd=dict(report=pin(pmd), exit=pmd_step.returncode, raw=len(messages),
                             added=[[*code, n] for code, n in (counters-old_counters).items()],
                             removed=[[*code, n] for code, n in (old_counters-counters).items()]),
                    launchCount=1, combinedOldExecCount=0, productNativeActions=0,
                    coverageExclusions=0, steps=steps, wholeF03=False, whole451=False, formalDelta=0)
        path = out / "manifest.json"
        with path.open("x") as file:
            json.dump(info, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(pin(path), len(cases), aggregate, info["pmd"]["raw"], info["pmd"]["added"])


if __name__ == "__main__":
    main()
