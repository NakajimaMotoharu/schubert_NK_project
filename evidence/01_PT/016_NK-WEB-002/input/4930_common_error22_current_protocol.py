"""Requalify the retained Web error fixture with the current qualified Protocol artifact."""
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=25)


pmo = Path("documents/400_PGPT/470_PMO")
start = json.loads(next(pmo.glob("601_*/1358_*")).read_bytes())
ctx = start["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
delta, prepared, preflight, original, libraries, current_batch = [
    json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:]]
assert all(row["actualExit"] == 0 for row in (delta, prepared, preflight, original, libraries, current_batch))
assert prepared["expectedTests"] == original["tests"] == 22
assert preflight["actualBackendOrHeldClassActions"] == 0
core = ctx["productionCoreMain"]
assert current_batch["source"] == core and delta["source"] == core
proto = libraries["packaged"]["protocol"]
assert proto == current_batch["priorSourceUnchangedLibraryReferences"]["protocol"]
protocol = Path(proto["path"])
assert pin(protocol)["sha256"] == proto["sha256"]
for tree_path in ("src/schubert-nk-protocol", "pom.xml", ".mvn"):
    assert git("rev-parse", f'{libraries["source"]}:{tree_path}') == git("rev-parse", f"{core}:{tree_path}")
web = [path for path in prepared["inputHashes"] if path.startswith("src/schubert-nk-web/")
       and path.endswith(".java") and "/src/main/" in path]
fixtures = prepared["apiTestSources"]
assert len(web) == 15 and len(fixtures) == 3
for path in web + fixtures:
    revision = core if path in web else ctx["source"]
    assert sha(git("show", f"{revision}:{path}")) == prepared["inputHashes"][path]
    assert pin(Path(path))["sha256"] == prepared["inputHashes"][path]

toolchain = Path("../toolchain").resolve()
jdk = toolchain / "jdk-25.0.4"
console = toolchain / "junit-platform-console-standalone-1.13.4.jar"
agent = toolchain / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
cli = toolchain / "org.jacoco.cli-0.8.15-nodeps.jar"
runs = Path("../pgpt-runs/PG379").resolve()
old = runs / "pg28014-common-error22-normal-v1"
deps = []
old_proto = None
for name, expected in prepared["dependencies"].items():
    path = Path(name)
    if path.name == protocol.name:
        assert old_proto is None and expected != proto["sha256"]
        old_proto = dict(path=name, sha256=expected)
        deps.append(protocol)
    else:
        allowed = path == old / "cached-error-root13.jar" or path == console or path.is_relative_to(toolchain / "m2/repository")
        assert allowed and pin(path)["sha256"] == expected
        deps.append(path)
assert old_proto and len(deps) == len(set(deps)) == 26 and console in deps

private = runs / ctx["run"]
out = Path("evidence/01_PT/016_NK-WEB-002/evidence") / ctx["run"]
assert not out.exists() and not private.exists()
private.mkdir(mode=0o700)
unit_classes = private / "units"
product_classes = private / "products"
admitted_classes = []
for field, origin, destination, count in (
        ("mainClassHashes", old / "target/classes", product_classes, 4),
        ("testClassHashes", old / "test-classes", unit_classes, 7)):
    original_classes = prepared[field]
    assert len(original_classes) == count
    for name, expected in original_classes.items():
        assert name.startswith("dev/codex/schubert/nk/web/") and name.endswith(".class")
        target = destination / name
        source_file = origin / name
        assert pin(source_file)["sha256"] == expected
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, target)
        admitted_classes.append(pin(target))

cache = old / "cached-error-root13.jar"
with ZipFile(cache) as archive:
    support_classes = [name for name in archive.namelist() if name.endswith(".class")]
    assert len(support_classes) == 13 and len(set(support_classes)) == 13
    assert all(name.startswith("dev/codex/schubert/nk/web/") for name in support_classes)
    targets = {
        "dev/codex/schubert/nk/web/controller/ErrorController",
        "dev/codex/schubert/nk/web/view/ErrorViewModel",
        "dev/codex/schubert/nk/web/view/ErrorViewModel$Status",
        "dev/codex/schubert/nk/web/error/ProblemViewFactory",
        "dev/codex/schubert/nk/web/error/WebResultMapper",
        "dev/codex/schubert/nk/web/security/WebErrorDispatchFilter",
    }
    target_files = []
    for binary in sorted(targets):
        filename = binary + ".class"
        if filename in support_classes:
            copied = private / "report" / filename
            data = archive.read(filename)
            assert sha(data) == prepared["physicalClassHashes"][filename]
            copied.parent.mkdir(parents=True, exist_ok=True)
            copied.write_bytes(data)
        else:
            copied = product_classes / filename
        assert copied.is_file()
        target_files.append(copied)

