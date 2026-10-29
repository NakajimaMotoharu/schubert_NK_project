"""Extend scoped host references to24 original executions; never replay or merge exec coverage."""
import copy
import json
import subprocess
import current_host_program_measurements_v1 as old
from trace_owner_join import canonical
from host_tool_invocation import capture,verify
from pg9880_snapshot_nonce_trace import audit

SOURCE=old.SOURCE
data=old.data
INV,SNAP,SECTIONS=old.INV,old.SNAP,old.SECTIONS
BASE="4541a217dd17e64d4daff9390b63b41ea791afd9"
OUT=data.BASE/"PG14176-current-host-program-measurements-24exec-v2"
RECORD="evidence/01_PT/018_NK-OPS-001/2601_現source二十四実行・完全Program測定_WBS参照結果.md"
OVERLAY="currentScopedHostMeasurementsPG14176"
ADDED=[
 ("PG14130-metric-mode-retention-whole-twenty-one-post-v1","2ae8a800873aa4d4db6caa531dd8e17ae135c7c197a575784d10bdfb0ff96b86",21,3),
 ("PG14136-alert-state-whole-thirty-six-post-v1","8245c63a6ba9765c7e417d4ccf4c2a1c2fff643b0af32c6d49b40975086279c3",36,4),
 ("PG14142-clock-filesystem-poller-whole-thirty-two-post-v1","bb3ed62011e58627711899eec827267b63afc5bdb30966ba53d6aa00c6b7a7fc",32,4),
 ("PG14148-heap-observation-connection-whole-seventeen-post-v1","aec1ce472b2e69b4d955987a21401e677282a2686eb2d26540674089243d1e0a",17,2),
 ("PG14154-policy-registry-status-missing-whole-twenty-two-post-v1","81a8a35942de02532dbd25dcecc3da2a6be258d58632065107790a246850c97e",22,4),
 ("PG14160-supplied-backlog-backup-whole-thirty-three-post-v1","9a18aa2413b319ad35aaba0ee9d00175df5c527afe8108db05bc0b010ee73dcb",33,4),
 ("PG14166-dlq-integrity-restart-whole-twenty-four-post-v1","b82f772091789826222714328ceff0eb3da7085a143b89bfb3ade7c603b49f0c",24,3),
 ("PG14172-transfer-metric-health-whole-sixteen-post-v1","f076c05a6f568cd7394bc05f231e2c81604cf2bce9c1683c645466fa01f681db",16,2)]

