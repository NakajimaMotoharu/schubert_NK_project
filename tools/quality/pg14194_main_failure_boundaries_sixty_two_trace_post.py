"""Independent62 retained Main catch references; never promote structural review to whole quality."""
import copy
import json
import f03_main_failure_boundary_sixty_two_trace_v1 as trace
from host_tool_invocation import capture,verify
from pg9880_snapshot_nonce_trace import audit

OUT=trace.data.BASE/"PG14194-main-failure-boundaries-sixty-two-trace-post-v1"
PIN="eaed345a74d501a1c4044d17851ac46abb3ef132c2d6a646805c37e82b9beec5"

def main():
    invocation=capture(__file__);assert not OUT.exists()
    prior,rows,raw,snap=trace.inputs()
    value=trace.data.read_checked(trace.OUT/"manifest.json",PIN);verify(value["invocation"])
    actual=copy.deepcopy(value)
    for k in ["invocation","wholeWbsAuditBefore"]:actual.pop(k,None)
    expected=trace.expected(prior,rows)
    strict=lambda v:json.dumps(v,sort_keys=True)==json.dumps(expected,sort_keys=True)
    assert strict(actual)
    a,b=trace.documents(value,raw,snap)
    assert (trace.data.ROOT/trace.INV).read_bytes()==a and (trace.data.ROOT/trace.SNAP).read_bytes()==b
    trace.validate_docs(a,b,json.loads(raw),json.loads(snap))
    original=trace.data.read_checked(trace.data.BASE/trace.ORIGINAL[0],trace.ORIGINAL[1])
    before_ids,before_refs,_=trace.previous_state();ids,refs,pending=trace.state_after()
    generic=trace.main_generic_ids();selected={r["id"] for r in rows}
    assert len(generic-before_refs)==520 and len(generic-refs)==458
    assert selected==trace.new_ids() and selected<=(generic-before_refs) and len(selected)==62
    assert selected.isdisjoint(before_refs) and before_ids==ids and len(refs-before_refs)==62
    assert all(r["rule"]=="AvoidCatchingGenericException" and r["id"] in generic and r["currentWholeJoinPending"] is True for r in rows)
    old_sync={r["id"] for r in original if r["sourceKind"]=="MAIN" and r["rule"]=="AvoidSynchronizedStatement"}
    assert len(old_sync)==96 and old_sync<=refs
    assert value["sourceRows"]==prior["sourceRows"] and value["currentQualification"]==prior["currentQualification"] and value["currentMainMonitorEightyOneReferences"]==prior["currentMainMonitorEightyOneReferences"]
    negatives=[]
    changes=[
      ("all-vs-new",lambda v:v[trace.FIELD].update(newCurrentReferences=len(generic))),
      ("double-new",lambda v:v.update(joinedContextWarnings=3698)),
      ("drop-new",lambda v:v[trace.FIELD]["rows"].pop()),
      ("old-id-in-new",lambda v:v[trace.FIELD]["rows"][0].update(id=sorted(before_refs)[0])),
      ("source",lambda v:v.update(source="0"*40)),
      ("raw-loss",lambda v:v.update(sourceDerivedRaw=6185)),
      ("false-retained",lambda v:v[trace.FIELD]["rows"][0].update(rawRetained=False)),
      ("runtime-promoted",lambda v:v[trace.FIELD].update(currentRuntimeQualification=True)),
      ("bool-test-count",lambda v:v[trace.FIELD].update(productTestsExecuted=False)),
      ("formal",lambda v:v.update(formalUpdated=True)),
      ("acceptance",lambda v:v.update(newAccepted=1)),
      ("old-runtime-loss",lambda v:v["sourceRows"].pop())]
    for label,change in changes:
        bad=copy.deepcopy(actual);change(bad)
        assert json.dumps(bad,sort_keys=True)!=json.dumps(actual,sort_keys=True) and not strict(bad)
        negatives.append(label)
    observed=audit();assert observed["actualExit"]==1 and not observed["passed"]
    verify(invocation);OUT.mkdir()
    trace.data.write(OUT/"manifest.json",dict(actualExit=0,source=trace.SOURCE,invocation=invocation,traceManifestSha256=PIN,inventorySha256=trace.data.sha(a),snapshotSha256=trace.data.sha(b),sourceDerivedRaw=6247,mainRaw=1491,testRaw=4756,originalCorrections=3194,newCurrentReferences=62,sourceFiles=5,joinedContextWarnings=3636,currentWholeJoinPending=2775,noCurrentReference=2611,previousUnreferencedMainGeneric=520,remainingUnreferencedMainGeneric=458,all96MainSyncStillReferenced=True,all995SourceRowsHistoricalRuntimeUnchanged=True,metadataNegativeVectors=len(negatives),negativeLabels=negatives,wholeWbsAudit=observed,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(trace.data.sha((OUT/"manifest.json").read_bytes()))
if __name__=="__main__":main()
