from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os, platform, subprocess, tempfile
from xml.etree import ElementTree as ET

repo = Path.cwd()
tools = repo.parent / "toolchain"
vpath = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1226_*"))
start = json.loads(vpath.read_bytes())
ctx = start["values"]
core = ctx["productionCoreMain"]
start_time = datetime.now(timezone.utc).isoformat()
namespace = "dev/codex/schubert/nk/batch/monitoring"
module = Path("src/schubert-nk-batch/src")
main = module / "main/java" / namespace
test_names = ("AlertLifecycleTest","AlertContinuityTest","AlertWindowedInputContractTest")
test_paths = [module / "test/java" / namespace / f"{name}.java" for name in test_names]
owned = [main / f"{name}.java" for name in (
    "AlertLifecycle", "ObservationContext", "package-info",
)]
def sha(data):
    return hashlib.sha256(data).hexdigest()
def ref(p):
    return {"path":str(p),"sha256":sha(p.read_bytes())}
for p in owned:
    assert p.read_bytes() == subprocess.check_output(["git","show",f"{core}:{p}"])
assert len(owned) == 3
new_fixture = Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/AlertWindowedInputContractTest.java")
spec = Path("evidence/01_PT/018_NK-OPS-001/4743_警報待機観測境界と四指標限定仕様.md")
for p in test_paths:
    if p == new_fixture:
        continue
    assert p.read_bytes() == subprocess.check_output(['git','show',f"{ctx['source']}:{p}"])

jdk = tools / "jdk-25.0.4/bin"
sdk = tools / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
test_ids = {
    "pendingBeforeFirstTriggerDoesNotCreateAnAlert": "PT-TIMED-RECOVERY-011",
    "invalidPendingObservationCannotResetAnExistingRecovery": "PT-TIMED-RECOVERY-012",
    "diagnosticNamesRoundTripThroughTheClosedAlertVocabulary": "PT-TIMED-RECOVERY-013",
}
raw_compile_manifest = next(Path("evidence/01_PT/018_NK-OPS-001/evidence").glob("PG31432-*/compile.json"))
raw_inputs = json.loads(raw_compile_manifest.read_bytes())
raw_cp = ":".join(dep["path"] for dep in raw_inputs["dependencies"])
assert all(sha(Path(dep["path"]).read_bytes()) == dep["sha256"] for dep in raw_inputs["dependencies"])
raw_tool_source = subprocess.check_output(["git","show",
    "c5674055a6:tools/quality/jacoco/UnfilteredCodeMeasurement.java"])
