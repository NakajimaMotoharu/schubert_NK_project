"""Close measured trace-only group once; never turn metadata into product PT or effort."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def run(library,group,out,scan_out,before,values,pins):
    invocation=capture(library);assert not out.exists() and not scan_out.exists()
    events=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    starts=[row for row in events if row['groupId']==group and row['eventType']=='GROUP_START']
    assert len(starts)==1 and not any(row['groupId']==group and row.get('groupBoundary')=='END' for row in events)
    start=starts[0]
    assert values['groupStartEstimatePp']==start['groupStartEstimatePp'] and values['quotaBefore']==start['quotaBefore']
    assert values['groupCapPp']==start['groupCapPp']==10
    assert values['technicalMeasurementDelta']['productTestsExecuted']==values['technicalMeasurementDelta']['formalAccepted']==0
    assert values['technicalMeasurementDelta']['coverage'] is None
    proofs=bind([(BASE/path,digest) for path,digest in pins],SOURCE)
    verify(invocation)
    event=metrics.append(group,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,sourceBefore=SOURCE,
      workCategory='CONTRACT_AUDIT',sourceProofs=proofs,stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',
      oldCumulativeStopAndLargeGroupPolicyApplied=False,actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      pgptAllComplete=False,stopReason=None,**values))
    out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=event,invocation=invocation,newSourceOwnerCandidates=values['technicalMeasurementDelta']['newSourceOwnerCandidates'],
          productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False,wholeWbsAuditAccepted=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event)))
    scan.BEFORE=before;scan.OUT=scan_out;scan.main()
