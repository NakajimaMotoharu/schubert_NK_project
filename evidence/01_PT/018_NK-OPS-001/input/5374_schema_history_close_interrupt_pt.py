"""Exercise the two added interruption checks with owned in-memory JDBC proxies."""

from collections import Counter
import gzip
import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile


U = runpy.run_path(str(Path(__file__).with_name("5362_migration_utc42_current_unit.py")))
H, OPS, PLAN, JAVA = (U[n] for n in ("H","OPS","PLAN","JAVA"))
WORKTREE = Path.cwd()
MODULE = Path("src/schubert-nk-bootstrap/src")
PK = "dev/codex/schubert/nk/api/bootstrap/"
TEST_PK = "dev/codex/schubert/nk/api/maintenance/"
CLS = "SchemaHistoryAdmission"
TEST = CLS + "Test"
ROW_TEST = "SchemaHistoryRowValueTest"
RED_SOURCE = "d95b02236ffaec2e847e1fd773fdd279d921762a"
CANONICAL = "63c4a673bc98464a5bb8e9dae85eba3ce9ef0d2a"
NEW = ("opsSchema012InterruptWhileClosingRowsRejectsObservedHistory",
       "opsSchema013InterruptWhileClosingStatementRejectsObservedHistory")
PRODUCTION = MODULE / "main/java" / PK / (CLS+".java")
TARGETS = {PK + CLS + suffix for suffix in (".class","$Row.class")}
BOOTSTRAP = TARGETS | {PK+name+".class" for name in ("JdbcAdmissionFailures","JdbcFailureGraph")}
STORAGE = {"dev/codex/schubert/nk/storage/"+n+".class"
           for n in ("StorageIoException","StorageIoException$Reason","package-info")}