assert sha(raw_tool_source) == raw_inputs["source"]["sha256"]
junit = tools / "junit-platform-console-standalone-1.13.4.jar"
agent = tools / "m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
jacoco = tools / "org.jacoco.cli-0.8.15-nodeps.jar"
fmt = tools / "google-java-format-1.36.1-all-deps.jar"
cs = tools / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml")
run_dir = Path("evidence/01_PT/018_NK-OPS-001/evidence") / ctx["run"]
run_dir.mkdir()
steps, cases, scope_coverage, raw_measurement, local_coverage = {}, [], None, None, None
recorded_class_names = []
code = 1
suite_prefix = namespace.replace("/", ".")
selectors = [token for name in test_names for token in ("--select-class",f"{suite_prefix}.{name}")]
with tempfile.TemporaryDirectory(prefix="pg40828-", dir="/dev/shm") as temp:
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
        if name=="rawMeasurement" and cp.returncode==0:
            (run_dir/"unfiltered.tsv").write_bytes(cp.stdout)
        if cp.returncode:
            print(name,cp.returncode,cp.stderr.decode(errors="replace")[:1300])
        return cp.returncode
    if (command("format",jdk/"java","-jar",fmt,"--skip-reflowing-long-strings","--dry-run",
                "--set-exit-if-changed",*test_paths) == 0
        and command("checkstyle",jdk/"java","-jar",cs,"-c",rules,"-f","xml","-o",xml,*test_paths)==0
        and command("mainCompile",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
                    "-cp",sdk,"-d",product,*owned)==0
        and command("testCompile",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
                    "-cp",f"{product}:{junit}:{sdk}","-d",fixture,*test_paths)==0):
        assert not ET.parse(xml).getroot().findall(".//error")
        recorded_class_names = sorted(str(p.relative_to(product)) for p in product.rglob("*.class"))
        assert all(p.startswith(namespace+"/") and p.count("/")==namespace.count("/")+1
                   for p in recorded_class_names)
        report_dir = scratch / "test"
        agent_config = f"-javaagent:{agent}=destfile={data},append=false,sessionid=PG40828"
        code = command("test",jdk/"java",agent_config,"-jar",junit,"execute","--disable-banner",
                       "--disable-ansi-colors","--class-path",f"{product}:{fixture}:{sdk}",
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
                test_id = test_ids.get(method.removesuffix("()"),f"{owner}.{method}")
                cases.append(dict(testId=test_id,method=method,owner=owner,outcome=status))
        if code==0:
            assert all(x["outcome"]=="passed" for x in cases)
            assert len(cases)==17 and len({x["testId"] for x in cases})==17
            code=command("selectedCoverage",jdk/"java","-jar",jacoco,"report",data,
                         "--classfiles",product,"--xml",cov)
            if code==0:
                output=ET.parse(cov).getroot()
                assert [s.attrib["id"] for s in output.findall("sessioninfo")]==["PG40828"]
                scope_coverage={c.attrib["type"]:dict(covered=int(c.attrib["covered"]),missed=int(c.attrib["missed"]))
                                for c in output.findall("counter")}
                steps["selectedCoverage"]["xmlSha256"]=sha(cov.read_bytes())
                (run_dir/"coverage.xml").write_bytes(cov.read_bytes())
                primary = next(f for f in output.findall(".//sourcefile") if f.attrib["name"] == "AlertLifecycle.java")
                local_coverage={c.attrib["type"]:{k:int(c.attrib[k]) for k in ("covered","missed")}
                                for c in primary.findall("counter")}
                raw_source = scratch/"UnfilteredCodeMeasurement.java"
                raw_source.write_bytes(raw_tool_source)
                raw_classes = scratch/"raw"
                code = command("rawCompile",jdk/"javac","--release",25,"-Xlint:all","-Werror",
                               "-cp",raw_cp,"-d",raw_classes,raw_source)
                if code==0:
                    code=command("rawMeasurement",jdk/"java","-cp",f"{raw_classes}:{raw_cp}",
                                 "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                                 data,*[product/name for name in recorded_class_names])
                if code==0:
                    raw_measurement={"primary":{},"otherClasses":{}}
                    records=(run_dir/"unfiltered.tsv").read_text().splitlines()
                    for line in records:
                        tags=line.split("\t")
                        if tags[0]!="CLASS":
                            continue
                        name=tags[1]
                        category="primary" if name.rsplit("/",1)[1].startswith("AlertLifecycle") else "otherClasses"
                        assert name not in raw_measurement[category] and name+".class" in recorded_class_names
                        raw_measurement[category][name]={"crc64":tags[2],"execDataMatched":tags[3]=="true",
                            "counters":{key:dict(missed=int(miss),covered=int(hit))
                                for key,miss,hit in (part.split(":") for part in tags[6:])}}
                    assert len(raw_measurement["primary"])==6 and len(raw_measurement["otherClasses"])==2
record=dict(run=ctx["run"],startEvent=start["eventId"],source=ctx["source"],core=core,actualExit=code,
            startedAtUTC=start_time,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
            os=platform.platform(),jdk="25.0.4",tools=[ref(p) for p in (agent,jacoco,junit,sdk,fmt,cs,rules)],
            sources=[ref(p) for p in [*owned,*test_paths]],fixtureSpec=ref(spec),rawToolReceipt=ref(raw_compile_manifest),compileClassNames=recorded_class_names,steps=steps,cases=cases,
            expectation="Fixed pending-to-warning times, state-preserving rejection, closed diagnostic vocabulary, plus unchanged lifecycle/continuity oracles in one execution.",
            passed=sum(c["outcome"]=="passed" for c in cases),notRun=17-len(cases),
            coverage=scope_coverage,rawProductCoverage=None,primarySourceDefaultCoverage=local_coverage,selectedRaw=raw_measurement,coverageMethod="JaCoCo default, two exact Main types plus package metadata, single selected run.",
            sameSourceCasesReplayed=0,requiredSameExecPriorPaths=14,newFixtureCases=3,runtimeInfrastructureActions=0,formalDelta=0,wholeC07=False,whole451=False)
out=run_dir/"manifest.json"
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(code,record["passed"],record["notRun"],scope_coverage,sha(out.read_bytes()))
raise SystemExit(code)