out.mkdir()
tmp = private / "tmp"
tmp.mkdir()
environment = os.environ.copy()
for key in ("CLASSPATH", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS"):
    environment.pop(key, None)
environment["LC_ALL"] = "C"
session = "PG40932-CURRENT-PROTOCOL-COMMON-ERROR22"
exec_data = private / "unit.exec"
class_init = private / "class-init.log"
report = private / "xml"
cmd = [
    jdk / "bin/java", f"-Djava.io.tmpdir={tmp}", "-Dfile.encoding=UTF-8", "-Duser.timezone=Asia/Tokyo",
    "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.extensions.autodetection.enabled=false",
    f"-javaagent:{agent}=destfile={exec_data},sessionid={session},append=false",
    f"-Xlog:class+init=info:file={class_init}", "-jar", console, "execute", "--disable-ansi-colors",
    "--class-path", ":".join(map(str, [product_classes, unit_classes, *deps])),
    *[value for name in prepared["selectedClasses"] for value in ("--select-class", name)],
    "--reports-dir", report, "--fail-if-no-tests", "--details", "summary",
]
started = now()
result = subprocess.run(list(map(str, cmd)), cwd=private, env=environment, capture_output=True, timeout=120)
(private / "unit-stdout").write_bytes(result.stdout)
(private / "unit-stderr").write_bytes(result.stderr)
suite = report / "TEST-junit-jupiter.xml"
counts = {}
seen = set()
if suite.is_file():
    root = ET.parse(suite).getroot()
    counts = {key: int(root.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    for case in root.findall("testcase"):
        if not any(child.tag in {"failure", "error", "skipped"} for child in case):
            seen.add((case.attrib["classname"], case.attrib["name"]))
expected_cases = {(x["classname"], x["name"]) for x in prepared["expectedCases"]}
assert len(expected_cases) == 22
held_binaries = ("TemporaryInfrastructureException", "FingerprintKeyRing",
                 "ResponseSnapshotCodec", "WebStartupException")
held_initialization_observed = sum(class_init.read_bytes().count(name.encode()) for name in held_binaries)
tests_pass = (result.returncode == 0 and seen == expected_cases
              and counts == dict(tests=22, failures=0, errors=0, skipped=0)
              and held_initialization_observed == 0)
coverage = {}
coverage_command = None
coverage_exit = None
if tests_pass:
    xml = out / "coverage.xml"
    command = [jdk / "bin/java", "-jar", cli, "report", exec_data,
               *[item for path in target_files for item in ("--classfiles", path)],
               "--xml", xml.resolve()]
    coverage_command = list(map(str, command))
    check = subprocess.run(coverage_command, cwd=private, env=environment, capture_output=True, timeout=35)
    coverage_exit = check.returncode
    if coverage_exit == 0:
        items = ET.parse(xml).getroot().findall("package/class")
        assert {node.attrib["name"] for node in items} == targets
        coverage = {node.attrib["name"]: [c.attrib for c in node.findall("counter")] for node in items}

exit_code = 0 if tests_pass and coverage_exit == 0 else 1
record = dict(
    actualExit=exit_code, source=core, testSource=ctx["source"], startEvent=start["eventId"],
    startedAtUTC=started, terminalAtUTC=now(), originalProof=refs[4], evaluatedCurrentProtocol=proto,
    originalProtocol=old_proto, unchangedDependencyCount=25,
    qualifiedSourceInputs=[pin(Path(p)) for p in web + fixtures], retainedClasses=admitted_classes,
    unitCommand=list(map(str, cmd)), unitExit=result.returncode,
    counts=counts, passingCases=[dict(className=c, method=m) for c, m in sorted(seen)],
    junitXml=pin(suite) if suite.is_file() else None, newOriginalCaseCount=0,
    requiredRequalificationCount=22 if tests_pass else 0, classInitHeldHits=held_initialization_observed,
    execData=pin(exec_data) if exec_data.is_file() else None, session=session,
    coverageCommand=coverage_command, coverageExit=coverage_exit, targetDefaultCoverage=coverage,
    coverageXml=pin(out / "coverage.xml") if coverage else None,
    tools=list(map(pin, [jdk / "release", console, agent, cli])),
    newArtifactBuilds=0, oldExecCombined=False, liveBackendActions=0, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
print(exit_code, counts, len(coverage))
raise SystemExit(exit_code)