def main(attempt, candidate):
    red = attempt == "red"
    read=U["read"]
    pin, git, sha, execute = (H[k] for k in ("pin","git","sha","execute"))
    work=read(next(PLAN.glob("893_*")))["values"]
    baseline = work["productionCoreMain"]
    refs=work["oracleReferences"]
    prior=read(refs[2]["path"])
    package=read(refs[3]["path"])
    assert pin(Path(refs[2]["path"]))==refs[2] and pin(Path(refs[3]["path"]))==refs[3]
    assert prior["actualExit"]==0 and prior["tests"]==11 and prior["scopePhysical"]==7
    assert package["sourceCore"]==baseline
    assert git("rev-parse","origin/main").decode().strip()==CANONICAL
    source=RED_SOURCE if red else candidate
    path="PG40492-schema-history-two-close-interrupt-red-v1" if red else "PG40494-schema-history-close-interrupt-green13-v1"
    baseline_assert=git("show", f"{baseline}:{PRODUCTION}")
    now=git("show", f"{source}:{PRODUCTION}")
    assert (baseline_assert==now) if red else (baseline_assert!=now)
    if not red:
        paths=git("diff","--name-only",RED_SOURCE,source,"--","src").decode().splitlines()
        assert paths==[str(PRODUCTION)]
    env=read(next(OPS.glob("PG40128-*/begin.json")))
    assert pin(JAVA)==env["jdk"]
    jars={k:Path(v["path"]) for k,v in env["tools"].items() if k in (
        "junit-platform-console-standalone-1.13.4.jar","org.jacoco.agent-0.8.15-runtime.jar",
        "org.jacoco.cli-0.8.15-nodeps.jar","jspecify-1.0.1.jar")}
    assert all(pin(v)==env["tools"][k] for k,v in jars.items())
    junit,agent,cli,jspec=list(jars.values())
    assert junit.name.startswith("junit") and "agent" in agent.name and "cli" in cli.name and "jspecify" in jspec.name
    meta=read(next(OPS.glob("PG33674-*/manifest.json")))
    jsr,=[Path(n) for n in meta["dependencies"] if Path(n).name.startswith("jsr305")]
    assert pin(jsr)["sha256"]==meta["dependencies"][str(jsr)]
    test_names = tuple(TEST_PK.replace("/",".")+n for n in (TEST,ROW_TEST))
    counts,stages,physical,inputs={},{},{},{}
    out=OPS/path
    out.mkdir()
    xml=out/"xml"
    xml.mkdir()
    exec_data=out/"jacoco.exec"
    compiler=[JAVA.with_name("javac"),"--release","25","-g","-Xlint:all","-Werror","-proc:none"]
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-schema-close-proxy-") as parent:
        root=Path(parent)
        classes,tests=root/"classes",root/"testclasses"
        for module,names in (("bootstrap",BOOTSTRAP),("storage",STORAGE)):
            jar=package["packagedJars"][module]["artifact"]
            assert pin(Path(jar["path"]))==jar
            with ZipFile(jar["path"]) as archive:
                for name in sorted(names):
                    member=classes/name
                    member.parent.mkdir(exist_ok=True,parents=True)
                    member.write_bytes(archive.read(name))
        sources=[]
        for name in (TEST,ROW_TEST):
            official=MODULE/"test/java"/TEST_PK/(name+".java")
            copied=root/official
            copied.parent.mkdir(exist_ok=True,parents=True)
            data=git("show",f"{source}:{official}")
            copied.write_bytes(data)
            inputs[str(official)]=sha(data)
            sources.append(copied)
        cp=os.pathsep.join(map(str,(classes,jspec,jsr)))
        if not red:
            main_file=root/PRODUCTION
            main_file.parent.mkdir(exist_ok=True,parents=True)
            main_file.write_bytes(now)
            stages["main"],_=execute(out,"main",[*compiler,"-cp",cp,"-d",classes,main_file],root)
            assert stages["main"]["actualExit"]==0
        physical={p.relative_to(classes).as_posix():pin(p)["sha256"] for p in classes.rglob("*.class")}
        assert set(physical)==BOOTSTRAP|STORAGE
        stages["tests"],_=execute(out,"tests",[*compiler,"-cp",cp+os.pathsep+str(junit),"-d",tests,*sources],root)
        assert stages["tests"]["actualExit"]==0
        selections=([f"--select-method={test_names[0]}#{name}" for name in NEW] if red else
                    [f"--select-class={name}" for name in test_names])
        trace=root/"class-init.log"
        command=[JAVA,f"-Xlog:class+init=info:file={trace}",f"-javaagent:{agent}=destfile={exec_data.resolve()},sessionid={path},append=false",
            "-jar",junit,"execute","--disable-banner","--fail-if-no-tests","--details=summary",
            "--class-path",str(tests)+os.pathsep+cp,"--reports-dir",xml.resolve(),*selections]
        stages["unit"],_=execute(out,"unit",command,root)
        U["pack_text"](out,stages["unit"])
        arrival=ElementTree.parse(xml/"TEST-junit-jupiter.xml").getroot()
        numbers=["tests","failures","errors","skipped"]
        counts={key:int(arrival.get(key)) for key in numbers}
        loaded=trace.read_bytes()
        assert all(token not in loaded for token in (b"FingerprintKeyRing",b"ResponseSnapshotCodec",
                                                     b"WebStartupException",b"TemporaryInfrastructureException"))
        (out/"class-init.log.gz").write_bytes(gzip.compress(loaded,mtime=0))
        names={node.get("name") for node in arrival.findall("testcase")}
        assert {item+"()" for item in NEW}<=names
        if not red and stages["unit"]["actualExit"]==0:
            stages["standard"],_=execute(out,"standard",[JAVA,"-jar",cli,"report",exec_data.resolve(),
                "--classfiles",classes,"--xml",(out/"coverage.xml").resolve()],root)
            raw=read(next(OPS.glob("PG40452-*/manifest.json")))["stages"]["raw"]["command"]
            stages["raw"],_=execute(out,"raw",[*raw[:5],exec_data.resolve(),*(classes/name for name in sorted(TARGETS))],root)
    needed = ({"tests":2,"failures":2,"errors":0,"skipped":0} if red else
              {"tests":13,"failures":0,"errors":0,"skipped":0})
    okay=counts==needed and stages["unit"]["actualExit"]==(1 if red else 0)
    if red:
        failed=arrival.findall(".//failure")
        assert len(failed)==2 and all("nothing was thrown" in case.get("message","") for case in failed)
    status=dict(actualExit=stages["unit"]["actualExit"],expectedDiagnosticOutcome=okay,testSource=source,
        productionCore=baseline if red else source,productionSourceSha256=sha(now),canonicalDesign=CANONICAL,
        testInputs=inputs,physicalClassHashes=physical,counts=counts,ownedSyntheticOnly=True,actualDbConnections=0,
        acceptedPtCount=0 if red or not okay else 13,stages=stages,caseNames=sorted(names),whole451Accepted=False,
        terminalAtUTC=H["timestamp"]())
    H["dump"](out/"manifest.json",status)
    print(pin(out/"manifest.json"),counts,okay)
    return 0 if okay else 1


if __name__=="__main__":
    assert sys.argv[1] in ("red","green")
    raise SystemExit(main(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None))
