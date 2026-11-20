"""Bind the current Range parser to the existing in-memory media response contract."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


h = runpy.run_path(str(Path(__file__).with_name("5618_f03_seven_local_tests_typed.py")))
BIN, OPS, WEB, DOMAIN, check, pin, read = (
    h[key] for key in ("BIN","OPS","WEB","DOMAIN","check","pin","read")
)
DIR = Path(DOMAIN)/"media"
TEST = WEB/"test/java"/DIR/"MediaRangePortTest.java"
TEST_OWNER = (DIR/"MediaRangePortTest").as_posix().replace("/",".")
MAIN_OWNERS = ("HttpByteRangeParser","MediaRangeService","MediaBodyStreamer",
               "MediaDeliveryException","ContentDispositionFactory")
RUN = "PG41250-media-current-range-response-port-v1"
NEW_case = "invalidUnitAndOverLimitEndDoNotRequestOrReadABody()"


def main():
    group, = Path("documents/400_PGPT/470_PMO").glob("601_*/1664_*.json")
    start = read(group)["values"]
    for ref in start["oracleReferences"][:-1]:
        assert pin(Path(ref["path"])) == ref
    old_input = start["oracleReferences"][-1]
    old_test = subprocess.check_output(["git","show",f'{start["source"]}:{TEST}'],timeout=12)
    assert sha256(old_test).hexdigest() == old_input["sha256"] != pin(TEST)["sha256"]
    paths = [Path(row["path"]) for row in start["oracleReferences"]]
    design = subprocess.check_output(["git","show",f'{start["canonicalDesignSource"]}:{paths[1]}'],timeout=12)
    assert "（SSC-476）。" in design.decode() and "416" in design.decode()
    prev, range_proof, decimal = [read(path) for path in paths[2:5]]
    assert prev["actualExit"] == range_proof["actualExit"] == decimal["actualExit"] == 0
    assert prev["productionCore"] != start["productionCoreMain"] == decimal["productionCore"]
    ma = [WEB/"main/java"/DIR/(name+".java") for name in MAIN_OWNERS]
    for path in ma:
        current = subprocess.check_output(["git","show",f'{start["productionCoreMain"]}:{path}'],timeout=12)
        earlier = subprocess.check_output(["git","show",f'{prev["productionCore"]}:{path}'],timeout=12)
        assert current == path.read_bytes() and (current != earlier) == (path.name == "HttpByteRangeParser.java")
    syntax = Path("../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar")
    format_jar = Path("../toolchain/google-java-format-1.36.1-all-deps.jar")
    tools = {}
    tools["format"], fmt = check([BIN/"java","-jar",format_jar,"--dry-run","--set-exit-if-changed",TEST])
    tools["checkstyle"], cs = check([BIN/"java","-jar",syntax,"-c","tools/quality/static/checkstyle.xml",
                                    "-f","xml",TEST])
    assert fmt.returncode==cs.returncode==0 and not ET.fromstring(cs.stdout).findall(".//error")
    deps = [Path(row["path"]) for row in prev["admittedDependencies"] if Path(row["path"]).name in {
        "current-protocol176.jar","jspecify-1.0.1.jar","junit-platform-console-standalone-1.13.4.jar"
    }]
    assert len(deps)==3 and all(pin(dep) in prev["admittedDependencies"] for dep in deps)
    for dep in deps:
        with ZipFile(dep) as archive:
            assert not any(Path(entry).stem.split("$")[0] in h["CLOSED_NAMES"] for entry in archive.namelist())
    agent=Path(range_proof["agent"]["path"])
    assert pin(agent)==range_proof["agent"]
    local=(Path("../pgpt-runs/PG379")/RUN).resolve()
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-range-service-current-") as temp:
        scratch=Path(temp)
        prod,test=scratch/"main",scratch/"test"
        prod.mkdir()
        test.mkdir()
        cp=os.pathsep.join(map(str,deps))
        compiler=[BIN/"javac","--release","25","-g","-Xlint:all","-Werror","-proc:none"]
        tools["compileMain"], a=check([*compiler,"-cp",cp,"-d",prod,*ma])
        tools["compileTest"], b=check([*compiler,"-cp",f"{prod}{os.pathsep}{cp}","-d",test,TEST])
        assert a.returncode==b.returncode==0,(a.stderr,b.stderr)
        current={str(p.relative_to(prod)):pin(p)["sha256"] for p in prod.rglob("*.class")}
        expected=dict((n,prev["scopedMainPhysical"][n]) for n in current)
        assert len(current)==13
        parser_as_tested={Path(row["path"]).name:row["sha256"] for row in range_proof["physical"]}
        for name,digest in current.items():
            if Path(name).name.startswith("HttpByteRangeParser"):
                assert digest==parser_as_tested[Path(name).name]
            else:
                assert digest==expected[name]
        spots=sorted(test.rglob("*.class"))
        assert len(spots)==8
        original_static=Path(prev["staticReference"]["path"])
        sb=read(original_static)["stagedStatic"]["spotbugs"]["command"][:13]
        sb[10]=f"{prod}{os.pathsep}{cp}"
        report=scratch/"spotbugs.xml"
        sb[12]=report
        tools["spotbugs"], detected=check([*sb,*spots])
        findings=ET.parse(report).getroot()
        local.mkdir()
        safe_report=local/"spotbugs.xml"
        safe_report.write_bytes(report.read_bytes())
        assert detected.returncode==0 and not any(findings.findall(q) for q in
                                                   ("BugInstance",".//MissingClass",".//Error"))
        xml, original=local/"xml",local/"unit.exec"
        tools["junit"], run=check([BIN/"java","-Dfile.encoding=UTF-8",
            f"-javaagent:{agent}=destfile={original},append=false,sessionid={RUN}",
            "-cp",f"{test}{os.pathsep}{prod}{os.pathsep}{cp}","org.junit.platform.console.ConsoleLauncher",
            "execute","--disable-banner","--details=summary","--fail-if-no-tests",
            "--reports-dir",xml,"--select-class",TEST_OWNER])
        terminal=local/"terminal.json"
        terminal.write_text(json.dumps(tools["junit"],indent=2)+"\n")
        unit=xml/"TEST-junit-jupiter.xml"
        root=ET.parse(unit).getroot()
        assert tuple(root.get(k) for k in ("tests","failures","errors","skipped"))==("12","0","0","0")
        cases=root.findall("testcase")
        assert run.returncode==0 and all(h["H"]["successful_case"](c) and c.get("classname")==TEST_OWNER for c in cases)
        originals=prev["productTestRequalification"]
        expect={originals["fixtureCase"],*originals["productCases"],NEW_case}
        assert len(expect)==12 and set(c.get("name") for c in cases)==expect
        owner_names={f"{DIR.as_posix()}/{name}" for name in ("HttpByteRangeParser","MediaRangeService")}
        decoded=runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](
            original.read_bytes(),owner_names)["classes"]
        crc=runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))["class_id"]
        for name, entry in decoded.items():
            assert int(entry["crc64"],16)==crc((prod/(name+".class")).read_bytes())
        sealed=local/"physical"
        sealed.mkdir()
        for name in current:
            content=prod/name
            (sealed/content.name).write_bytes(content.read_bytes())
    out=OPS/RUN
    out.mkdir()
    for name,path in (("unit.exec",original),("jupiter.xml",unit),("spotbugs.xml",safe_report)):
        (out/name).write_bytes(path.read_bytes())
    d=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
           source=start["productionCoreMain"],testId="PT-MED-PORT011",testInput=pin(TEST),
           stages=tools,originalArtifacts=list(map(pin,(terminal,original,unit,safe_report))),
           coverageClassFiles=list(map(pin,sorted(sealed.iterdir()))),inputSources=list(map(pin,ma)),
           actualProductTests=11,newProductCases=1,requiredOlderCases=10,fixtureCanaries=1,
           failed=0,skipped=0,errors=0,notRun=0,
           originalProbeRecords=decoded,channelMetadataOpens=2,
           bodyRequestsInNewCase=0,fileBytesReadInNewCase=0,physicalFileOrHttpOps=0,formalDelta=0)
    result=out/"manifest.json"
    with result.open("x") as f:
        json.dump(d,f,indent=2)
        f.write("\n")
    print(pin(result),len(cases),len(decoded))


if __name__=="__main__":
    main()
