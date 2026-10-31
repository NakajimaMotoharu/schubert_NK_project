"""Independent read-only qualification of six append corrections; original costs/events retained."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG16927-formal-frozen-estimate-leaf-corrections-post-v1'
def main():
    invocation=capture(__file__);assert not OUT.exists()
    p=data.read_checked(data.BASE/'PG16925-formal-frozen-estimate-leaf-corrections-v1/manifest.json','228ecac632d7a72cded5df9e7feb39b16eda4b3341b411e0f6edce9a23862f99')
    lines=(data.ROOT.parent/'PMO/pgpt-execution-metrics/events.jsonl').read_bytes().splitlines()
    events={json.loads(b)['eventId']:(json.loads(b),data.sha(b)) for b in lines}
    expected=[([3554,3555],(.75,2,4),'WBS-P018-03.02'),([3556,3557],(.75,2,4),'WBS-P018-03.02'),([3558,3559],(.75,2.5,5),'WBS-P018-04.02'),([3560,3561],(.75,2,4),'WBS-F03'),([3562,3563],(.75,2,4),'WBS-F03'),([3564],(1.5,4,8),'WBS-F03')]
    assert p['actualExit']==0 and p['source']==SOURCE and len(p['corrections'])==6
    for row,(ids,values,leaf) in zip(p['corrections'],expected,strict=True):
        names=['PGPT-20261008-'+str(n) for n in ids]
        cost=dict(zip(['low','base','high'],values))
        event=events[row['eventId']][0]
        assert row['correctionOfEventIds']==event['correctionOfEventIds']==names
        assert row['originalGroupEstimatePp']==event['estimateAtGroupStartPp']==cost
        assert event['wbsLeafIds']==row['measurementLeafIds']==[leaf]
        assert event['leafAcceptedByCorrection'] is False and event['referenceAdditionalBudgetPp']==0
        assert all(events[n][1]==row['originalEventRowSha256'][n] for n in names)
        first=events[names[0]][0]
        assert first['startEstimatePp']==dict(zip(['low','standard','high'],values))
        assert event['source']==first['source']==SOURCE and event['groupId']==first['groupId']
        assert data.sha((data.ROOT/row['originalSpecPath']).read_bytes())==row['originalSpecSha256']
        assert event['actualAllocatedPp'] is event['N'] is event['T'] is None
        assert event['productTestsReexecuted']==0 and event['technicalProgressAddedByCorrection'] is False
    late=events[p['corrections'][2]['eventId']][0]
    assert late['captureStatus']=='LATE_CAPTURE_AFTER_ORIGINAL_PT_NOT_A_PREEXECUTION_EVENT'
    before=events[p['corrections'][-1]['eventId']][0]
    raw=data.read_checked(data.BASE/'PG16926-original-start-client-seventeen-pt-v1/manifest.json','3accdf1a31ffd7d711e0bcc2464b9c43ab0c8974e4379479c3ee25278e9d5241')
    # Current raw command is a later, separately started operation, not a replay by correction.
    starts=[v.get('startUTC') for v in raw['stages']]
    assert before['current17StillNotExecuted'] is True and all(starts)
    verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,correctionManifestSha256='228ecac632d7a72cded5df9e7feb39b16eda4b3341b411e0f6edce9a23862f99',sixGroupsChecked=6,originalRowsChecked=11,allOriginalRowsUnchanged=True,allFrozenCostsUnchanged=True,lateCaptureNotRewritten=True,leafAcceptanceAdded=False,productTestsExecuted=0,formalUpdated=False,newAccepted=0,actualAllocatedPp=None,N=None,T=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
