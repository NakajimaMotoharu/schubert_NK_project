"""Measure the current complete monitoring policy fixture in one ordinary local execution."""
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    with path.open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    docs = Path("documents/400_PGPT/470_PMO")
    g = json.loads(next(docs.glob("601_*/1410_*.json")).read_bytes())
    ctx = g["values"]
    core = ctx["productionCoreMain"]
    refs = ctx["oracleReferences"]
    assert all(pin(Path(item["path"])) == item for item in refs)
    prior = json.loads(Path(refs[1]["path"]).read_bytes())
    fixture = Path(prior["test"]["path"])
    source_inputs = [*prior["inputs"], prior["test"]]
    names = [item["path"] for item in prior["inputs"]]
    assert len(names) == 7 and all(pin(Path(item["path"])) == item for item in source_inputs + prior["tools"])
    assert not subprocess.check_output(["git", "diff", "--name-only", prior["core"], core, "--", *names])
    assert subprocess.check_output(["git", "show", f"{ctx['source']}:{fixture}"]) == fixture.read_bytes()
    expected = set(re.findall(r'@Test\s+void (\w+)\(', fixture.read_text()))
    assert len(expected) == 10
    evidence = Path(refs[1]["path"]).parent.parent
    work = Path("../pgpt-runs/PG379").resolve() / ctx["run"]
    work.mkdir(mode=0o700)
    tc = Path("../toolchain").resolve()
    java = tc / "jdk-25.0.4/bin/java"
    steps = []
    classes = work / "classes"
    reports = work / "reports"
    exec_file = work / "unit.exec"

    def run(name, values):
        command = list(map(str, values))
        ts = utc()
        result = subprocess.run(command, env={"PATH": f"{java.parent}:/usr/bin:/bin",
                                              "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"},
                                capture_output=True, timeout=60, check=False)
        err = work / f"{name}.stderr"
        out = work / f"{name}.stdout"
        err.write_bytes(result.stderr)
        out.write_bytes(result.stdout)
        terminal = dict(command=command, exitCode=result.returncode, step=name,
                        startedAtUTC=ts, terminalAtUTC=utc(), stderr=pin(err), stdout=pin(out))
        steps.append(terminal)
        write(work / f"{name}-terminal.json", terminal)
        if result.returncode:
            raise SystemExit(result.returncode)
        return result.stdout

    compile_args = next(x["command"].copy() for x in prior["stages"] if x["step"] == "compile")
    compile_args[compile_args.index("-d") + 1] = str(classes)
    run("compile", compile_args)
    prior_test = next(x["command"] for x in prior["stages"] if x["step"] == "test")
    junit = prior_test[prior_test.index("-jar") + 1]
    agent = prior_test[1].split("=", maxsplit=1)[0]
    cp = prior_test[prior_test.index("--class-path") + 1].split(":", maxsplit=1)[1]
    selected = prior_test[prior_test.index("--select-method") + 1].split("#", maxsplit=1)[0]
    session = "PG40966-CURRENT-MONITOR-POLICY-WHOLE-10"
    run("unit", [java, "-Djunit.jupiter.execution.parallel.enabled=false",
                 "-Djunit.jupiter.extensions.autodetection.enabled=false",
                 f"{agent}=destfile={exec_file},sessionid={session},append=false", "-jar", junit,
                 "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                 "--class-path", f"{classes}:{cp}", "--select-class", selected,
                 "--reports-dir", reports])
    junit_xml = reports / "TEST-junit-jupiter.xml"
    x = ET.parse(junit_xml).getroot()
    counts = {k: int(x.attrib[k]) for k in ("tests", "failures", "errors", "skipped")}
    actual_names = {item.attrib["name"].removesuffix("()") for item in x.findall("testcase")}
    assert counts == dict(tests=10, failures=0, errors=0, skipped=0) and actual_names == expected

    raw_previous = json.loads(next(evidence.glob("PG40942*v2/raw-manifest.json")).read_bytes())
    measure = work / "UnfilteredCodeMeasurement.java"
    measure.write_bytes(subprocess.check_output(["git", "show",
        "c5674055a6:tools/quality/jacoco/UnfilteredCodeMeasurement.java"], timeout=15))
    origin = json.loads(next(evidence.glob("PG40904*/manifest.json")).read_bytes())
    assert pin(measure)["sha256"] == origin["unfilteredToolSha256"]
    raw_cc = raw_previous["compileCommand"]
    raw_libs = raw_cc[raw_cc.index("-cp") + 1]
    analyzer = work / "analyzer"
    run("compile-raw", [*raw_cc[:raw_cc.index("-d")], "-d", analyzer, measure])
    package = classes / "dev/codex/schubert/nk/batch/monitoring"
    support = sorted(p for p in package.glob("*.class")
                     if p.name not in {"MonitoringPolicyEngine.class", "ObservationContext.class"}
                     and not p.name.startswith("MonitoringPolicyEngineTest"))
    target = [package / "MonitoringPolicyEngine.class", package / "ObservationContext.class"]
    report = run("raw", [java, "-cp", f"{analyzer}:{raw_libs}", raw_previous["rawCommand"][3],
                         exec_file, *target])
    measurements = {}
    for row in (line.split("\t") for line in report.decode().splitlines() if line.startswith("CLASS\t")):
        measurements[row[1]] = dict(crc64=row[2], executionDataFound=row[3] == "true",
            counters=[dict(kind=k, missed=int(m), covered=int(c)) for k,m,c in
                      (part.split(":") for part in row[6:])])
    assert len(measurements) == 2 and all(value["executionDataFound"] for value in measurements.values())
    out = evidence / ctx["run"]
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(report)
    write(out / "manifest.json", dict(
        actualExit=0, source=core, testSource=ctx["source"], run=ctx["run"], startEvent=g["eventId"],
        terminalAtUTC=utc(), java="25.0.4", os="Linux", steps=steps, counts=counts,
        originalCasesRequired=10, newDefinitions=0, originalWholeCurrentRunProofWasMissing=True,
        exactMethods=sorted(actual_names), priorSeparation=refs[1], inputSourcePins=source_inputs,
        targets=[pin(p) for p in target], supportMeasuredHere=False,
        supportSeparatePhysical=[pin(p) for p in support], executionSession=session,
        execData=pin(exec_file), junitXml=pin(junit_xml), supplementaryRawTable=pin(out / "unfiltered.tsv"),
        measurements=measurements, realOperations=0, historicalExecMerged=False,
        whole451=False, formalDelta=0,
    ))
    print(counts, measurements)


if __name__ == "__main__":
    main()
