"""Join current DAO and output value tests in one ordinary, admitted execution."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

HERE = Path("evidence/01_PT/004_NK-DAT-001")
OPS = Path("evidence/01_PT/018_NK-OPS-001")
CORE = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
PACKAGE = "dev/codex/schubert/nk/batch/repository/"
JAVA = f"src/schubert-nk-batch/src/main/java/{PACKAGE}"
TEST = f"src/schubert-nk-batch/src/test/java/{PACKAGE}ObservationValueContractTest.java"
SUITE = "dev.codex.schubert.nk.batch.repository.ObservationValueContractTest"


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def load(row):
    p = Path(row["path"])
    assert pin(p)==row
    return json.loads(p.read_bytes())


def run(step, args, where, stages):
    begin = datetime.now(timezone.utc).isoformat()
    argv = list(map(str,args))
    outcome = subprocess.run(argv,check=False,capture_output=True,cwd=where,timeout=50)
    stdout,stderr = where/(step+".stdout"),where/(step+".stderr")
    stdout.write_bytes(outcome.stdout)
    stderr.write_bytes(outcome.stderr)
    stages[step]=dict(argv=argv,actualExit=outcome.returncode,stdout=pin(stdout),stderr=pin(stderr),
                      start=begin,terminalAtUTC=datetime.now(timezone.utc).isoformat())
    path=where/(step+"-terminal.json")
    path.write_text(json.dumps(stages[step],indent=2)+"\n")
    assert outcome.returncode==0
    return outcome.stdout


def main():
    cp, = Path("documents/400_PGPT/470_PMO").glob("601_*/1579_*.json")
    g=json.loads(cp.read_bytes())
    scope=g["values"]
    dao, value, maven, current_tool = map(load,scope["oracleReferences"][1:])
    assert all(row["actualExit"]==0 for row in (dao,value,maven,current_tool))
    assert dao["counts"]==dict(tests=9,failures=0,errors=0,skipped=0)
    core=scope["productionCoreMain"]
    assert core==maven["source"]
    assert dao["source"]!=core  # Prior roster only; every current input is rebound below.
    initial=Counter(tuple(item) for item in dao["roster"])
    expected_value=Counter((row["classname"],row["name"]) for row in value["cases"] if row["classname"]==SUITE)
    assert len(initial)==9 and len(expected_value)==3
    inputs=[Path(row["path"]) for row in dao["sourceInputs"]]
    extra=[Path(JAVA+"InspectionSummary.java"),Path(JAVA+"CleanupCounts.java"),Path(TEST)]
    inputs += extra
    proof=[]
    for item in inputs:
        sha=pin(item)
        assert sha["sha256"]==sha256(subprocess.check_output(
            ["git","show",f'{scope["source"]}:{item}'],timeout=10)).hexdigest()
        proof.append(sha)
    assert [entry for entry in proof if entry["path"] in [r["path"] for r in dao["sourceInputs"]]
            ]==dao["sourceInputs"]
    cwd=Path("../pgpt-runs/PG379").resolve()/scope["run"]
    cwd.mkdir(mode=0o700)
    classes,reports,stream = (cwd/key for key in ("classes","unit","joint.exec"))
    stages={}
    old_work=Path(dao["exec"]["path"]).parent
    prior_compile=dao["steps"][0]["command"]
    compile_argv=[p.replace(str(old_work),str(cwd)) for p in prior_compile]
    assert compile_argv[-len(dao["sourceInputs"]):]==[str(f) for f in inputs[:len(dao["sourceInputs"])]]
    run("compile",[*compile_argv[:len(compile_argv)-len(dao["sourceInputs"])],
                    *(p.resolve() for p in inputs)],cwd,stages)
    packaged={}
    with ZipFile(maven["batchArtifact"]["path"]) as jar:
        for name in ("RunReferenceRepository","RunReferences","BatchRun","InspectionSummary","CleanupCounts"):
            member=PACKAGE+name+".class"
            actual=(classes/member).read_bytes()
            assert actual==jar.read(member)
            packaged[member]=sha256(actual).hexdigest()
    java = prior_compile[0].replace("/javac","/java")
    session = "PG41150-RRF-DAO-VALUE-JOINT"
    argv=[]
    for argument in dao["steps"][1]["command"]:
        argument=argument.replace(str(old_work),str(cwd)).replace("/unit.exec","/joint.exec")
        argument=argument.replace(dao["session"],session)
        argv.append(argument)
    run("unit",[*argv,"--select-class",SUITE],cwd,stages)
    xml=reports/"TEST-junit-jupiter.xml"
    root=ET.parse(xml).getroot()
    counts={key:int(root.attrib[key]) for key in ("tests","errors","failures","skipped")}
    assert counts==dict(tests=12,errors=0,failures=0,skipped=0)
    assert Counter((n.attrib["classname"],n.attrib["name"]) for n in root.findall("testcase"))==initial+expected_value
    assert not any(root.findall(tag) for tag in (".//error",".//failure",".//skipped"))

    product={p.relative_to(classes).as_posix().removesuffix(".class"):p
             for p in classes.rglob("*.class") if not re_test(p.stem)}
    assert len(product)==10
    names={PACKAGE+name for name in ("RunReferenceRepository","RunReferences")}
    decode=runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    crc=runpy.run_path(str(OPS/"input/5257_p01810_broker_evidence_value_post.py"))["crc64"]
    d=decode(stream.read_bytes(),names)
    assert [r["labelBytesHex"] for r in d["sessions"]]==[session.encode().hex()]
    assert {name:int(row["crc64"],16) for name,row in d["classes"].items()}=={
        name:int(crc(product[name].read_bytes()),16) for name in names}
    dependencies = json.loads(next((OPS/"evidence").glob("PG31432-*/compile.json")).read_bytes())["dependencies"]
    assert all(pin(Path(row["path"]))==row for row in dependencies)
    cp_sdk=os.pathsep.join(row["path"] for row in dependencies)
    rawbin = cwd/"rawtool"
    assert current_tool["source"] == subprocess.check_output(
        ["git","log","-1","--format=%H","--",str(CORE)],text=True,timeout=10).strip()
    run("raw-compile",[prior_compile[0],"--release","25","-proc:none","-Xlint:all","-Werror",
                         "-cp",cp_sdk,"-d",rawbin,CORE.resolve()],cwd,stages)
    visible=run("raw",[java,"-cp",f"{rawbin}:{cp_sdk}","org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                        "--strict-original-exec",stream,*[product[n] for n in sorted(product)]],cwd,stages)
    raw={}
    for line in visible.decode().splitlines():
        cells=line.split("\t")
        if cells[0]=="CLASS":
            raw[cells[1]]={item.split(":")[0]:[int(v) for v in item.split(":")[1:]] for item in cells[6:]}
    assert set(raw)==product.keys()
    assert all(miss==0 and hit>0 for name in names for miss,hit in raw[name].values())
    out=HERE/"evidence"/scope["run"]
    out.mkdir()
    table=out/"unfiltered.tsv"
    table.write_bytes(visible)
    receipt=out/"manifest.json"
    with receipt.open("x") as f:
        json.dump(dict(actualExit=0,core=core,source=scope["source"],group=g["eventId"],
                       observed=counts,testsCompared=sorted(initial+expected_value),newDefinitions=0,
                       physicalQualified=packaged,scopedRaw={name:raw[name] for name in sorted(names)},
                       auxiliaryMeasurements={name:raw[name] for name in sorted(raw.keys()-names)},
                       inputFiles=proof,physicalFiles=[pin(p) for p in product.values()],
                       xml=pin(xml),exec=pin(stream),session=session,raw=pin(table),originals=scope["oracleReferences"][1:],
                       steps=stages,oldStreamsMerged=0,actualDbRootNativeActions=0,formalDelta=0,whole451=False,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),f,indent=2,ensure_ascii=False)
        f.write("\n")
    print(pin(receipt),counts)


def re_test(name):
    return name.startswith(("ObservationValueContractTest","RunReferenceRepositoryPureJdbcTest"))


if __name__=="__main__":
    main()
