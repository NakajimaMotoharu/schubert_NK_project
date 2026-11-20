"""Run only RRF-PURE-009 against the frozen, synthetic JDBC closure."""
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def execute(command):
    args = list(map(str, command))
    result = subprocess.run(args, capture_output=True, check=False, text=True,
                            env=environment, timeout=45)
    stages.append(dict(command=args, exitCode=result.returncode))
    if result.returncode:
        print(result.stdout)
        print(result.stderr)
    return result.returncode


start_path = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1331_*"))
group = json.loads(start_path.read_bytes())
ctx = group["values"]
source = ctx["productionCoreMain"]
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
batch = Path("src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository")
sources = [batch / (name + ".java") for name in
           ("BatchRepositoryException", "BatchRun", "JdbcResourceFailures",
            "RunReferenceRepository", "RunReferences")]
sources += [
    Path("src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph.java"),
    Path("src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java"),
]
for path in sources:
    fixed = subprocess.check_output(["git", "show", f"{source}:{path}"], timeout=10)
    assert path.read_bytes() == fixed
test = Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/RunReferenceRepositoryPureJdbcTest.java")
spec = Path("evidence/01_PT/004_NK-DAT-001/455_P00403参照DAO三経路例外順位仕様.md")
test_id = "RRF-PURE-009"
class_name = "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryPureJdbcTest"
method = "combinedReadAndCloseSqlFailuresKeepFirstFatalAndReleaseBothResources"
toolchain = Path("/home/mini/codex/project1/work/toolchain")
jdk = toolchain / "jdk-25.0.4"
junit = toolchain / "junit-platform-console-standalone-1.13.4.jar"
jspecify = toolchain / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
agent = toolchain / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
cli = toolchain / "org.jacoco.cli-0.8.15-nodeps.jar"
environment = os.environ.copy()
for key in ("CLASSPATH", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS"):
    environment.pop(key, None)
environment["LC_ALL"] = "C"
stages = []
out = Path("evidence/01_PT/004_NK-DAT-001/evidence") / ctx["run"]
out.mkdir()
opened = datetime.now(timezone.utc).isoformat()
cases = []
unit_count = None
unit_xml_hash = None
coverage = None
with tempfile.TemporaryDirectory(prefix="pg40914-rrf-", dir="/dev/shm") as name:
    scratch = Path(name)
    classes = scratch / "classes"
    reports = scratch / "unit"
    exec_data = scratch / "rrf.exec"
    target = classes / "dev/codex/schubert/nk/batch/repository/RunReferenceRepository.class"
    compile_exit = execute([
        jdk / "bin/javac", "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none",
        "-implicit:none", "-sourcepath", "", "-cp", f"{junit}:{jspecify}", "-d", classes,
        *sources, test,
    ])
    if compile_exit == 0:
        unit_exit = execute([
            jdk / "bin/java",
            f"-javaagent:{agent}=destfile={exec_data},append=false,sessionid=PG40914-RRF-PURE-009",
            "-jar", junit, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
            "--class-path", f"{classes}:{jspecify}", "--select-method", f"{class_name}#{method}",
            "--reports-dir", reports,
        ])
        xml = reports / "TEST-junit-jupiter.xml"
        if xml.is_file():
            unit_xml_hash = pin(xml)["sha256"]
            suite = ET.parse(xml).getroot()
            unit_count = {field: int(suite.attrib[field])
                          for field in ("tests", "failures", "errors", "skipped")}
            cases = [dict(className=node.attrib["classname"], method=node.attrib["name"])
                     for node in suite.findall("testcase")]
        if (unit_exit == 0 and unit_count == dict(tests=1, failures=0, errors=0, skipped=0)
                and cases == [dict(className=class_name, method=method + "()")]):
            xml = out / "coverage.xml"
            coverage_exit = execute([jdk / "bin/java", "-jar", cli, "report", exec_data,
                                     "--classfiles", target, "--xml", xml])
            if coverage_exit == 0:
                tree = ET.parse(xml).getroot()
                report_class, = tree.findall("package/class")
                assert report_class.attrib["name"] == "dev/codex/schubert/nk/batch/repository/RunReferenceRepository"
                coverage = dict(xml=pin(xml), execSha256=pin(exec_data)["sha256"],
                                targetClass=pin(target),
                                counters=[node.attrib for node in report_class.findall("counter")])

actual_exit = 0 if coverage is not None else 1
observed = dict(actualExit=actual_exit, source=source, startEvent=group["eventId"],
                startedAtUTC=opened, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                testId=test_id, independentOracle=pin(spec), fixture=pin(test),
                sourceClosure=list(map(pin, sources)), tools=list(map(pin, [jdk / "release", junit, jspecify, agent, cli])),
                stages=stages, observedJUnit=unit_count, observedCases=cases,
                originalPrivateJUnitXmlSha256=unit_xml_hash, distinctInputVariants=3,
                rawCoverageMeasured=False, scopedDefaultCoverage=coverage,
                priorProductSuccessReexecuted=0, realDbOrNativeActions=0,
                whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(observed, ensure_ascii=False, indent=2) + "\n")
print(actual_exit, unit_count, coverage["counters"] if coverage else None)
raise SystemExit(actual_exit)
