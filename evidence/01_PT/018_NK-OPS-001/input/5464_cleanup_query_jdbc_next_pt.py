"""Execute the admitted cleanup query fixture with a single nested SQL case."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path),sha256=digest(path.read_bytes()))


plan=next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start=json.loads(next(plan.glob("1278_*")).read_bytes())
core=start["values"]["productionCoreMain"]
namespace="dev/codex/schubert/nk"
folder=Path("src/schubert-nk-batch/src/main/java")/namespace/"batch/repository"
names=("CleanupRepository","CleanupChunk","CleanupKind","CleanupCounts","BatchRun","BatchStep","CleanupReason",
       "LogCleanupProgress","BatchRepositoryException","JdbcResourceFailures")
main=[folder/(name+".java") for name in names]
main.extend([Path("src/schubert-nk-bootstrap/src/main/java")/namespace/"api/bootstrap/JdbcFailureGraph.java",
             Path("src/schubert-nk-storage/src/main/java")/namespace/"storage/StorageIoException.java"])
assert all(path.read_bytes()==subprocess.check_output(["git","show",f"{core}:{path}"]) for path in main)
fixture=Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/CleanupQueryPortTest.java")
spec=Path("evidence/01_PT/017_NK-BAT-001/4746_CleanupQuery_SQL次辺・資源所有の単体仕様.md")
tc=Path.cwd().parent/"toolchain"
rep=tc/"m2/repository"
jdk=tc/"jdk-25.0.4/bin"
sdk=[rep/"org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar",rep/"com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"]
junit=tc/"junit-platform-console-standalone-1.13.4.jar"
formatter=tc/"google-java-format-1.36.1-all-deps.jar"
style=tc/"static-gates-20261015/checkstyle-14.3.0-all.jar"
rules=Path("tools/quality/static/checkstyle.xml")
started=datetime.now(timezone.utc).isoformat()
steps={}
evidence=Path("evidence/01_PT/018_NK-OPS-001/evidence")
preparation_failure=evidence/start["values"]["run"]/"manifest.json"
prior=json.loads(preparation_failure.read_bytes())
assert prior["steps"]["compile"]["exit"]==1 and not prior["caseResults"]
out=evidence/"PG40868-cleanup-query-jdbc-next-owner-v1"
out.mkdir()


def run(name,*args):
    cmd=list(map(str,args))
    r=subprocess.run(cmd,capture_output=True,timeout=45)
    steps[name]=dict(command=cmd,exit=r.returncode,stdoutSha256=digest(r.stdout),stderrSha256=digest(r.stderr))
    if r.returncode and name!="test":
        print(name,r.stderr.decode(errors="replace")[:1000])
    return r.returncode


cases=[]
xml_hash=None
with tempfile.TemporaryDirectory(prefix="pg40866-",dir="/dev/shm") as folder:
    dest=Path(folder)/"classes"
    report=Path(folder)/"reports"
    report.mkdir()
    cp=":".join(str(p) for p in sdk)
    code=run("format",jdk/"java","-jar",formatter,"--skip-reflowing-long-strings","--dry-run","--set-exit-if-changed",fixture)
    if code==0:
        code=run("checkstyle",jdk/"java","-jar",style,"-c",rules,fixture)
    if code==0:
        code=run("compile",jdk/"javac","--release",25,"-g","-Werror","-Xlint:all","-proc:none",
                 "-cp",f"{cp}:{junit}","-d",dest,*main,fixture)
    if code==0:
        assert not any(p.name=="BatchRunRepository.class" for p in dest.rglob("*.class"))
        method="nestedSqlNextErrorPreservesIdentityAtBothResourceBoundaries"
        code=run("test",jdk/"java","-jar",junit,"execute","--disable-ansi-colors","--disable-banner",
           "--class-path",f"{dest}:{cp}","--select-method",
           "dev.codex.schubert.nk.batch.repository.CleanupQueryPortTest#"+method,
           "--reports-dir",report,"--fail-if-no-tests")
        xml=report/"TEST-junit-jupiter.xml"
        if xml.is_file():
            xml_hash=digest(xml.read_bytes())
            for c in ET.parse(xml).getroot().findall("testcase"):
                assert c.attrib["name"].removesuffix("()")==method
                result=next((s for s in ("failure","error","skipped") if c.find(s) is not None),"passed")
                cases.append(dict(testId="CLNQUERY010",method=method,outcome=result))
        if code==0:
            assert len(cases)==1 and cases[0]["outcome"]=="passed"
output=dict(actualExit=code,core=core,startEvent=start["eventId"],startedAtUTC=started,
    terminalAtUTC=datetime.now(timezone.utc).isoformat(),tools=[pin(p) for p in [*sdk,junit,style,formatter,rules]],
    sourceClosure=[pin(p) for p in main],fixture=pin(fixture),spec=pin(spec),steps=steps,caseResults=cases,
    trialMatrixSize=4,oldTestsRerun=0,testXmlSha256=xml_hash,realDatabaseActions=0,whole451=False,coverage=None,
    formalDelta=0,priorPreparationFailure=pin(preparation_failure),
    preparationCorrection="BatchStep is a direct CleanupKind dependency from the admitted closure.")
manifest=out/"manifest.json"
manifest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
print(code,cases,pin(manifest))
raise SystemExit(code)
