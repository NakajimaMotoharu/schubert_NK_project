"""Own JDK proxy tests of an inspection summary's SQL failure boundary."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib
import json
import os
import subprocess
import sys
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path),sha256=sha(path.read_bytes()))


start_at = datetime.now(timezone.utc).isoformat()
plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
run_start = json.loads(next(plan.glob("1235_*")).read_bytes())
ctx = run_start["values"]
stage = sys.argv[1]
assert stage in {"before","after"}
old_core = ctx["productionCoreMain"]
core = old_core if stage=="before" else sys.argv[2]
fixture = Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/InspectionSummaryPortTest.java")
spec = Path("evidence/01_PT/004_NK-DAT-001/012_InspectionSummary単独SQL例外の単体テスト仕様書.md")
base = "dev/codex/schubert/nk"
batch = Path("src/schubert-nk-batch/src/main/java")/base/"batch/repository"
owned = [batch/f"{name}.java" for name in ("InspectionSummaryRepository","InspectionSummary",
         "BatchRun","CleanupCounts","BatchRepositoryException","JdbcResourceFailures")]
owned.extend([
    Path("src/schubert-nk-bootstrap/src/main/java")/base/"api/bootstrap/JdbcFailureGraph.java",
    Path("src/schubert-nk-storage/src/main/java")/base/"storage/StorageIoException.java",
])
for path in owned:
    assert path.read_bytes() == subprocess.check_output(["git","show",f"{core}:{path}"]),path
test_sources = [fixture] if stage=="before" else [fixture,fixture.with_name("InspectionSummaryGraphContractTest.java")]
if stage=="after":
    assert fixture.read_bytes() == subprocess.check_output(["git","show",f"{core}:{fixture}"])
target_method = "singleSqlFailurePreservesNestedErrorAfterOwnedResourcesClose"
test_dir = Path("evidence/01_PT/018_NK-OPS-001/evidence")
out = test_dir/(ctx["run"] if stage=="before" else "PG40836-p00402-inspection-single-sql-after-v1")
out.mkdir()
tc=Path.cwd().parent/"toolchain"
jdk=tc/"jdk-25.0.4/bin"
sdk=tc/"m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
junit=tc/"junit-platform-console-standalone-1.13.4.jar"
jacoco=tc/"org.jacoco.cli-0.8.15-nodeps.jar"
agent=tc/"m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
formatter=tc/"google-java-format-1.36.1-all-deps.jar"
checkstyle=tc/"static-gates-20261015/checkstyle-14.3.0-all.jar"
rules=Path("tools/quality/static/checkstyle.xml")
tests = []
steps = {}
cov_summary = None
code = 1
xml_sha = None
expect = 1 if stage=="before" else 12
ns = "dev.codex.schubert.nk.batch.repository"
selectors = ("--select-method",f"{ns}.InspectionSummaryPortTest#{target_method}") if stage=="before" else tuple(
    token for p in test_sources for token in ("--select-class",f"{ns}.{p.stem}"))
env = {"PATH":os.defpath,"LANG":"C.UTF-8","TZ":"Asia/Tokyo"}


def command(name,*args):
    argv = list(map(str,args))
    cp=subprocess.run(argv,capture_output=True,timeout=55,env=env)
    steps[name]=dict(command=argv,exitCode=cp.returncode,outputSha256=sha(cp.stdout),errorSha256=sha(cp.stderr))
    if cp.returncode and name!="test":
        print(name,cp.returncode,cp.stderr.decode(errors="replace")[:500])
    return cp.returncode


with tempfile.TemporaryDirectory(prefix="pg4083-inspection-",dir="/dev/shm") as td:
    scratch=Path(td)
    product=scratch/"product"
    unit=scratch/"unit"
    style_files=[owned[0],fixture]
    if (command("format",jdk/"java","-jar",formatter,"--skip-reflowing-long-strings","--dry-run",
                "--set-exit-if-changed",*style_files)==0
        and command("checkstyle",jdk/"java","-jar",checkstyle,"-c",rules,*style_files)==0
        and command("compileMain",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
                    "-cp",sdk,"-d",product,*owned)==0
        and command("compileTest",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
                    "-cp",f"{product}:{sdk}:{junit}","-d",unit,*test_sources)==0):
        reldir=scratch/"test-report"
        data=scratch/"unit.exec"
        agent_arg=f"-javaagent:{agent}=destfile={data},append=false,sessionid={out.name}"
        code=command("test",jdk/"java",agent_arg,"-jar",junit,"execute","--disable-banner",
                     "--disable-ansi-colors","--class-path",f"{product}:{unit}:{sdk}",
                     *selectors,"--reports-dir",reldir,"--fail-if-no-tests")
        report=reldir/"TEST-junit-jupiter.xml"
        if report.is_file():
            xml_sha=sha(report.read_bytes())
            for elem in ET.parse(report).getroot().findall("testcase"):
                outcome="passed"
                failed=elem.find("failure")
                if failed is not None:
                    outcome="failed"
                elif elem.find("error") is not None:
                    outcome="error"
                elif elem.find("skipped") is not None:
                    outcome="skipped"
                method=elem.attrib["name"].removesuffix("()")
                test_id="INSPPORT011" if method==target_method else elem.attrib["classname"]+"."+method
                record=dict(testId=test_id,method=method,outcome=outcome)
                if failed is not None and method==target_method:
                    text="".join(failed.itertext())
                    record["mismatchTextOccurrences"]=text.count("but was: <dev.codex.schubert.nk.batch.repository.BatchRepositoryException>")
                    record["fixedDiagnosisReplacedFatal"]="batch repository operation failed" in text
                tests.append(record)
        if code==0 and stage=="after" and len(tests)==expect and all(t["outcome"]=="passed" for t in tests):
            cov=scratch/"coverage.xml"
            code=command("coverage",jdk/"java","-jar",jacoco,"report",data,"--classfiles",product,"--xml",cov)
            if code==0:
                tree=ET.parse(cov).getroot()
                assert [s.attrib["id"] for s in tree.findall("sessioninfo")]==[out.name]
                source=next(p for p in tree.findall(".//sourcefile") if p.attrib["name"]=="InspectionSummaryRepository.java")
                cov_summary={elem.attrib["type"]:{key:int(elem.attrib[key]) for key in ("covered","missed")}
                             for elem in source.findall("counter")}
                (out/"coverage.xml").write_bytes(cov.read_bytes())
counts=dict(Counter(test["outcome"] for test in tests))
manifest=dict(run=out.name,stage=stage,currentCore=core,priorCore=old_core,startEvent=run_start["eventId"],
    actualExit=code,expectedMethods=expect,cases=tests,counts=counts,notRun=expect-len(tests),steps=steps,
    sourceInputs=[pin(p) for p in [*owned,*test_sources]],spec=pin(spec),testXmlSha256=xml_sha,
    relatedBug="BUG-3416",relatedYkt="YKT-2359",localDefaultCoverage=cov_summary,realDatabaseRead=0,
    originalSourceTestReplay=0,whole451=False,formalDelta=0,startedAtUTC=start_at,
    terminalAtUTC=datetime.now(timezone.utc).isoformat())
path=out/"manifest.json"
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(code,counts,manifest["notRun"],cov_summary, pin(path)["sha256"])
raise SystemExit(code)
