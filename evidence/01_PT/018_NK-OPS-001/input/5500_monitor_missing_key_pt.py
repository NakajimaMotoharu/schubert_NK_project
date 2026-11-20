"""Run the single new monitoring recovery case with the fixed pure Java closure."""
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


def now():
    return datetime.now(timezone.utc).isoformat()


group = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1368_*")).read_bytes())
ctx = group["values"]
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
root = Path("src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring")
main = [root / (name + ".java") for name in
        ("AlertLifecycle", "AlertRegistry", "AlertThresholds", "MonitoringModePolicy",
         "MonitoringPolicyEngine", "ObservationContext", "package-info")]
for source in main:
    frozen = subprocess.check_output(["git", "show", f'{ctx["productionCoreMain"]}:{source}'],
                                     timeout=10)
    assert frozen == source.read_bytes()
fixture = Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/MonitoringPolicyEngineTest.java")
spec = Path("evidence/01_PT/018_NK-OPS-001/5498_警報回復における観測欠落のキー分離仕様.md")
tc = Path("../toolchain").resolve()
jdk = tc / "jdk-25.0.4"
console = tc / "junit-platform-console-standalone-1.13.4.jar"
symbols = tc / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
jacoco = tc / "org.jacoco.cli-0.8.15-nodeps.jar"
formatter = tc / "google-java-format-1.36.1-all-deps.jar"
style = tc / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml")
env = os.environ.copy()
for key in ("CLASSPATH", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS"):
    env.pop(key, None)
env["LC_ALL"] = "C"
stages = []


def run(step, *command):
    args = list(map(str, command))
    p = subprocess.run(args, env=env, capture_output=True, timeout=40)
    stages.append(dict(step=step, command=args, exitCode=p.returncode,
                       stderrSha256=hashlib.sha256(p.stderr).hexdigest()))
    if p.returncode:
        print(p.stdout.decode(errors="replace")[-3000:])
        print(p.stderr.decode(errors="replace")[-3000:])
    return p


begin = now()
out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / ctx["run"]
out.mkdir()
info = {}
coverage = None
with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40938-") as name:
    temp = Path(name)
    classes, reports, exec_data = (temp / part for part in ("classes", "reports", "test.exec"))
    java = jdk / "bin/java"
    method = "monPipe008MissingObservationResetsOnlyItsConditionAndService"
    fqcn = "dev.codex.schubert.nk.batch.monitoring.MonitoringPolicyEngineTest"
    target = classes / "dev/codex/schubert/nk/batch/monitoring/MonitoringPolicyEngine.class"
    form = run("format", java, "-jar", formatter, "--dry-run", "--set-exit-if-changed", fixture)
    checkstyle = run("checkstyle", java, "-jar", style, "-c", rules, "-f", "xml", fixture)
    compiled = run("compile", jdk / "bin/javac", "--release", "25", "-g", "-Xlint:all", "-Werror",
                   "-proc:none", "-implicit:none", "-sourcepath", "", "-cp", f"{console}:{symbols}",
                   "-d", classes, *main, fixture)
    if form.returncode == checkstyle.returncode == compiled.returncode == 0:
        test = run("test", java, f"-javaagent:{agent}=destfile={exec_data},append=false,sessionid=PG40938-MONPIPE008",
                   "-jar", console, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                   "--class-path", f"{classes}:{symbols}", "--select-method", f"{fqcn}#{method}",
                   "--reports-dir", reports)
        xml = reports / "TEST-junit-jupiter.xml"
        if xml.is_file():
            suite = ET.parse(xml).getroot()
            info = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
            info["cases"] = [(case.attrib["classname"], case.attrib["name"])
                             for case in suite.findall("testcase")]
            info["privateJUnitSha256"] = pin(xml)["sha256"]
        if test.returncode == 0 and info.get("cases") == [(fqcn, method + "()")] and all(
                info[key] == value for key, value in dict(tests=1, failures=0, errors=0, skipped=0).items()):
            report = out / "coverage.xml"
            rc = run("coverage", java, "-jar", jacoco, "report", exec_data, "--classfiles", target,
                     "--xml", report)
            if rc.returncode == 0:
                class_row, = ET.parse(report).getroot().findall("./package/class")
                coverage = dict(xml=pin(report), target=pin(target), execSha256=pin(exec_data)["sha256"],
                                counters=[node.attrib for node in class_row.findall("counter")])
record = dict(actualExit=0 if coverage else 1, core=ctx["productionCoreMain"],
              startEvent=group["eventId"], startedAtUTC=begin, terminalAtUTC=now(),
              testId="PT-OPS-MONPIPE-008", test=pin(fixture), independentSpec=pin(spec),
              inputs=list(map(pin, main)), tools=list(map(pin, [jdk / "release", console, agent, jacoco,
                                                               formatter, style, rules])),
              stages=stages, observed=info, defaultCoverage=coverage, previousCasesRerun=0,
              actualExternalActions=0, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
print(record["actualExit"], info, coverage["counters"] if coverage else None)
raise SystemExit(record["actualExit"])
