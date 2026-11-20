"""Verify the current borrowed Outbox JDBC close ordering using only JDK interface doubles."""
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    with path.open("x") as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    ops = Path("evidence/01_PT/018_NK-OPS-001")
    evidence = ops / "evidence"
    group = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1392_*.json")).read_bytes())
    context = group["values"]
    production = context["productionCoreMain"]
    old_unit = next(evidence.glob("PG40942*v2/manifest.json"))
    previous = json.loads(old_unit.read_bytes())
    typed_path = next(evidence.glob("PG40946*/manifest.json"))
    typed = json.loads(typed_path.read_bytes())
    assert previous["source"] == typed["source"] == production and typed["compilerExit"] == 0
    names = {
        "OutboxObservationRepository.java", "OutboxRowsMetricRecorder.java",
        "OutboxAgeMetricRecorder.java", "package-info.java",
    }
    source_pins = [
        ref for ref in typed["explicitSourcePins"] if Path(ref["path"]).name in names
    ]
    dep_pins = [
        ref for ref in previous["dependencyPins"]
        if Path(ref["path"]).name.startswith(("jspecify-", "junit-platform-", "micrometer-commons-",
                                              "micrometer-core-", "micrometer-observation-"))
    ]
    assert len(source_pins) == 4 and len(dep_pins) == 5
    assert all(pin(Path(ref["path"])) == ref for ref in [*source_pins, *dep_pins])
    specs = next(ops.glob("4686_*.md"))
    test_owner = "dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest"
    method = "outboxDb012CompleteReadWithTwoCloseFailuresKeepsFirstReleaseAsPrimary"
    fixture = Path("src/schubert-nk-api/src/test/java") / (test_owner.replace(".", "/") + ".java")
    slot = Path("../pgpt-runs/PG379").resolve() / context["run"]
    slot.mkdir(mode=0o700)
    classes = slot / "classes"
    compiled_tool = slot / "tool-classes"
    exec_data = slot / "unit.exec"
    reports = slot / "reports"
    steps = []
    env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}

    def run(stage, args):
        command = list(map(str, args))
        started = utc()
        with (slot / f"{stage}.log").open("xb") as log:
            result = subprocess.run(
                command, env=env, stdout=log, stderr=subprocess.PIPE, timeout=30, check=False,
            )
        with (slot / f"{stage}.stderr").open("xb") as err:
            err.write(result.stderr)
        record = dict(stage=stage, command=command, exitCode=result.returncode,
                      startedAtUTC=started, terminalAtUTC=utc())
        steps.append(record)
        write(slot / f"{stage}-terminal.json", record)
        if result.returncode:
            raise SystemExit(result.returncode)
        return (slot / f"{stage}.log").read_bytes()

    tc = Path("../toolchain").resolve()
    java = tc / "jdk-25.0.4/bin/java"
    javac = java.with_name("javac")
    fmt = tc / "google-java-format-1.36.1-all-deps.jar"
    checkstyle = tc / "static-gates-20261015/checkstyle-14.3.0-all.jar"
    run("format", [java, "-jar", fmt, "--dry-run", "--set-exit-if-changed", fixture])
    style = run("checkstyle", [java, "-jar", checkstyle, "-c", "tools/quality/static/checkstyle.xml",
                               "-f", "xml", fixture])
    assert not ET.fromstring(style).findall("file/error")
    dependencies = ":".join(ref["path"] for ref in dep_pins)
    run("compile", [javac, "--release", "25", "-g", "-proc:none", "-Xlint:all", "-Werror",
                    "-implicit:none", "-sourcepath", "", "-cp", dependencies, "-d", classes,
                    *[ref["path"] for ref in source_pins], fixture])
    prefix = "dev/codex/schubert/nk/api/monitoring/persistence/OutboxObservationRepository"
    target = classes / (prefix + ".class")
    expected_sha = {item["classPath"]: item["sha256"] for item in typed["generatedPhysical"]}
    target_refs = [pin(p) for p in sorted(target.parent.glob("OutboxObservationRepository*.class"))]
    assert len(target_refs) == 2
    assert all(ref["sha256"] == expected_sha[str(Path(ref["path"]).relative_to(classes))] for ref in target_refs)

    raw_previous = json.loads(old_unit.with_name("raw-manifest.json").read_bytes())
    probe = next(arg.split("=", 1)[0] for arg in previous["stages"][1]["command"] if arg.startswith("-javaagent:"))
    console = next(ref["path"] for ref in dep_pins if Path(ref["path"]).name.startswith("junit-platform-"))
    session = "PG40954-OUTBOXDB012"
    run("unit", [java, "-Djunit.jupiter.execution.parallel.enabled=false",
                 "-Djunit.jupiter.extensions.autodetection.enabled=false",
                 f"{probe}=destfile={exec_data},sessionid={session},append=false",
                 "-jar", console, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                 "--class-path", f"{classes}:{dependencies}", "--select-method", f"{test_owner}#{method}",
                 "--reports-dir", reports])
    xml = reports / "TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    counts = {name: int(suite.attrib[name]) for name in ("tests", "failures", "errors", "skipped")}
    assert counts == dict(tests=1, failures=0, errors=0, skipped=0)
    case, = suite.findall("testcase")
    assert (case.attrib["classname"], case.attrib["name"]) == (test_owner, method + "()")

    instrument = slot / "UnfilteredCodeMeasurement.java"
    instrument.write_bytes(subprocess.check_output(
        ["git", "show", "c5674055a6:tools/quality/jacoco/UnfilteredCodeMeasurement.java"], timeout=10,
    ))
    prior_measure = json.loads(next(evidence.glob("PG40904*/manifest.json")).read_bytes())
    assert pin(instrument)["sha256"] == prior_measure["unfilteredToolSha256"]
    command = raw_previous["compileCommand"]
    raw_libraries = command[command.index("-cp") + 1]
    run("compile_raw", [*command[:command.index("-d")], "-d", compiled_tool, instrument])
    table = run("raw", [java, "-cp", f"{compiled_tool}:{raw_libraries}", raw_previous["rawCommand"][3],
                        exec_data, target, classes / (prefix + "$Snapshot.class")])
    coverage = []
    for row in (line.split("\t") for line in table.decode().splitlines() if line.startswith("CLASS\t")):
        coverage.append(dict(className=row[1], crc64=row[2], executionDataFound=row[3] == "true",
                             counters=[dict(kind=k, missed=int(m), covered=int(c)) for k, m, c in
                                       (cell.split(":") for cell in row[6:])]))
    assert len(coverage) == 2
    out = evidence / context["run"]
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(table)
    write(out / "manifest.json", dict(
        source=production, startEvent=group["eventId"], run=context["run"], actualExit=0,
        terminalAtUTC=utc(), os="Linux", java="25.0.4", coverageTool="JaCoCo 0.8.15",
        testId="OUTBOXDB012", executionSession=session, steps=steps, testCounts=counts,
        expectedVariants=["SQL primary/Error suppressed", "Error primary/SQL suppressed"],
        actualVariants=["SQL primary/Error suppressed", "Error primary/SQL suppressed"],
        sourcePins=source_pins, dependencyPins=dep_pins, fixture=pin(fixture), specification=pin(specs),
        exactTypedSource=pin(typed_path), measuredPhysical=target_refs,
        junitXml=pin(xml), executionData=pin(exec_data), unfilteredTable=pin(out / "unfiltered.tsv"),
        unfilteredCoverage=coverage, historicalTestsRerun=0, realDatabaseOrExternalOperations=0,
        productChanges=0, whole451=False, formalDelta=0,
    ))
    print(counts, coverage)


if __name__ == "__main__":
    main()