def inputs():
    prior,refs,programs,natural,_,_,pin,modules=old.inputs()
    previous=data.read_checked(old.OUT/"manifest.json","9c01f2521b537607e818f5cce2d3f20eacce84fe4649053faa41451afef46903")
    assert previous["source"]==SOURCE and refs==previous["originalPostReferences"] and programs==previous["fullSourceProgramMeasurements"] and natural==previous["naturalZeroBranchSources"]
    raw,snap=[subprocess.check_output(["git","show",BASE+":"+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw)=="3cacce76a16c553f556e6a00cf05a48b3d25e5ca701a55f5081c5b2ccf3e9234"
    assert data.sha(snap)=="3a31a522bb413fb638e0271611b9d2975131f6a594afbce5990c08610e7a67b9"
    logical={r["path"]:r for r in json.loads(raw)["artifacts"]}
    normal,normal_pin=old.cfg.normal();assert normal_pin==pin
    hashes=normal["begin"]["inputHashes"]
    for name,h,methods,suites in ADDED:
        post=data.read_checked(data.BASE/name/"manifest.json",h)
        assert post["source"]==SOURCE and post["actualExit"]==0 and post["tests"]==len(post["cases"])==methods and post["suites"]==suites
        assert all(post[k] is False for k in ["formalUpdated","wholeF03Accepted","whole451Accepted","oldCoverageTransferred"])
        assert post["failures"]==post["errors"]==post["skipped"]==post["newAccepted"]==post["productTestsReexecutedByPost"]==post["crcMismatch"]==0 and post["singleSession"] is True
        ref=dict(path=str((data.BASE/name/"manifest.json").relative_to(data.ROOT)),sha256=h,source=SOURCE,methods=methods,suites=suites)
        refs.append(ref)
        assert set(post["fullSourceUnits"])==set(post["completeSourceUnitClosure"])
        for unit,value in sorted(post["fullSourceUnits"].items()):
            closure=value["physical"];totals=value["totals"];path=old.unit_path(unit)
            assert sorted(closure)==sorted(post["completeSourceUnitClosure"][unit]) and set(totals)=={"LINE","METHOD","CLASS","BRANCH"}
            assert all(type(v["missed"]) is int and v["missed"]==0 and type(v["covered"]) is int and v["covered"]>=0 for v in totals.values())
            assert all(totals[k]["covered"]>0 for k in ["LINE","METHOD","CLASS"])
            owner=canonical(path,logical);assert owner["canonicalOwner"]==owner["canonicalCostOwner"]=="WBS-P018-09"
            assert post["owners"][path]==dict(sha256=hashes[path],**owner)
            if value["four100"]:
                assert totals["BRANCH"]["covered"]>0
                programs.append(dict(source=SOURCE,sourceUnit=unit,completeSourceClosure=closure,executablePhysical=len(closure),postManifest=ref,totalsFromOneOriginalExecOnly=totals,path=path,sourceSha256=hashes[path],canonicalOwnership=owner,runtimeDomain="ONE_ORIGINAL_SCOPED_EXECUTION_NOT_GLOBAL_UNION",formalAccepted=False))
            else:
                assert totals["BRANCH"]==dict(missed=0,covered=0)
                natural.append(dict(sourceUnit=unit,path=path,totals=totals,qualification="FULL_SOURCE_COUNTERS_WITH_NATURAL_ZERO_BRANCH_NOT_FOUR100",postManifest=ref,source=SOURCE,sourceSha256=hashes[path],branchPercent=None,canonicalOwnership=owner,formalAccepted=False))
    cases=[]
    for ref in refs:
        post=data.read_checked(data.ROOT/ref["path"],ref["sha256"]);cases.extend((r["classname"],r["name"]) for r in post["cases"])
    assert len(refs)==len({r["path"] for r in refs})==24 and len(cases)==len(set(cases))==384 and sum(r["suites"] for r in refs)==57
    assert len(programs)==len({r["sourceUnit"] for r in programs})==37 and sum(r["executablePhysical"] for r in programs)==69
    assert len(natural)==len({r["sourceUnit"] for r in natural})==6 and not ({r["sourceUnit"] for r in natural}&{r["sourceUnit"] for r in programs})
    return prior,refs,programs,natural,raw,snap,pin,modules

def expected(prior,refs,programs,natural,pin,modules):
    value=old.expected(prior,refs,programs,natural,pin,modules)
    value.update(record=RECORD,originalExecutions=24,uniqueMethods=384,suiteReferences=57,fullSourceProgramsFour100=37,fullSourceExecutablePhysicalFour100=69,naturalZeroBranchSourceCount=6,previousHostRegistryReference=dict(path=str((old.OUT/"manifest.json").relative_to(data.ROOT)),sha256="9c01f2521b537607e818f5cce2d3f20eacce84fe4649053faa41451afef46903"),previous16HostRegistryPreserved=True)
    return value

def documents(value,raw,snap):
    original=json.loads(raw);result=raw
    overlay={k:copy.deepcopy(value[k]) for k in ["source","record","qualification","fullSourceProgramsFour100","fullSourceExecutablePhysicalFour100","naturalZeroBranchSourceCount","originalExecutions","uniqueMethods","suiteReferences","previous995RowsAndHistoricalRuntimeUnchanged","previousSnapshotCurrentQualificationUnchanged","globalExecUnion","newAccepted","formalUpdated","whole451Accepted"]}
    overlay.update(manifest=str((OUT/"manifest.json").relative_to(data.ROOT)),sha256=data.sha((OUT/"manifest.json").read_bytes()))
    for name in SECTIONS:
        section=copy.deepcopy(original[name]);assert OVERLAY not in section
        section[OVERLAY]=copy.deepcopy(overlay);result,_,_=old.replaced(result,name,section)
    result_snap,_,_=old.replaced(snap,"inventorySha256",data.sha(result))
    old.validate_docs(result,result_snap,original,json.loads(snap))
    restored=json.loads(result)
    for name in SECTIONS:restored[name].pop(OVERLAY)
    assert restored==original
    return result,result_snap

def main():
    invocation=capture(__file__);assert not OUT.exists() and (data.ROOT/RECORD).is_file()
    args=inputs();prior,refs,programs,natural,raw,snap,pin,modules=args
    assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    value=expected(prior,refs,programs,natural,pin,modules)
    observed=audit();assert observed["actualExit"]==1 and not observed["passed"]
    value.update(invocation=invocation,wholeWbsAuditBefore=observed)
    verify(invocation);OUT.mkdir();data.write(OUT/"manifest.json",value)
    print(data.sha((OUT/"manifest.json").read_bytes()))
if __name__=="__main__":main()
