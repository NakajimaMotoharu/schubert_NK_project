"""Measure the three changed SDK owner classes in one current ordinary test execution."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import shutil
import subprocess
import tempfile


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start = read(next(plan.glob("1319_*")))
ctx = start["values"]
core = ctx["productionCoreMain"]
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
batch, api, web, typed, raw_reference = [read(Path(row["path"])) for row in ctx["oracleReferences"][1:]]
runs = (batch, api, web)
assert all(run["actualExit"] == 0 for run in runs)
inputs = [row for run in runs for row in [*run["productionInputs"], run["testInput"]]]
assert len(inputs) == len({row["path"] for row in inputs}) == 23
assert all(pin(Path(row["path"])) == row for row in inputs)
for row in inputs:
    expected_bytes = subprocess.check_output(["git", "show", f'{core}:{row["path"]}'], timeout=20)
    assert sha(expected_bytes) == row["sha256"]
assert typed["source"] == core
typed_inventory = {row["classPath"]: row["sha256"] for row in typed["physicalInventory"]}
target_members = typed["changedClasses"]
assert len(target_members) == 3 and len(typed_inventory) == 27
expected = {case["method"] for run in runs for case in run["selectedCases"]}
assert len(expected) == 51
chosen_targets = [p.removesuffix(".class").replace("/", ".") for p in target_members]
deps = batch["runtimeDependencies"]
assert len(deps) == 12 and all(run["runtimeDependencies"] == deps for run in runs)
assert all(pin(Path(row["path"])) == row for row in deps)

project = Path.cwd()
tc = project.parent / "toolchain"
java = tc / "jdk-25.0.4/bin/java"
junit = tc / "junit-platform-console-standalone-1.13.4.jar"
agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
cli = tc / "org.jacoco.cli-0.8.15-nodeps.jar"
retained_tool = "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
raw_tool_bytes = subprocess.check_output(["git", "show", "c5674055a6:" + retained_tool], timeout=20)
raw_sdk = raw_reference["steps"]["rawCompile"]["command"][6]
assert all(Path(path).is_relative_to(tc) for path in raw_sdk.split(":"))
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
out = evidence / ctx["run"]
out.mkdir()
started = datetime.now(timezone.utc).isoformat()
stages = {}


def run(label, *args):
    argv = list(map(str, args))
    data = subprocess.run(argv, capture_output=True, timeout=100)
    stages[label] = dict(command=argv, exit=data.returncode, stdoutSha256=sha(data.stdout),
                         stderrSha256=sha(data.stderr))
    if data.returncode and label != "unit":
        print(label, data.stderr.decode(errors="replace")[:1300])
    return data


cases = []
quality = {}
private_exec = None
default_receipt = raw_receipt = junit_xml_hash = None
did_match = False
with tempfile.TemporaryDirectory(prefix="pg40904-", dir="/dev/shm") as location:
    where = Path(location)
    classes, reports, raw = (where / name for name in ("classes", "reports", "raw"))
    reports.mkdir()
    runtime_cp = ":".join(row["path"] for row in deps)
    status = run("compile", java.with_name("javac"), "--release", 25, "-g", "-Xlint:all", "-Werror",
                 "-proc:none", "-cp", f"{runtime_cp}:{junit}", "-d", classes, *[r["path"] for r in inputs]).returncode
    target_files = [classes / name for name in target_members]
    if status == 0:
        assert all(pin(classes / path)["sha256"] == stamp for path, stamp in typed_inventory.items())
        did_match = True
        exec_path = where / "unit.exec"
        session = "PG40904-CURRENT-THREE-STANDARD-SDK-OWNERS"
        agent_flags = (f"-javaagent:{agent}=destfile={exec_path},sessionid={session},append=false,"
                       f"includes={':'.join(chosen_targets)}")
        status = run("unit", java, agent_flags, "-jar", junit, "execute", "--disable-banner", "--disable-ansi-colors",
                     "--class-path", f"{classes}:{runtime_cp}", "--reports-dir", reports, "--fail-if-no-tests",
                     *[arg for name in chosen_targets for arg in ("--select-class", name + "Test")]).returncode
        junit_xml = reports / "TEST-junit-jupiter.xml"
        if junit_xml.is_file():
            junit_xml_hash = pin(junit_xml)["sha256"]
            for case in ET.parse(junit_xml).getroot().findall("testcase"):
                outcome = next((tag for tag in ("failure", "error", "skipped") if case.find(tag) is not None),
                               "passed")
                cases.append(dict(classname=case.attrib["classname"],
                                  method=case.attrib["name"].removesuffix("()"), outcome=outcome))
        if status == 0:
            assert len(cases) == 51 and {case["method"] for case in cases} == expected
            assert all(c["outcome"] == "passed" for c in cases)
            private = project.parent / "pgpt-runs/PG379" / ctx["run"]
            private.mkdir(mode=0o700)
            saved_exec = private / "unit.exec"
            shutil.copyfile(exec_path, saved_exec)
            for class_path in target_files:
                shutil.copyfile(class_path, private / class_path.name)
            private_exec = pin(saved_exec)
            default_report = out / "coverage.xml"
            cov_args = [arg for target in target_files for arg in ("--classfiles", target)]
            status = run("default", java, "-jar", cli, "report", exec_path, *cov_args,
                         "--xml", default_report).returncode
            if status == 0:
                assert [node.attrib["id"] for node in ET.parse(default_report).getroot().findall("sessioninfo")] == [session]
                default_receipt = pin(default_report)
                raw_source = where / "UnfilteredCodeMeasurement.java"
                raw_source.write_bytes(raw_tool_bytes)
                status = run("rawCompile", java.with_name("javac"), "--release", 25, "-Xlint:all", "-Werror",
                             "-cp", raw_sdk, "-d", raw, raw_source).returncode
                if status == 0:
                    raw_result = run("unfiltered", java, "-cp", f"{raw}:{raw_sdk}",
                                     "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                                     "--line-deficits", exec_path, *target_files)
                    status = raw_result.returncode
                    if status == 0:
                        raw_tsv = out / "unfiltered.tsv"
                        raw_tsv.write_bytes(raw_result.stdout)
                        raw_receipt = pin(raw_tsv)
                        for line in raw_result.stdout.decode().splitlines():
                            row = line.split("\t")
                            if row[0] == "CLASS":
                                assert row[3] == "true"
                                values = {}
                                for counter in row[6:]:
                                    key, missed, covered = counter.split(":")
                                    values[key] = dict(missed=int(missed), covered=int(covered))
                                quality[row[1]] = dict(crc64=row[2], probes=int(row[4]), counters=values)
                        assert {s.replace("/", ".") for s in quality} == set(chosen_targets)
record = dict(actualExit=status, source=core, startEvent=start["eventId"], startedAtUTC=started,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), sourceInputs=inputs, productBuildByteMatched=did_match,
              steps=stages, tests=cases, junitXmlSha256=junit_xml_hash, defaultCoverage=default_receipt,
              unfilteredCoverage=raw_receipt, ownSyntheticExecPrivate=private_exec,
              unfilteredToolSha256=sha(raw_tool_bytes), currentSingleExecTargetCounters=quality,
              measuredClasses=3 if quality else 0, supportPhysicalOutsideTargetMeasurement=24,
              newProductTests=0, actualNativeOrExternalOperations=0, whole451=False, formalDelta=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(status, len(cases), quality, pin(manifest))
raise SystemExit(status)
