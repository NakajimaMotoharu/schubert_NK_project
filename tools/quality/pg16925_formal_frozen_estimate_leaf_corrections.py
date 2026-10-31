"""Append-only formal frozen-estimate/measurement-leaf projection for eleven original events; no Product run."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg998_metrics import append,canonical_fields,EVENTS
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG16925-formal-frozen-estimate-leaf-corrections-v1'
BASE=data.ROOT/'evidence/01_PT/018_NK-OPS-001'
PROFILE=[
 (3554,3555,'3280_ChildBrokerCaddy原七_現source資格仕様.md',(0.75,2,4),'低0.75/標準2/高4','WBS-P018-03.02',['WBS-P018-03'],[]),
 (3556,3557,'3283_ChildParentInspectorCaddy原十二_現source資格仕様.md',(0.75,2,4),'0.75/2/4','WBS-P018-03.02',['WBS-P018-03'],['WBS-P018-04.02']),
 (3558,3559,'3286_CaddyReadiness原二十_現source資格仕様.md',(0.75,2.5,5),'0.75/2.5/5','WBS-P018-04.02',['WBS-P018-03'],[]),
 (3560,3561,'3289_公開Unit四suite原十四_現source資格仕様.md',(0.75,2,4),'低0.75/標準2/高4','WBS-F03',[],[]),
 (3562,3563,'3292_MemoryLiveIntentFence原八_現source資格仕様.md',(0.75,2,4),'低0.75/標準2/高4','WBS-F03',[],[]),
 (3564,None,'3295_起動client原十七_現source資格仕様.md',(1.5,4,8),'低1.5/標準4/高8','WBS-F03',[],[])]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    assert not (data.ROOT.parent/'pgpt-runs/PG379/pg16926-original-start-client-seventeen-pt-v1').exists(),'current17 has not started'
    blobs=EVENTS.read_bytes().splitlines();rows={json.loads(b)['eventId']:(json.loads(b),data.sha(b)) for b in blobs}
    nodes={};parents=set()
    def collect(item):
        if isinstance(item,dict):
            if isinstance(item.get('id'),str):
                nodes.setdefault(item['id'],[]).append(item)
                if item.get('children'):parents.add(item['id'])
            for v in item.values():collect(v)
        elif isinstance(item,list):
            for v in item:collect(v)
    for filename in ['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json']:
        collect(json.loads((data.ROOT/'documents/400_PGPT/470_PMO'/filename).read_bytes()))
    assert 'WBS-P018-03' in parents and 'WBS-P018-03.02' in nodes and 'WBS-P018-03.02' not in parents
    for n in [3465,3466]:
        old=rows['PGPT-20261008-'+str(n)][0]
        assert old['measurementLeafIds']==['WBS-P018-03.02'] and old['leafAcceptedByCorrection'] is False
    plan=[]
    for first,last,spec,cost,token,leaf,canonical,related in PROFILE:
        ids=['PGPT-20261008-'+str(v) for v in [first,last] if v is not None]
        originals=[rows[n][0] for n in ids];start=originals[0]
        assert start['eventType']=='GROUP_START' and start['source']==SOURCE and all(r['source']==SOURCE and r['groupId']==start['groupId'] for r in originals)
        assert start['startEstimatePp']==dict(zip(['low','standard','high'],cost))
        path=BASE/spec;blob=path.read_bytes();assert token in blob.decode()
        frozen=dict(zip(['low','base','high'],cost))
        normalized,_=canonical_fields(dict(groupStartEstimatePp=frozen),'CHECKPOINT')
        assert normalized['estimateAtGroupStartPp']==frozen and leaf in nodes and leaf not in parents
        original_hashes={n:rows[n][1] for n in ids}
        plan.append(dict(groupId=start['groupId'],correctionOfEventIds=ids,originalEventRowSha256=original_hashes,originalSpecPath=str(path.relative_to(data.ROOT)),originalSpecSha256=data.sha(blob),originalGroupEstimatePp=frozen,groupStartEstimatePp=frozen,estimateAtGroupStartPp=frozen,measurementLeafIds=[leaf],primaryWbs=leaf,canonicalArtifactOwnerReferences=canonical,relatedLeafReferences=related,referenceAdditionalBudgetPp=0,measurementLeafStatus='PARTIAL_TEST_OR_TECHNICAL_EVIDENCE_LINK_ONLY_NOT_LEAF_ACCEPTANCE',leafAcceptedByCorrection=False,parentAndChildCostsNotSummed=True,actualAllocatedPp=None,N=None,T=None,originalCaptureStatus=start.get('captureStatus'),captureStatus=start.get('captureStatus','CURRENT_APPEND_CORRECTION_NO_BACKDATE'),current17StillNotExecuted=first==3564))
    assert len(plan)==6 and sum(len(r['correctionOfEventIds']) for r in plan)==11
    assert plan[2]['captureStatus']=='LATE_CAPTURE_AFTER_ORIGINAL_PT_NOT_A_PREEXECUTION_EVENT'
    # No aliases may erase parent hierarchy, manufacture a leaf acceptance, or change a cost.
    assert any(r.get('children') for r in nodes['WBS-P018-03'])
    assert any(not r.get('children') for r in nodes['WBS-P018-03'])  # legacy comparison row exists
    assert all(set(r['groupStartEstimatePp'])=={'low','base','high'} and not set(r['measurementLeafIds'])&parents for r in plan)
    verify(invocation);OUT.mkdir();data.write(OUT/'before.safe.json',dict(source=SOURCE,invocation=invocation,profile=plan,originalRowsRetained=True,originalEventCount=len(rows),productTestsExecuted=0))
    completed=[]
    for row in plan:
        # Restart safety: a prior partial append with the exact identity is referenced, never resent.
        now=[json.loads(b) for b in EVENTS.read_bytes().splitlines()]
        found=[r for r in now if r.get('correctionType')=='PG16925_FORMAL_ESTIMATE_MEASUREMENT_LEAF_V1' and r.get('correctionOfEventIds')==row['correctionOfEventIds']]
        if found:
            assert len(found)==1 and all(found[0][k]==v for k,v in row.items() if k!='groupId');event=found[0]['eventId']
        else:
            values=dict(row);group=values.pop('groupId')
            values.update(workCategory='ADMIN',source=SOURCE,correctionType='PG16925_FORMAL_ESTIMATE_MEASUREMENT_LEAF_V1',newAccepted=0,formalUpdated=False,productTestsReexecuted=0,technicalProgressAddedByCorrection=False,previousMeasurementLeafCorrectionEvents=['PGPT-20261008-3465','PGPT-20261008-3466'],groupBudgetAdditive=False,notes='3298/BUG2192/YKT1939; preserve original spec, estimate, source/run, time and late capture. Official base is the frozen standard amount, not an estimate revision. Canonical references have no extra budget or cost allocation.')
            event=append(group,'CHECKPOINT',values)
        completed.append(dict(eventId=event,**row))
    after={json.loads(b)['eventId']:(json.loads(b),data.sha(b)) for b in EVENTS.read_bytes().splitlines()}
    assert all(after[n][1]==digest for row in plan for n,digest in row['originalEventRowSha256'].items())
    assert all(after[row['eventId']][0]['estimateAtGroupStartPp']==row['originalGroupEstimatePp'] and after[row['eventId']][0]['wbsLeafIds']==row['measurementLeafIds'] for row in completed)
    assert not (data.ROOT.parent/'pgpt-runs/PG379/pg16926-original-start-client-seventeen-pt-v1').exists()
    verify(invocation);data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,corrections=completed,groupCount=6,originalEventCountCorrected=11,allOriginalRowsRetained=True,originalEstimatesChanged=False,originalCaptureTimesChanged=False,lateCapturePreserved=True,officialEstimateAndLeafExportVerified=True,allParentsFromBothMastersRetained=True,productTestsExecuted=0,productTestsReexecuted=0,actualAllocatedPp=None,N=None,T=None,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('corrections',','.join(r['eventId'] for r in completed))
if __name__=='__main__':main()
