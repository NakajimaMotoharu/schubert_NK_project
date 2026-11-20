"""Measure all admitted media parser/value/port tests from one current execution."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


h=runpy.run_path(str(Path(__file__).with_name("5639_current_media_range_error_response.py")))
BIN, OPS, WEB, DIR, MAIN_OWNERS, pin, read, check=(
    h[key] for key in ("BIN","OPS","WEB","DIR","MAIN_OWNERS","pin","read","check")
)
RUN="PG41256-media-current-five-types-single-exec-v1"
FIXED_RUN="PG41260-media-current-five-types-corrected-v1"
METHOD_COUNTS={
    "HttpByteRangeParserTest":4,
    "HttpByteRangeNamespaceContractTest":1,
    "HttpByteRangeLongBoundaryTest":1,
    "HttpByteRangeUnitTokenTest":2,
    "HttpByteRangeDecimalLimitTest":1,
    "MediaRangePortTest":12,
    "MediaBodyStreamerTest":2,
    "MediaBodyStreamerNamespaceContractTest":1,
    "ContentDispositionFactoryTest":1,
    "ContentDispositionNamespaceContractTest":1,
    "ExceptionValueContractTest":1,
}


def main(fixed):
    code="1673" if fixed else "1670"
    run_name=FIXED_RUN if fixed else RUN
    counts=dict(METHOD_COUNTS)
    if fixed:
        counts["ExceptionValueContractTest"]=2
    start,=Path("documents/400_PGPT/470_PMO").glob(f"601_*/{code}_*.json")
    plan=read(start)["values"]
    for row in plan["oracleReferences"]:
        assert pin(Path(row["path"]))==row
    refs=[Path(row["path"]) for row in plan["oracleReferences"]]
    assert len(refs)==(8 if fixed else 6)
    parser, port, post, copy=[read(p) for p in refs[2:6]]
    assert all(record["actualExit"]==0 for record in (parser,port,post,copy))
    assert parser["productionCore"]==port["source"]==post["source"]==plan["productionCoreMain"]
    assert copy["fixtureTempEmptyAfter"] and copy["syntheticFilesystemIoInvoked"]
    assert copy["actualDbRootNativeVmKeySignerPermitPlacementActions"]==0
    sdk,=OPS.glob("PG41200-*/manifest.json")
    dependencies=[Path(item["path"]) for item in read(sdk)["admittedDependencies"] if Path(item["path"]).name in {
        "junit-platform-console-standalone-1.13.4.jar","current-protocol176.jar","jspecify-1.0.1.jar"
    }]
    assert len(dependencies)==3 and all(pin(p) in read(sdk)["admittedDependencies"] for p in dependencies)
    allowed=h["h"]["CLOSED_NAMES"]
    for dep in dependencies:
        with ZipFile(dep) as jar:
            assert not any(Path(name).stem.split("$")[0] in allowed for name in jar.namelist())
    mains=[WEB/"main/java"/DIR/(name+".java") for name in MAIN_OWNERS]
    tests=[WEB/"test/java"/DIR/(name+".java") for name in METHOD_COUNTS]
    tested=plan["source"]
    core=plan["productionCoreMain"]
    if fixed:
        tested=subprocess.check_output(["git","rev-parse","HEAD"],text=True,timeout=10).strip()
        changed=subprocess.check_output(["git","diff","--name-only",plan["source"],tested,"--","src"],
                                        text=True,timeout=10).splitlines()
        service=str(WEB/"main/java"/DIR/"MediaRangeService.java")
        exception=str(WEB/"test/java"/DIR/"ExceptionValueContractTest.java")
        assert set(changed)=={service,exception}
        core=tested
    for path in [*mains,*tests]:
        revision=core if path in mains else tested
        current=subprocess.check_output(["git","show",f"{revision}:{path}"],timeout=10)
        assert current==path.read_bytes()
        typed = current.replace(b"import java.net.URLEncoder;",b"") if path.name=="ContentDispositionFactory.java" else current
        assert not any(word in typed for word in (b"LinuxDirectoryCalls",b"OwnedTransferDirectory",
            b"DriverManager",b"ProcessBuilder",b"java.net.",b"System.loadLibrary"))
        if path.name!="MediaBodyStreamerTest.java":
            assert b"java.nio.file" not in current and b"@TempDir" not in current
    for path in tests:
        assert len(re.findall(r"(?m)^[ \t]*@Test[ \t]*$",path.read_text()))==counts[path.stem]
    assert sum(counts.values())==(28 if fixed else 27)
    agent=Path(parser["agent"]["path"])
    assert pin(agent)==parser["agent"]
    saved=Path("../pgpt-runs/PG379").resolve()/run_name
    tools={}
    if fixed:
        edited=[Path(service),Path(exception)]
        formatter=Path("../toolchain/google-java-format-1.36.1-all-deps.jar")
        style=Path("../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar")
        tools["format"],fmt=check([BIN/"java","-jar",formatter,"--dry-run","--set-exit-if-changed",*edited])
        tools["style"],cs=check([BIN/"java","-jar",style,"-c","tools/quality/static/checkstyle.xml",
                                 "-f","xml",*edited])
        assert fmt.returncode==cs.returncode==0 and not ET.fromstring(cs.stdout).findall(".//error")
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-five-media-") as temp:
        slot=Path(temp)
        main_dir,test_dir,owned=(slot/name for name in ("main","test","owned-temp"))
        for dest in (main_dir,test_dir,owned):
            dest.mkdir()
        sdk_cp=os.pathsep.join(map(str,dependencies))
        compile_args=[BIN/"javac","--release","25","-g","-Xlint:all","-Werror","-proc:none"]
        tools["main"],a=check([*compile_args,"-cp",sdk_cp,"-d",main_dir,*mains])
        tools["tests"],b=check([*compile_args,"-cp",f"{main_dir}{os.pathsep}{sdk_cp}",
                               "-d",test_dir,*tests])
        assert a.returncode==b.returncode==0,(a.stderr,b.stderr)
        candidate=sorted(main_dir.rglob("*.class"))
        archived={Path(row["path"]).name:row["sha256"] for row in port["coverageClassFiles"]}
        assert len(candidate)==len(archived)==13
        assert all((pin(p)["sha256"]!=archived[p.name])==(fixed and p.name=="MediaRangeService.class")
                   for p in candidate)
        saved.mkdir()
        physical=saved/"physical"
        physical.mkdir()
        for p in candidate:
            (physical/p.name).write_bytes(p.read_bytes())
        original,report=saved/"media.exec",saved/"xml"
        selectors=[argument for n in METHOD_COUNTS
                   for argument in ("--select-class",DIR.as_posix().replace("/",".")+"."+n)]
        tools["junit"],u=check([BIN/"java","-Dfile.encoding=UTF-8",f"-Djava.io.tmpdir={owned}",
            f"-javaagent:{agent}=destfile={original},append=false,sessionid={run_name}",
            "-cp",os.pathsep.join(map(str,(test_dir, main_dir, sdk_cp))),
            "org.junit.platform.console.ConsoleLauncher","execute","--disable-banner","--details=summary",
            "--fail-if-no-tests","--reports-dir",report,*selectors])
        terminal=saved/"junit-terminal.json"
        terminal.write_text(json.dumps(tools["junit"],indent=2)+"\n")
        raw_xml=report/"TEST-junit-jupiter.xml"
        doc=ET.parse(raw_xml).getroot()
        cases={}
        for entry in doc.findall("testcase"):
            assert h["h"]["H"]["successful_case"](entry)
            name=entry.get("classname").split(".")[-1]
            cases.setdefault(name,[]).append(entry.get("name"))
        assert {k:len(v) for k,v in cases.items()}==counts
        assert u.returncode==0 and [doc.get(k) for k in ("tests","failures","errors","skipped")]==[
            str(sum(counts.values())),"0","0","0"]
        assert not list(owned.iterdir())
    out=OPS/run_name
    out.mkdir()
    for name,path in (("media.exec",original),("jupiter.xml",raw_xml)):
        (out/name).write_bytes(path.read_bytes())
    proof=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
               source=tested,productionCore=core,run=run_name,
               priorPG41250=pin(refs[3]),previousCopyAdmission=pin(refs[5]),
               inputMain=list(map(pin,mains)),inputTests=list(map(pin,tests)),sdk=list(map(pin,dependencies)),
               commands=tools,original=list(map(pin,(original,raw_xml,terminal))),
               admittedPhysical=list(map(pin,sorted(physical.iterdir()))),scopeCounts=counts,caseNames=cases,
               tests=sum(counts.values()),newTests=int(fixed),productRequalifications=26,fixtureCanary=1,
               fail=0,error=0,skip=0,notRun=0,tempOwnedEmptyAfter=True,
               inheritedNativeSuiteExcludedWithHold="MediaRangeServiceTest",
               actualServicesOrNative=0,noOldExecUnion=True,formalDelta=0)
    dst=out/"manifest.json"
    with dst.open("x") as stream:
        json.dump(proof,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(pin(dst),len(cases),sum(counts.values()))


if __name__=="__main__":
    assert sys.argv[1:] in ([],["--fixed"])
    main(bool(sys.argv[1:]))
