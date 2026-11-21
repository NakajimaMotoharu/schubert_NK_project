"""Verify coverage from the only successful Outbox value run with the approved fixtures."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET

from jacoco_readonly_exec_subset import decode

R=Path.cwd()
OPS=R/"evidence/01_PT/018_NK-OPS-001/evidence"
TC=R.parent/"toolchain"
JDK=TC/"jdk-25.0.4/bin"
UNIT=next(OPS.glob("PG41404*/manifest.json"))
OUT=OPS/"PG41406-outbox-copy-independent-v1"
WORK=R.parent/"pgpt-runs/PG379"/OUT.name

def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())

def get(value):
    p=Path(value["path"])
    assert pin(p)==value
    return p

def crc64(raw):
    numbers=0
    for byte in raw:
        numbers^=byte
        for _ in range(8):
            numbers=(numbers>>1)^0xd800000000000000 if numbers&1 else numbers>>1
    return f"{numbers:016x}"

def main():
    unit=json.loads(UNIT.read_bytes())
    assert unit["actualExit"]==0==unit["errors"]==unit["skipped"]==unit["failures"]==unit["notRun"]
    old=json.loads(get(unit["originalFailure"]).read_bytes())
    assert old["actualExit"]==1 and old["failures"]==2 and unit["originalFailedExecMerged"] is False
    assert not subprocess.check_output(["git","diff","--name-only",unit["source"],"HEAD","--","src","pom.xml"])
    physical=[get(row) for row in unit["productMainClasses"]]
    assert len(physical)==8
    get(unit["originalMainCompile"])
    init_file=get(unit["unitExec"])
    xml_path=get(unit["jupiter"])
    xml=ET.parse(xml_path).getroot()
    assert all(int(xml.get(key,'0'))==0 for key in ("failures","errors","skipped"))
    cases=xml.findall("testcase")
    assert len(cases)==len({(row.attrib["classname"],row.attrib["name"]) for row in cases})==10
    assert Counter(x.attrib["classname"].rsplit(".",1)[-1] for x in cases)=={
        "OutboxModelTest":4,"OutboxDlqMetadataTest":2,"OutboxRetainedValueContractTest":4}
    binary_names={p.as_posix().split('/target/classes/',1)[1].removesuffix('.class'):p for p in physical}
    targets={name for name in binary_names if not name.endswith("/package-info")}
    exact=decode(init_file.read_bytes(),targets)
    assert len(exact["sessions"])==1 and len(exact["classes"])==len(targets)==7
    assert bytes.fromhex(exact["sessions"][0]["labelBytesHex"])==unit["run"].encode("ascii")
    assert all(int(exact["classes"][name]["crc64"],16)==int(crc64(binary_names[name].read_bytes()),16)
               for name in targets)
    for report in unit["originalConstructors"]:
        block=get(report).read_text()
        calls=[line for line in block.splitlines() if "invoke" in line]
        assert "clone:()Ljava/lang/Object;" in calls[-1] and "requireProfile:" in calls[-2]
        assert sum('clone:()Ljava/lang/Object;' in line for line in calls)==1
    pm=ET.parse(get(unit["staticReports"]["pmd"]))
    sb=ET.parse(get(unit["staticReports"]["spotbugs"]))
    assert not pm.findall(".//{*}violation") and not pm.findall(".//{*}error")
    sb_names={x.attrib["class"].replace(".","/") for x in sb.findall(".//ClassStats")}
    assert sb_names==targets or sb_names==set(binary_names)
    assert not any(sb.findall(".//"+n) for n in ("Error","MissingClass","BugInstance"))
    OUT.mkdir()
    WORK.mkdir(mode=0o700)
    jcache=TC/"m2/repository"
    dependencies=[jcache/"org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]
    dependencies.extend(jcache/f"org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar" for n in ("asm","asm-commons","asm-tree"))
    source=R/"tools/quality/jacoco/UnfilteredCodeMeasurement.java"
    cp=os.pathsep.join(map(str,dependencies))
    steps={}
    def execute(name,argv):
        args=list(map(str,argv))
        completed=subprocess.run(args,capture_output=True,timeout=90,check=False)
        out=OUT/(name+".stdout.txt")
        err=OUT/(name+".stderr.txt")
        out.write_bytes(completed.stdout)
        err.write_bytes(completed.stderr)
        steps[name]=dict(actualExit=completed.returncode,command=args,stdout=pin(out),stderr=pin(err))
        assert completed.returncode==0
        return completed.stdout.decode()
    target=WORK/"analyzer"
    inventory=execute("exec-inventory",[JDK/"java","-jar",TC/"org.jacoco.cli-0.8.15-nodeps.jar",
        "execinfo",init_file])
    all_records=set(re.findall(r"^[a-f0-9]{16}\s+\d+ of\s+\d+\s+(\S+)\s*$",inventory,re.M))
    assert len(all_records)==exact["totalClassRecords"]
    admitted_test_names={row.attrib["classname"].replace(".","/") for row in cases}
    observed_product={name for name in all_records if name.startswith("dev/codex/schubert/nk/")}
    assert observed_product==targets|admitted_test_names
    execute("compile-raw",[JDK/"javac","--release","25","-Xlint:all","-Werror","-proc:none","-cp",cp,"-d",target,source])
    report=execute("raw",[JDK/"java","-cp",str(target)+os.pathsep+cp,
        "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement","--strict-original-exec","--line-deficits",init_file,*physical])
    raw={}
    for line in report.splitlines():
        item=line.split("\t")
        if item[0]=="CLASS":
            name=item[1]
            assert name not in raw and item[2]==crc64(binary_names[name].read_bytes())
            raw[name]={tag:dict(missed=int(miss),covered=int(covered))
                       for tag,miss,covered in (s.split(":") for s in item[6:])}
    assert set(raw)==set(binary_names)
    four=("LINE","METHOD","CLASS","BRANCH")
    two={name:record for name,record in raw.items() if name.rsplit("/",1)[-1] in ("OutboxEntry","OutboxRequest")}
    assert len(two)==2
    result=dict(run=OUT.name,source=unit["source"],productionCoreMain=old["source"],
        actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),qualified=pin(UNIT),originalFailedRun=unit["originalFailure"],
        originalSession=unit["run"],singleSession=True,coverageInputs=unit["productMainClasses"],exactMatchCrc=len(targets),
        totalExecRecords=len(all_records),observedProductTestTypes=len(admitted_test_names),
        testCounts=dict(tests=10,failed=0,errors=0,skipped=0,notRun=0),formatter=0,checkstyle=0,spotbugs=0,pmd=0,
        spotbugsAnalyzedClassCount=len(sb_names),twoTargetScopes=two,
        fourAllCovered=all(values[tag]["missed"]==0 for values in two.values() for tag in four),
        wholeRaw=raw,heldTypesOpened=0,originalFailedExecMerged=False,actualBackendOperations=0,whole451=False,formalDelta=0,steps=steps)
    (OUT/"manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result["fourAllCovered"],len(raw),{name.rsplit("/",1)[-1]:[v[t] for t in four] for name,v in two.items()})

if __name__=="__main__":
    main()
