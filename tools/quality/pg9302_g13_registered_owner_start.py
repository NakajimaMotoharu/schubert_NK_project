"""Freeze a bounded metadata-only registry denominator audit, not trace acceptance."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9302-g13-registered-owner-start-v1'
GROUP='G13_CURRENT_JAVA_REGISTERED_OWNER_GAP_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    rows=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP for row in rows)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_START',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],
      source='64446a9f8901084a4ad7eba1f66ae975eb2bbdea',workCategory='CONTRACT_AUDIT',
      groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),quotaObservedAtUTC='2026-10-25T02:31:19Z',
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,
        capturedLowerBoundPp=87,unknownIntervalPp=2,cumulativeExactPp=None,cap=90,
        preservationReservePp=2,reserveIsMeasurement=False,rebased=False,newLargeGroupsSuppressed=True),
      plannedOutcome='NORMAL_INPUT_JAVA_DENOMINATOR_VS_GIT_TREE; ORIGINAL941_PLUS_REVIEWED256_REGISTRY_GAPS_ONLY',
      excludedOperations=['VM','ROOT','DB','KEY','NATIVE','BUILD','JUNIT','DEPLOYMENT','OWNERSHIP_INFERENCE'],
      expectedEvidence='1893 + PG9304 original + PG9305 independent post; not whole G13 or method trace acceptance',
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      toolConstructionAndEnvironmentRework=dict(guessedToolPathDiagnostic=1,exclusivePp=None)))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,eventId=identifier,invocation=invocation,source='64446a9f8901084a4ad7eba1f66ae975eb2bbdea',
          newAccepted=0,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))

if __name__=='__main__':main()
