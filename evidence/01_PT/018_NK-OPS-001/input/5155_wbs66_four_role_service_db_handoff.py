"""Join the new service database source and independent test evidence to the four roles."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

B = Path("evidence/01_PT/018_NK-OPS-001")
E = B / "evidence"
D = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
OUT = E / "PG39454-wbs66-four-role-service-jdbc-handoff-v1"


def one(parent, pattern):
    hits = list(parent.glob(pattern))
    assert len(hits) == 1, pattern
    return hits[0]


def evidence(run):
    return one(E, run + "-*/manifest.json")


def ref(p):
    return dict(path=str(p), sha256=sha256(p.read_bytes()).hexdigest())


def load(p):
    return json.loads(p.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=25)


def current_hash(source, path):
    return sha256(git("show", f"{source}:{path}")).hexdigest()


def diff(old, new, prefix):
    query=f":(glob)src/*/src/{prefix}/java/**/*.java"
    return [s.decode() for s in git("diff", "--name-only", "-z", old, new, "--", query).split(b"\0") if s]


def main():
    start = load(one(D,"448_*"))
    prior_p = evidence("PG39312")
    prior = load(prior_p)
    focused_p = evidence("PG39452")
    focused = load(focused_p)
    storage_p = evidence("PG39426-f03")
    storage = load(storage_p)
    core = start["baseCore"]
    head = start["values"]["source"]
    assert focused["source"] == core and git("rev-parse","HEAD").decode().strip() == head
    assert git("rev-parse","origin/dev-foundation").decode().strip() == head
    build = load(Path(focused["proofs"]["build"]["path"]))
    static = load(Path(focused["proofs"]["staticOriginal"]["path"]))
    main_paths = diff(prior["source"],core,"main")
    test_paths = diff(prior["inspectionHead"],head,"test")
    assert set(main_paths) == set(build["changedSources"]) and len(main_paths) == 2
    proofs = {}
    for run in ("PG39324","PG39342","PG39360","PG39378","PG39396","PG39414","PG39428"):
        p = evidence(run)
        cert = load(p)
        assert cert["actualExit"] == 0
        for name, value in cert["inputHashes"].items():
            if name in test_paths and current_hash(head,name) == value:
                proofs[name] = ref(p)
    for name,value in static["inputHashes"].items():
        if name in test_paths and value == current_hash(head,name):
            proofs[name] = ref(focused_p)
    assert set(proofs) == set(test_paths),(set(test_paths)-set(proofs))
    assert all(current_hash(head,n)==ref(Path(n))["sha256"] for n in main_paths+test_paths)
    templates = prior["c02"]["templateHashes"]
    assert len(templates)==14 and all(current_hash(core,n)==h for n,h in templates.items())
    owner_path = one(D.parent,"485_*.json")
    owner = {n["path"]:n["owner"] for n in load(owner_path)["artifacts"] if n["path"] in main_paths}
    assert set(owner.values())=={"WBS-P018-05"} and len(owner)==2
    ssc = prior["ssc447Historical"]
    assert all(ref(Path(n["path"]))==n for n in (ssc["proof"],ssc["laterProtocolSeparate"]))
    assert ssc["tests"]==ssc["success"]==152 and all(ssc[k]==0 for k in ("failed","errors","skipped","notRun"))
    canonical=git("rev-parse","origin/main").decode().strip()
    docs=[x.decode() for x in git("ls-tree","-r","-z","--name-only",canonical,"documents/300_SS").split(b"\0")
          if x and Path(x.decode()).name[:4] in ("311_","332_","342_","343_")]
    assert len(docs)==4
    unit=load(Path(focused["proofs"]["unit"]["path"]))
    by_name={Path(p).stem:p for p in test_paths}
    traced=[]
    for path in main_paths:
        name=Path(path).stem
        t=name+"PortTest"
        cases=[dict(className=klass,method=method) for klass,method in unit["selectedCases"] if klass.rsplit(".",1)[1]==t]
        assert len(cases)==(16 if name.endswith("Admission") else 15)
        traced.append(dict(main=path,program="NK-OPS-001",artifactOwner=owner[path],requirements=["SYS-002","SYS-004","DAT-001"],
            relatedCriteria=["WBS-F02-a","WBS-P004-05/2","WBS-P018-05"],canonicalDesignSource=canonical,
            design=[dict(path=x,blob=git("rev-parse",f"{canonical}:{x}").decode().strip()) for x in docs],
            test=by_name[t],methods=cases,spec=ref(one(B,"4672_*")),result=ref(one(B,"4673_*")),evidence=ref(focused_p)))
    value=dict(actualExit=0,id="W66-HANDOFF-20261118-06",startEvent=start["eventId"],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=core,inspectionHead=head,remoteHeadVerified=True,
        previous=ref(prior_p),criteriaByRole=prior["criteriaByRole"],ssc447Historical=ssc,
        f02=dict(fourMain=482,physical=1102,buildActualExit=0,receipt=ref(focused_p),migratedUpperSites=32,remainingUpperSites=72,
          newArchitectureExecution=0,priorStorageEdgeStillExactBytes=not build["deltas"]["storage"]["changed"],
          need=["API/Web typed gate and QA056","72 upper / three Storage and original entry","current whole architecture and runtime/451"]),
        f03=dict(previousMain=prior["f03"]["main"],previousTest=prior["f03"]["test"],newMainExactReplacementPaths=main_paths,
          newTestExactReplacementPaths=test_paths,testProofs=proofs,currentMainEligibleConfirmed=1023,currentTestEligibleConfirmed=1101,
          fourModulesSpotBugsMissing0=ref(Path(focused["proofs"]["repair"]["path"])),currentWholeSixStatus="UNACCEPTED",
          need=["Main4 / Test32 held","Root11, PMD45, six typed and 451"]),
        c02=dict(activeRuntimeConfirmed=False,verifiedTemplateHashes=templates,need=prior["c02"]["remaining"]),
        f04=prior["f04"],scopesTrace=dict(sourceOwner=ref(owner_path),changedCurrentMainAndTest=traced,storageWorkerRecord=ref(storage_p)),
        deadlineJST=prior["deadlineJST"],externalAcknowledgement=None,externalActions=0,addedProductExecutions=0,
        formalAcceptance=17,formalDenominator=190,newAcceptance=0,officialPt=1964,officialScope=53,effortCompletionRate=None)
    OUT.mkdir()
    out=OUT/"manifest.json"
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
    print(ref(out))


if __name__ == "__main__":
    main()
