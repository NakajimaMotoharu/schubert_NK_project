"""Bind current local evidence to WBS66 and verify the active design IDs."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


DOCS = Path("documents/400_PGPT/470_PMO")
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
MEDIA = Path("evidence/01_PT/009_NK-MED-001")
OPERATIONS = OPS.parent
WEB = Path("evidence/01_PT/016_NK-WEB-002")


def pin(path):
    return {"path":str(path),"sha256":sha256(path.read_bytes()).hexdigest()}


def named(parent,pattern):
    p, = parent.glob(pattern)
    return p


def json_file(p):
    return json.loads(p.read_bytes())


def git(*args):
    return subprocess.check_output(["git",*args],timeout=16)


def main():
    plan = named(DOCS,"601_*/1667_*.json")
    ctx = json_file(plan)["values"]
    for ref in ctx["oracleReferences"]:
        assert pin(Path(ref["path"]))==ref
    _,proto,screen,static,reader,decimal,media=[Path(ref["path"]) for ref in ctx["oracleReferences"]]
    actual=[json_file(p) for p in (proto,screen,static,reader,decimal,media)]
    required=(actual[0]["core"],actual[1]["productionCore"],actual[2]["source"],
              actual[3]["core"],actual[4]["productionCore"],actual[5]["source"])
    assert set(required)=={ctx["productionCoreMain"]}
    assert all(j["actualExit"]==j["formalDelta"]==0 for j in actual)
    assert actual[0]["productModuleCoverage"]=="1/6" and actual[0]["protocolPhysical"]==176
    assert actual[1]["tests"]==1 and actual[2]["dynamicProductTests"]==0
    assert len(actual[3]["exactGenuinePasses"])==3 and actual[3]["oldReadonlyToolTests"]==32
    assert actual[4]["ssc"]=="SSC-476" and actual[4]["cases"]==1
    assert actual[5]["wholeScope"]["BRANCH"]=={"covered":58,"missed":16}
    old=Path(actual[5]["unit"]["path"])
    local=json_file(old)
    assert local["actualProductTests"]==11 and local["fixtureCanaries"]==1
    assert local["newProductCases"]==1 and local["requiredOlderCases"]==10
    wf=named(Path("../PMO/hourly-monitor/wbs66-20261116"),"58_*/WBS.tsv")
    work={}
    required_rows={"WBS-F02-a":582,"WBS-F03/2-2":1004,"WBS-P016-15/2-照合":501,
                   "WBS-P018-08.03/2":742,"WBS-P009-04/2":392}
    for ln,line in enumerate(wf.read_text().splitlines(),1):
        fields=line.split("\t")
        if fields[0] in required_rows:
            assert required_rows[fields[0]]==ln and fields[0] not in work
            work[fields[0]]=dict(row=ln,description=fields[5],standardPricePp=float(fields[6]))
    assert set(work)==set(required_rows)
    ledger=named(Path("documents/900_OTHER/910_台帳"),"914_*.md")
    model=named(Path("documents/300_SS"),"330_*/333_*.md")
    remote=git("rev-parse","origin/main").decode().strip()
    assert remote==ctx["canonicalDesignSource"]==actual[4]["correctedCanonicalDesign"]
    raw_main=git("show",f"{remote}:{model}").decode()
    assert [line for line in raw_main.splitlines() if "SSC-476" in line] == [
        line for line in model.read_text().splitlines() if "SSC-476" in line]
    ledger_main=git("show",f"{remote}:{ledger}").decode()
    local_numbers=re.findall(r"(?m)^## SSC-(\d{3}) (.+)$",ledger.read_text())
    assert max(int(number) for number,_ in local_numbers)==476
    prior_heading,=[title for num,title in local_numbers if num=="475"]
    range_heading,=[title for num,title in local_numbers if num=="476"]
    assert "通知・質問検索" in prior_heading and "Range" in range_heading
    assert ledger_main.count("## SSC-476 ")==1 and "## SSC-475 Media Range" not in ledger_main
    items=(
        (proto,"WBS-F02-a", ["SYS-005","SS311"], (), OPERATIONS,"5628_*"),
        (screen,"WBS-P016-15/2-照合",["UI225/236","SS313"],("PT-WEB-SCR015-COUNT-001",),WEB,"4159_*"),
        (static,"WBS-F03/2-2",["SS352/354"],tuple(f"PT-OPS-JDBCGRAPH00{n}" for n in (6,7,8)),
         OPERATIONS,"5632_*"),
        (reader,"WBS-P018-08.03/2",["SS354","451"],tuple(f"PT-OPS-EXEC-NAMES-{n:03}" for n in range(1,9)),
         OPERATIONS,"5635_*"),
        (decimal,"WBS-P009-04/2",["SS333","SSC-476","DIF-012"],("PT-MED-RANGE-BOUND-001",),MEDIA,"4098_*"),
        (media,"WBS-P009-04/2",["SS333","SSC-476"],("PT-MED-PORT011",),MEDIA,"4099_*"),
    )
    rows=[]
    for receipt,id,design,tests,folder,pattern in items:
        spec=named(folder,pattern)
        text=spec.read_text()
        for test_id in tests:
            prefix = re.sub(r"\d+$","",test_id)
            assert test_id in text or prefix in text
        for source in (actual[1]["testSource"],actual[4]["source"],local["testInput"]):
            assert pin(Path(source["path"]))==source
        rows.append(dict(workId=id,originalWbs=work[id],verification=pin(receipt),
                         testIds=list(tests),specification=pin(spec),design=design,
                         assessedSource=ctx["productionCoreMain"],formalDelta=0))
    out=OPS/"PG41254-g08-current-short-and-independent-trace-v1"
    out.mkdir()
    result=out/"manifest.json"
    d=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=ctx["source"],
           productionCore=ctx["productionCoreMain"],canonicalDesign=remote,sourceTrace=rows,
           workingSsc475Reserved=True,currentRangeSsc476Verified=True,originalWbs=pin(wf),
           independentWorkIds=len(work),traceBindings=len(rows),exactFormalDelta=0,
           executedProductTests=0,whole451=False,wholeG08=False)
    with result.open("x") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(pin(result),len(rows),len(work))


if __name__ == "__main__":
    main()
