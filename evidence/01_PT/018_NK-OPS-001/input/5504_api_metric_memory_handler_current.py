"""Run the original 23 API metric handler cases against the admitted current Java closure."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def now():
    return datetime.now(timezone.utc).isoformat()


start = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1374_*")).read_bytes())
ctx = start["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(row["path"])) == row for row in refs)
original, oracle, context = [json.loads(Path(row["path"]).read_bytes()) for row in refs[1:]]
assert original["actualExit"] == oracle["actualExit"] == context["actualExit"] == 0
assert context["source"] == ctx["productionCoreMain"]
expected = {(row["classname"], row["name"].removesuffix("()")) for row in original["cases"]}
assert len(expected) == 23 and all(row["result"] == "PASS" for row in original["cases"])
main = [Path(row["path"]) for row in context["javaSourceInputs"]
        if "/schubert-nk-api/src/main/" in row["path"]]
base = main[0].parent
main.extend(base / (name + ".java") for name in
            ("ApiMetricHttpHandler", "ApiServiceMetricBinding", "ApiDbPoolMetricBinding",
             "DbPoolMetricObservation", "DbPoolMetricRecorder", "OutboxRowsMetricRecorder",
             "OutboxAgeMetricRecorder", "DbPoolMetricCollector", "persistence/OutboxObservationRepository"))
assert len(set(main)) == 23
old_inputs = original["begin"]["sourceHashes"]
test = Path(str(base).replace("/src/main/", "/src/test/"))
fixtures = [test / f"{name}.java" for name in ("ApiMetricHttpHandlerTest", "DbPoolMetricObservationTest")]
held_types = ("TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec",
              "WebStartupException")
inputs = []
changed = []
for path in main + fixtures:
    revision = ctx["productionCoreMain"] if path in main else ctx["source"]
    payload = subprocess.check_output(["git", "show", f"{revision}:{path}"], timeout=15)
    assert payload == path.read_bytes()
    assert not any(held.encode() in payload for held in held_types)
    item = pin(path)
    inputs.append(item)
    prior = old_inputs.get(str(path)) if path in main else original["begin"]["testSourceHashes"].get(str(path.resolve()))
    assert prior
    if item["sha256"] != prior:
        changed.append(path.name)
assert sorted(changed) == ["ApiStandardMetricSource.java", "DbPoolMetricObservationTest.java",
                           "OutboxObservationRepository.java"]
deps = context["runtimeJarHashes"] + [
    dict(path=p, sha256=h) for p, h in original["begin"]["dependencyHashes"].items()
    if Path(p).name in {"HikariCP-7.1.0.jar", "slf4j-api-2.0.18.jar"}]
evidence = Path(refs[3]["path"]).parent.parent
libraries_receipt = next(evidence.glob("PG40802-*/manifest.json"))
libraries = json.loads(libraries_receipt.read_bytes())
assert libraries["actualExit"] == 0
for tree in ("src/schubert-nk-protocol", "pom.xml", ".mvn"):
    previous, current = subprocess.check_output(
        ["git", "rev-parse", f'{libraries["source"]}:{tree}', f'{ctx["productionCoreMain"]}:{tree}'],
        timeout=15).splitlines()
    assert previous == current
jar = libraries["packaged"]["protocol"]
deps.append(dict(path=jar["path"], sha256=jar["sha256"]))
assert len(deps) == 16 and all(pin(Path(row["path"])) == row for row in deps)
first = evidence / ctx["run"] / "manifest.json"
first_report = json.loads(first.read_bytes())
assert first_report["actualExit"] == 1 and first_report["counts"] == {}
assert [step["step"] for step in first_report["stages"]] == ["compile"]
cp = ":".join(row["path"] for row in deps)
tc = Path("../toolchain").resolve()
jdk = tc / "jdk-25.0.4/bin"
junit = tc / "junit-platform-console-standalone-1.13.4.jar"
agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
cli = tc / "org.jacoco.cli-0.8.15-nodeps.jar"
environment = {"PATH": f"{jdk}:/usr/bin:/bin", "LANG": "C.UTF-8"}
slot = Path("../pgpt-runs/PG379").resolve() / (ctx["run"].removesuffix("-v1") + "-v2")
slot.mkdir(mode=0o700)
out = evidence / (ctx["run"].removesuffix("-v1") + "-v2")
out.mkdir()
classes, reports, exec_data = (slot / name for name in ("classes", "reports", "unit.exec"))
tmp = slot / "tmp"
tmp.mkdir()
props = slot / "empty-prometheus.properties"
props.touch()
stages = []


def run(step, *command):
    args = list(map(str, command))
    result = subprocess.run(args, env=environment, capture_output=True, timeout=90)
    stages.append(dict(step=step, command=args, exitCode=result.returncode,
                       stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr)))
    if result.returncode:
        (slot / f"{step}.stdout").write_bytes(result.stdout)
        (slot / f"{step}.stderr").write_bytes(result.stderr)
        if step == "compile":
            print(result.stderr.decode(errors="replace")[:5000])
    return result.returncode


started = now()
cc = run("compile", jdk / "javac", "--release", "25", "-g", "-proc:none", "-Xlint:all",
         "-Werror", "-implicit:none", "-sourcepath", "", "-cp", cp, "-d", classes, *main, *fixtures)
counts, seen, coverage = {}, set(), None
stage_exit = cc
init = slot / "class-init.log"
held_loaded = None
raw_unit = None
session = "PG40942-CURRENT-API-MEMORY-HANDLER23"
if cc == 0:
    (classes / "prometheus.properties").touch()
    stage_exit = run(
        "unit", jdk / "java", f"-Djava.io.tmpdir={tmp}", f"-Dprometheus.config={props}",
        "-Duser.timezone=Asia/Tokyo", "-Dfile.encoding=UTF-8",
        "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.extensions.autodetection.enabled=false",
        f"-Xlog:class+init=info:file={init}",
        f"-javaagent:{agent}=destfile={exec_data},append=false,sessionid={session},includes=dev.codex.schubert.nk.api.monitoring.*",
        "-jar", junit, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
        "--class-path", f"{classes}:{cp}", "--select-class",
        "dev.codex.schubert.nk.api.monitoring.ApiMetricHttpHandlerTest", "--reports-dir", reports)
    xml = reports / "TEST-junit-jupiter.xml"
    held_loaded = sum(init.read_bytes().count(name.encode()) for name in held_types)
    if xml.is_file():
        raw_unit = pin(xml)
        unit = ET.parse(xml).getroot()
        counts = {key: int(unit.attrib[key]) for key in ("tests", "errors", "failures", "skipped")}
        seen = {(c.attrib["classname"], c.attrib["name"].removesuffix("()"))
                for c in unit.findall("testcase")
                if not any(child.tag in {"failure", "error", "skipped"} for child in c)}
    if stage_exit == 0 and counts == dict(tests=23, errors=0, failures=0, skipped=0) and seen == expected and held_loaded == 0:
        xml = out / "coverage.xml"
        target = classes / "dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandler.class"
        stage_exit = run("coverage", jdk / "java", "-jar", cli, "report", exec_data,
                         "--classfiles", target, "--xml", xml)
        if stage_exit == 0:
            report = ET.parse(xml).getroot()
            assert report.find("sessioninfo").attrib["id"] == session
            node, = report.findall("./package/class")
            coverage = dict(xml=pin(xml), target=pin(target), session=session, exec=pin(exec_data),
                            counters=[item.attrib for item in node.findall("counter")])
record = dict(actualExit=0 if coverage else 1, source=ctx["productionCoreMain"], testSource=ctx["source"],
              startEvent=start["eventId"], startedAtUTC=started, terminalAtUTC=now(),
              inputPins=inputs, dependencyPins=deps, original=refs[1], independentOracle=refs[2],
              protocolBuild=pin(libraries_receipt), priorPreparationAttempt=pin(first),
              changedSourceNames=changed, stages=stages, counts=counts, unitXml=raw_unit,
              actualCases=[dict(className=c, method=m) for c, m in sorted(seen)],
              coverage=coverage, heldInitializationsObserved=held_loaded,
              actualNetworkOrDatabaseActions=0, fixedMemoryFixture=True, oldCoverageCombined=False,
              newlyDefinedTests=0, formalDelta=0, whole451=False)
(out / "manifest.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
print(record["actualExit"], counts, held_loaded, coverage["counters"] if coverage else None)
raise SystemExit(record["actualExit"])
