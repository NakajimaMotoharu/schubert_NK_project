from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os, platform, re, subprocess, tempfile
from xml.etree import ElementTree as ET

repo = Path.cwd()
tools = repo.parent / "toolchain"
vpath = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1208_*"))
start = json.loads(vpath.read_bytes())
ctx = start["values"]
core = ctx["productionCoreMain"]
start_time = datetime.now(timezone.utc).isoformat()
namespace = "dev/codex/schubert/nk/batch/monitoring"
module = Path("src/schubert-nk-batch/src")
main = module / "main/java" / namespace
test_names = ("TransferHealthMonitorTest",)
test_paths = [module / "test/java" / namespace / f"{name}.java" for name in test_names]
owned = [main / f"{name}.java" for name in (
    "AlertLifecycle", "AlertThresholds", "TransferHealthMonitor", "TransferMetricRecorder",
    "MetricContract", "MonitoringModePolicy", "MonitoringObservationClock",
    "MonitoringPoller", "ObservationContext", "package-info",
)]
def sha(data):
    return hashlib.sha256(data).hexdigest()
def ref(p):
    return {"path":str(p),"sha256":sha(p.read_bytes())}
for p in owned:
    assert p.read_bytes() == subprocess.check_output(["git","show",f"{core}:{p}"])
assert len(owned) == 10
for p in test_paths:
    assert p.read_bytes() == subprocess.check_output(['git','show',f"{ctx['source']}:{p}"])

jdk = tools / "jdk-25.0.4/bin"
sdk = tools / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
pin_source = Path("tools/quality/pg7106_micrometer_http_host.py")
pins = re.findall(r"\('([^']+\.jar)','([a-f0-9]{64})'\)", pin_source.read_text())
assert len(pins) == 4
external = [tools / "m2/repository" / path for path, _ in pins]
assert all(sha(path.read_bytes()) == expected for path, (_, expected) in zip(external, pins))
sdk_classpath = ":".join(map(str, (sdk, *external)))
junit = tools / "junit-platform-console-standalone-1.13.4.jar"
agent = tools / "m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
jacoco = tools / "org.jacoco.cli-0.8.15-nodeps.jar"
fmt = tools / "google-java-format-1.36.1-all-deps.jar"
cs = tools / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml")
run_dir = Path("evidence/01_PT/018_NK-OPS-001/evidence") / "PG40816-c07-transfer-new-source-v2"
run_dir.mkdir()
steps, cases, scope_coverage = {}, [], None
recorded_class_names = []
code = 1
suite_prefix = namespace.replace("/", ".")
selectors = [token for name in test_names for token in ("--select-class",f"{suite_prefix}.{name}")]
with tempfile.TemporaryDirectory(prefix="pg40816-", dir="/dev/shm") as temp:
    scratch = Path(temp)
    product, fixture = scratch / "product", scratch / "fixture"
    product.mkdir()
    fixture.mkdir()
    xml, cov, data = scratch/"checkstyle.xml", scratch/"coverage.xml", scratch/"selected.exec"
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    def command(name, *values):
        cmd = [str(v) for v in values]
        cp = subprocess.run(cmd,capture_output=True,timeout=45,env=env)
        steps[name] = dict(command=cmd,exit=cp.returncode,stdoutSha256=sha(cp.stdout),stderrSha256=sha(cp.stderr))
        if cp.returncode:
            print(name,cp.returncode,cp.stderr.decode(errors="replace")[:1300])
        return cp.returncode
    if (command("format",jdk/"java","-jar",fmt,"--skip-reflowing-long-strings","--dry-run",
                "--set-exit-if-changed",*test_paths) == 0
        and command("checkstyle",jdk/"java","-jar",cs,"-c",rules,"-f","xml","-o",xml,*test_paths)==0
        and command("mainCompile",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
                    "-cp",sdk_classpath,"-d",product,*owned)==0
        and command("testCompile",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
                    "-cp",f"{product}:{junit}:{sdk_classpath}","-d",fixture,*test_paths)==0):
        assert not ET.parse(xml).getroot().findall(".//error")
        recorded_class_names = sorted(str(p.relative_to(product)) for p in product.rglob("*.class"))
        assert all(p.startswith(namespace+"/") and p.count("/")==namespace.count("/")+1
                   for p in recorded_class_names)
        report_dir = scratch / "test"
        agent_config = f"-javaagent:{agent}=destfile={data},append=false,sessionid=PG40816-v2"
        code = command("test",jdk/"java",agent_config,"-jar",junit,"execute","--disable-banner",
                       "--disable-ansi-colors","--class-path",f"{product}:{fixture}:{sdk_classpath}",
                       *selectors,"--reports-dir",report_dir,"--fail-if-no-tests")
        report = report_dir / "TEST-junit-jupiter.xml"
        if report.is_file():
            steps["test"]["xmlSha256"] = sha(report.read_bytes())
            for case in ET.parse(report).getroot().findall("testcase"):
                owner = case.attrib["classname"].rsplit(".",1)[-1]
                assert owner in test_names
                method=case.attrib["name"]
                status=next((status for status in ("failure","error","skipped")
                             if case.find(status) is not None),"passed")
                cases.append(dict(testId=f"{owner}.{method}",method=method,owner=owner,outcome=status))
        if code==0:
            assert all(x["outcome"]=="passed" for x in cases)
            assert len(cases)==8 and len({x["testId"] for x in cases})==len(cases)
            code=command("selectedCoverage",jdk/"java","-jar",jacoco,"report",data,
                         "--classfiles",product,"--xml",cov)
            if code==0:
                output=ET.parse(cov).getroot()
                assert [s.attrib["id"] for s in output.findall("sessioninfo")]==["PG40816-v2"]
                scope_coverage={c.attrib["type"]:dict(covered=int(c.attrib["covered"]),missed=int(c.attrib["missed"]))
                                for c in output.findall("counter")}
                steps["selectedCoverage"]["xmlSha256"]=sha(cov.read_bytes())
                (run_dir/"coverage.xml").write_bytes(cov.read_bytes())
record=dict(run=run_dir.name,initialAttempt=ctx["run"],startEvent=start["eventId"],source=ctx["source"],core=core,actualExit=code,
            startedAtUTC=start_time,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
            os=platform.platform(),jdk="25.0.4",tools=[ref(p) for p in (agent,jacoco,junit,sdk,fmt,cs,rules,pin_source,*external)],
            sources=[ref(p) for p in [*owned,*test_paths]],compileClassNames=recorded_class_names,steps=steps,cases=cases,
            expectation="TRANSFERCONN001..008, supplied usage/context, owned SimpleMeterRegistry and MockClock; no collectors or exporters.",
            passed=sum(c["outcome"]=="passed" for c in cases),notRun=8-len(cases),
            coverage=scope_coverage,rawProductCoverage=None,coverageMethod="JaCoCo default, nine exact Main types plus package metadata, single selected run.",
            sameSourceCasesReplayed=0,oldSourceTestsRequired=8,oldSourceTestsRequalified=sum(c["outcome"]=="passed" for c in cases),runtimeInfrastructureActions=0,formalDelta=0,wholeC07=False,whole451=False)
out=run_dir/"manifest.json"
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(code,record["passed"],record["notRun"],scope_coverage,sha(out.read_bytes()))
raise SystemExit(code)
