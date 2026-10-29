"""Independent retained counts and typed metadata, all96 vs old15/new81."""
import copy
import json
import f03_main_monitor_eighty_one_trace_v2 as trace
from host_tool_invocation import capture,verify
from pg9880_snapshot_nonce_trace import audit

OUT=trace.data.BASE/'PG14088-main-monitor-eighty-one-trace-post-v1'
PIN='7ae5c6848478b409aa366c974e777aa25d0a7abac23fbe1b328e82d68d01580c'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    prior,rows,raw,snap=trace.inputs()
    value=trace.data.read_checked(trace.OUT/'manifest.json',PIN);verify(value['invocation'])
    actual=copy.deepcopy(value)
    for key in ['invocation','wholeWbsAuditBefore']:actual.pop(key,None)
    expected=trace.expected(prior,rows)
    strict=lambda v:json.dumps(v,sort_keys=True)==json.dumps(expected,sort_keys=True)
    assert strict(actual)
    a,b=trace.documents(value,raw,snap)
    assert (trace.data.ROOT/trace.INV).read_bytes()==a and (trace.data.ROOT/trace.SNAP).read_bytes()==b
    trace.validate_docs(a,b,json.loads(raw),json.loads(snap))
    original=trace.data.read_checked(trace.data.BASE/trace.ORIGINAL[0],trace.ORIGINAL[1])
    before_ids,before_refs,_=trace.previous_state();ids,refs,pending=trace.state_after()
    all_main_sync={r['id'] for r in original if '/src/main/java/' in r['path'] and r['rule']=='AvoidSynchronizedStatement'}
    selected={r['id'] for r in rows}
    assert len(all_main_sync)==96 and len(all_main_sync&before_refs)==15
    assert selected==all_main_sync-before_refs and len(selected)==81
    assert selected.isdisjoint(before_refs) and all_main_sync<=refs
    assert before_ids==ids and len(refs-before_refs)==81 and len(all_main_sync-refs)==0
    assert value['sourceRows']==prior['sourceRows'] and value['currentQualification']==prior['currentQualification']
    negatives=[]
    changes=[
      ('wrong-all-vs-new',lambda v:v['currentMainMonitorEightyOneReferences'].update(newCurrentReferences=96)),
      ('double-count-old15',lambda v:v.update(joinedContextWarnings=3589)),
      ('drop-new',lambda v:v['currentMainMonitorEightyOneReferences']['rows'].pop()),
      ('old-id-in-new',lambda v:v['currentMainMonitorEightyOneReferences']['rows'][0].update(id=sorted(all_main_sync&before_refs)[0])),
      ('source',lambda v:v.update(source='0'*40)),
      ('raw-loss',lambda v:v.update(sourceDerivedRaw=6166)),
      ('false-retained',lambda v:v['currentMainMonitorEightyOneReferences']['rows'][0].update(rawRetained=False)),
      ('runtime-promoted',lambda v:v['currentMainMonitorEightyOneReferences'].update(currentRuntimeQualification=True)),
      ('bool-test-count',lambda v:v['currentMainMonitorEightyOneReferences'].update(productTestsExecuted=False)),
      ('formal',lambda v:v.update(formalUpdated=True)),
      ('acceptance',lambda v:v.update(newAccepted=1)),
      ('old-runtime-loss',lambda v:v['sourceRows'].pop())]
    for label,change in changes:
        bad=copy.deepcopy(actual);change(bad)
        assert json.dumps(bad,sort_keys=True)!=json.dumps(actual,sort_keys=True) and not strict(bad)
        negatives.append(label)
    observed=audit();assert observed['actualExit']==1 and not observed['passed']
    verify(invocation);OUT.mkdir()
    trace.data.write(OUT/'manifest.json',dict(actualExit=0,source=trace.SOURCE,invocation=invocation,traceManifestSha256=PIN,inventorySha256=trace.data.sha(a),snapshotSha256=trace.data.sha(b),sourceDerivedRaw=6247,mainRaw=1491,testRaw=4756,allMainSynchronizedRaw=96,previousMainSyncReferences=15,newCurrentReferences=81,remainingUnreferencedMainSync=0,sourceFiles=len({r['path'] for r in rows}),joinedContextWarnings=3574,currentWholeJoinPending=2713,noCurrentReference=2673,all995SourceRowsHistoricalRuntimeUnchanged=True,metadataNegativeVectors=len(negatives),negativeLabels=negatives,wholeWbsAudit=observed,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(trace.data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
