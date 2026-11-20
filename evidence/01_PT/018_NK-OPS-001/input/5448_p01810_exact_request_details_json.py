from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os, platform, subprocess, tempfile
from xml.etree import ElementTree as ET

repo = Path.cwd()
tools = repo.parent / "toolchain"
vpath = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1223_*"))
start = json.loads(vpath.read_bytes())
ctx = start["values"]
core = ctx["productionCoreMain"]
start_time = datetime.now(timezone.utc).isoformat()
namespace = "dev/codex/schubert/nk/api/logging"
module = Path("src/schubert-nk-api/src")
main = module / "main/java" / namespace
test_names = ("RequestLogDetailsBoundaryTest",)
test_paths = [module / "test/java" / namespace / f"{name}.java" for name in test_names]
protocol = Path("src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol")
owned = [main/"RequestLogDetails.java", main/"package-info.java",
         protocol/"codec/PermanentProtocolException.java", protocol/"layout/semantic/WireEnum.java",
         protocol/"layout/semantic/UserRole.java"]
def sha(data):
    return hashlib.sha256(data).hexdigest()
def ref(p):
    return {"path":str(p),"sha256":sha(p.read_bytes())}
for p in owned:
    assert p.read_bytes() == subprocess.check_output(["git","show",f"{core}:{p}"])
assert len(owned) == 5
assert test_paths == [Path("src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/logging/RequestLogDetailsBoundaryTest.java")]

jdk = tools / "jdk-25.0.4/bin"
sdk = tools / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
gson = tools / "m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar"
assert sha(gson.read_bytes()) == "2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f"
sdk_classpath = f"{sdk}:{gson}"
test_ids = {
    "decodedPropertyIdentityControlsDuplicatesAndRoleOwnership": "PT-IDEM-012-JSON-001",
    "numericZeroRequiresAnUnsignedDecimalIntegerSpelling": "PT-IDEM-012-JSON-002",
}
junit = tools / "junit-platform-console-standalone-1.13.4.jar"
agent = tools / "m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
jacoco = tools / "org.jacoco.cli-0.8.15-nodeps.jar"
fmt = tools / "google-java-format-1.36.1-all-deps.jar"
cs = tools / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml")
run_dir = Path("evidence/01_PT/018_NK-OPS-001/evidence") / "PG40826-p01810-exact-request-details-json-v2"
run_dir.mkdir()
steps, cases, scope_coverage = {}, [], None
recorded_class_names = []
code = 1
suite_prefix = namespace.replace("/", ".")
selectors = [token for name in test_names for token in ("--select-class",f"{suite_prefix}.{name}")]
with tempfile.TemporaryDirectory(prefix="pg40826-", dir="/dev/shm") as temp:
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
        expected_classes = {
            f"{namespace}/RequestLogDetails.class",
            f"{namespace}/package-info.class",
            "dev/codex/schubert/nk/protocol/codec/PermanentProtocolException.class",
            "dev/codex/schubert/nk/protocol/layout/semantic/WireEnum.class",
            "dev/codex/schubert/nk/protocol/layout/semantic/UserRole.class",
        }
        assert set(recorded_class_names) == expected_classes, recorded_class_names
        report_dir = scratch / "test"
        agent_config = f"-javaagent:{agent}=destfile={data},append=false,sessionid=PG40826"
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
                cases.append(dict(testId=test_ids[method.removesuffix("()")],method=method,owner=owner,outcome=status))
        if code==0:
            assert all(x["outcome"]=="passed" for x in cases)
            assert len(cases)==len(test_ids) and set(test_ids.values()) == {x["testId"] for x in cases}
            code=command("selectedCoverage",jdk/"java","-jar",jacoco,"report",data,
                         "--classfiles",product,"--xml",cov)
            if code==0:
                output=ET.parse(cov).getroot()
                assert [s.attrib["id"] for s in output.findall("sessioninfo")]==["PG40826"]
                scope_coverage={c.attrib["type"]:dict(covered=int(c.attrib["covered"]),missed=int(c.attrib["missed"]))
                                for c in output.findall("counter")}
                steps["selectedCoverage"]["xmlSha256"]=sha(cov.read_bytes())
                (run_dir/"coverage.xml").write_bytes(cov.read_bytes())
record=dict(run=run_dir.name,initialAttempt=ctx["run"],startEvent=start["eventId"],source=ctx["source"],core=core,actualExit=code,
            startedAtUTC=start_time,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
            os=platform.platform(),jdk="25.0.4",tools=[ref(p) for p in (agent,jacoco,junit,sdk,gson,fmt,cs,rules)],
            sources=[ref(p) for p in [*owned,*test_paths]],spec=ref(Path('evidence/01_PT/018_NK-OPS-001/4742_REQUEST詳細JSON同一属性と数値境界単体仕様.md')),compileClassNames=recorded_class_names,steps=steps,cases=cases,
            expectation="SS351 section 3.3 literal JSON; canonical identity rejects repeated names and wire role; unsigned decimal permits only zero among the tested spellings.",
            passed=sum(c["outcome"]=="passed" for c in cases),notRun=len(test_ids)-len(cases),
            coverage=scope_coverage,rawProductCoverage=None,coverageMethod="JaCoCo default, four exact Main types plus API package metadata, single selected run.",
            sameSourceCasesReplayed=0,newTestDefinitions=2,previousTestsRun=0,runtimeInfrastructureActions=0,formalDelta=0,wholeC07=False,whole451=False)
out=run_dir/"manifest.json"
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(code,record["passed"],record["notRun"],scope_coverage,sha(out.read_bytes()))
raise SystemExit(code)
