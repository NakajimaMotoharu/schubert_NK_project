"""Run only the new status catalog case with the already qualified Web error runtime."""
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def execute(args, folder):
    command = list(map(str, args))
    result = subprocess.run(command, cwd=folder, env=environment, capture_output=True,
                            timeout=45, check=False)
    return command, result


root = Path("evidence/01_PT")
start = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1361_*")).read_bytes())
ctx = start["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
unit, raw = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:3]]
assert unit["source"] == raw["source"] == ctx["productionCoreMain"]
assert unit["actualExit"] == raw["actualExit"] == 0
for entry in unit["retainedClasses"] + raw["targetClasses"]:
    assert pin(Path(entry["path"])) == entry
previous_deps = json.loads(next((root / "018_NK-OPS-001/evidence").glob("PG28014-*/manifest.json")).read_bytes())
command = unit["unitCommand"]
prior_classpath = command[command.index("--class-path") + 1]
libraries = prior_classpath.split(":")[2:]
for entry in libraries:
    old_sha = previous_deps["dependencies"].get(entry)
    if entry == unit["evaluatedCurrentProtocol"]["path"]:
        old_sha = unit["evaluatedCurrentProtocol"]["sha256"]
    assert old_sha and pin(Path(entry))["sha256"] == old_sha
status, = (entry for entry in raw["targetClasses"] if entry["path"].endswith("/ErrorViewModel$Status.class"))
test = Path("tools/quality/architecture/ErrorValueContractTest.java").resolve()
spec = Path("evidence/01_PT/016_NK-WEB-002/4933_P01624公開error状態単体仕様.md")
selector = "dev.codex.schubert.nk.web.error.ErrorValueContractTest#errorValue007PublicStatusCatalogIsClosedAndEachNameRetainsItsHttpStatus"
java = Path(command[0])
toolchain = java.parents[2]
console = Path(command[command.index("-jar") + 1])
agent = Path(next(x for x in command if x.startswith("-javaagent:")).split("=", 1)[0][11:])
rules = Path("tools/quality/static/checkstyle.xml").resolve()
style = toolchain / "static-gates-20261015/checkstyle-14.3.0-all.jar"
formatter = toolchain / "google-java-format-1.36.1-all-deps.jar"
environment = os.environ.copy()
for key in ("CLASSPATH", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS"):
    environment.pop(key, None)
environment["LC_ALL"] = "C"
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
assert not out.exists()
out.mkdir()
stages = []
observed = {}
measured = None


def step(name, args, folder):
    command, result = execute(args, folder)
    stages.append(dict(step=name, command=command, exitCode=result.returncode,
                       stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr)))
    return result


with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40934-") as temp:
    work = Path(temp)
    test_classes = work / "test-classes"
    tools = work / "raw-tool"
    exec_data = work / "enum.exec"
    junit_reports = work / "junit"
    fix = step("format", [java, "-jar", formatter, "--dry-run", "--set-exit-if-changed", test], work)
    cs = step("checkstyle", [java, "-jar", style, "-c", rules, "-f", "xml", test], work)
    assert fix.returncode == cs.returncode == 0
    assert not ET.fromstring(cs.stdout).findall("file/error")
    compiler = java.with_name("javac")
    compiled = step("compile", [compiler, "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                                "-implicit:none", "-sourcepath", "", "-cp", prior_classpath,
                                "-d", test_classes, test], work)
    assert compiled.returncode == 0
    session = "PG40934-CURRENT-ERROR-VALUE007"
    run = step("unit", [java, f"-Djava.io.tmpdir={work}", "-Duser.timezone=Asia/Tokyo",
                       f"-javaagent:{agent}=destfile={exec_data},append=false,sessionid={session}",
                       "-jar", console, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                       "--class-path", f"{test_classes}:{prior_classpath}", "--select-method",
                       selector, "--reports-dir", junit_reports], work)
    xml = junit_reports / "TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    observed = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    assert run.returncode == 0 and observed == dict(tests=1, failures=0, errors=0, skipped=0)
    case, = suite.findall("testcase")
    owner, method = selector.split("#")
    assert case.attrib["classname"] == owner and case.attrib["name"] == method + "()"
    raw_source = subprocess.check_output(
        ["git", "show", raw["measurementTool"]["revision"] + ":" + raw["measurementTool"]["path"]],
        timeout=15)
    assert sha(raw_source) == raw["measurementTool"]["sha256"]
    source_file = work / "UnfilteredCodeMeasurement.java"
    source_file.write_bytes(raw_source)
    base = raw["compileCommand"]
    raw_cp = base[base.index("-cp") + 1]
    compile_raw = step("raw_compile", [*base[:base.index("-d")], "-d", tools, source_file], work)
    assert compile_raw.returncode == 0
    coverage = step("raw", [java, "-cp", f"{tools}:{raw_cp}", raw["rawCommand"][3], exec_data,
                           status["path"]], work)
    assert coverage.returncode == 0
    row, = (line.split("\t") for line in coverage.stdout.decode().splitlines() if line.startswith("CLASS\t"))
    assert row[1].endswith("/ErrorViewModel$Status") and row[3] == "true"
    measured = [dict(kind=kind, missed=int(missed), covered=int(covered))
                for kind, missed, covered in (cell.split(":") for cell in row[6:])]
    assert all(counter["missed"] == 0 for counter in measured)
    table = out / "status-unfiltered.tsv"
    table.write_bytes(coverage.stdout)
    evidence = dict(unitXmlSha256=pin(xml)["sha256"], unitExecSha256=pin(exec_data)["sha256"],
                    session=session, rawTable=pin(table), classCrc64=row[2])
receipt = dict(actualExit=0, source=ctx["productionCoreMain"], startEvent=start["eventId"],
               terminalAtUTC=datetime.now(timezone.utc).isoformat(),
               testId="ERROR-VALUE007", fixture=pin(test), specification=pin(spec), runtime=refs[1],
               selectedCase=selector, testCounts=observed, stages=stages, statusClass=status,
               measured=measured, rawOutline=evidence, prior22Reexecutions=0,
               externalActions=0, combinedAcrossRuns=False, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(observed, measured)
