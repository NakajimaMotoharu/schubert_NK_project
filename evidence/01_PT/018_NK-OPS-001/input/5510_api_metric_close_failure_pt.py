"""Run the new memory exchange cleanup invariant and measure its exact handler bytecode."""
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


group = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1377_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
unit, raw = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:3]]
assert unit["source"] == raw["source"] == ctx["productionCoreMain"]
assert unit["actualExit"] == raw["actualExit"] == 0 and unit["counts"]["tests"] == 23
fixture = Path("src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandlerTest.java")
assert all(pin(Path(row["path"])) == row for row in unit["inputPins"] + unit["dependencyPins"]
           if row["path"] != str(fixture))
spec = Path("evidence/01_PT/018_NK-OPS-001/5508_API監視応答の所有解放仕様.md")
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
steps = []
java = Path(unit["stages"][1]["command"][0])
tc = java.parents[2]
environment = {"PATH": f"{java.parent}:/usr/bin:/bin", "LANG": "C.UTF-8"}
expected = "apimhttp024OwnedCloseFailureKeepsThePrimaryWriteOutcome"
owner = "dev.codex.schubert.nk.api.monitoring.ApiMetricHttpHandlerTest"


def run(stage, command):
    args = list(map(str, command))
    result = subprocess.run(args, env=environment, capture_output=True, timeout=65, check=False)
    steps.append(dict(stage=stage, command=args, exitCode=result.returncode))
    if result.returncode:
        print(result.stderr.decode(errors="replace")[-3000:])
        print(result.stdout.decode(errors="replace")[-3000:])
    result.check_returncode()
    return result.stdout


with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40944-") as temp:
    slot = Path(temp)
    classes, reports, exec_data = (slot / name for name in ("classes", "reports", "unit.exec"))
    props = slot / "empty-prometheus.properties"
    props.touch()
    fmt = tc / "google-java-format-1.36.1-all-deps.jar"
    chk = tc / "static-gates-20261015/checkstyle-14.3.0-all.jar"
    run("format", [java, "-jar", fmt, "--dry-run", "--set-exit-if-changed", fixture])
    style = run("checkstyle", [java, "-jar", chk, "-c", "tools/quality/static/checkstyle.xml", "-f", "xml", fixture])
    assert not ET.fromstring(style).findall("file/error")
    compile_cmd = unit["stages"][0]["command"].copy()
    compile_cmd[compile_cmd.index("-d") + 1] = str(classes)
    run("compile", compile_cmd)
    (classes / "prometheus.properties").touch()
    target = classes / "dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandler.class"
    assert pin(target)["sha256"] == raw["target"]["sha256"]
    original = unit["stages"][1]["command"]
    original_cp = original[original.index("--class-path") + 1]
    libs = original_cp.split(":", 1)[1]
    console = original[original.index("-jar") + 1]
    agent = next(arg.split("=", 1)[0] for arg in original if arg.startswith("-javaagent:"))
    session = "PG40944-API-HANDLER-CLOSE-024"
    run("unit", [java, f"-Djava.io.tmpdir={slot}", f"-Dprometheus.config={props}",
                 f"{agent}=destfile={exec_data},sessionid={session},append=false",
                 "-jar", console, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                 "--class-path", f"{classes}:{libs}", "--select-method", f"{owner}#{expected}",
                 "--reports-dir", reports])
    report = reports / "TEST-junit-jupiter.xml"
    suite = ET.parse(report).getroot()
    counts = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    assert counts == dict(tests=1, failures=0, errors=0, skipped=0)
    testcase, = suite.findall("testcase")
    assert (testcase.attrib["classname"], testcase.attrib["name"]) == (owner, expected + "()")
    previous = json.loads(next(Path(refs[1]["path"]).parent.parent.glob("PG40904-*/manifest.json")).read_bytes())
    measurement = "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
    source = subprocess.check_output(["git", "show", "c5674055a6:" + measurement], timeout=15)
    assert sha(source) == previous["unfilteredToolSha256"]
    staged = slot / "UnfilteredCodeMeasurement.java"
    staged.write_bytes(source)
    cc = raw["compileCommand"]
    raw_libs = cc[cc.index("-cp") + 1]
    run("compile_raw", [*cc[:cc.index("-d")], "-d", slot, staged])
    table = out / "unfiltered.tsv"
    table.write_bytes(run("raw", [java, "-cp", f"{slot}:{raw_libs}", raw["rawCommand"][3],
                                 exec_data, target]))
    row, = (line.split("\t") for line in table.read_text().splitlines() if line.startswith("CLASS\t"))
    assert row[2] == raw["crc64"] and row[3] == "true"
    counters = [dict(kind=kind, missed=int(missed), covered=int(covered))
                for kind, missed, covered in (cell.split(":") for cell in row[6:])]
    run_pins = dict(execSha256=pin(exec_data)["sha256"], classSha256=pin(target)["sha256"],
                    crc64=row[2], session=session, junitSha256=pin(report)["sha256"], table=pin(table))
record = dict(actualExit=0, source=ctx["productionCoreMain"], startEvent=group["eventId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), testId="APIMHTTP024",
              fixture=pin(fixture), independentSpec=pin(spec), previousRun=refs[1], stages=steps,
              counts=counts, rawCounters=counters, runPins=run_pins, existingTestsRerun=0,
              actualExternalActions=0, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(counts, counters)
