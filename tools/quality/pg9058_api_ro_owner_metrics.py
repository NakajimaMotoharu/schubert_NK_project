"""Bounded dependency audit only; no test/Main/acceptance increment or cost reassignment."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9058-api-ro-owner-metrics-v1'
GROUP='P01809_API_RO_OWNER_DEPENDENCY_V1'
SOURCE='2ed81b14bb41512e1cda720a446ed7b261121605'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    rows=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in rows)
    proof=bind([(BASE/'PG9056-api-ro-owner-dependency-v1/manifest.json','b91eee75c854969089f1a183cb4d1ea614c067c421879b3d3f744f98f2227869')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,workCategory='CONTRACT_AUDIT',
      groupStartEstimatePp=dict(low=0.5,base=2,high=4),groupCapPp=10,
      quotaBefore=dict(usedPercent=53,remainingPercent=47,resetsAt=1793382075),quotaAfter=dict(usedPercent=53,remainingPercent=47,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T21:28:53+00:00',sameQuotaWindow=True,observedSharedPp=0,roundedZeroNotExclusiveZero=True,
      priorGroupToStartSharedBoundaryPp=1,boundaryPpNotAllocatedToEitherGroup=True,
      attemptResult='THIRTEEN_PUBLIC_ARTIFACTS_SIX_DEPENDENCIES_BOUND; NEXT_FINITE_RO_CONNECTION_OWNER_PG_PT',
      technicalMeasurementDelta=dict(artifacts=13,dependencyRows=6,newTestIds=0,newMain=0,formalAccepted=0,coverage=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1857_APIReadOnly観測owner_限定依存照合結果.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,originalOrV4V5EstimateChanged=False,
      pgptAllComplete=False,stopReason=None,nextCommand='9060 scan/commit-push; finite RO observation attempt with retaining policy and own-double phase fault tests'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,newTests=0,newMain=0,newAccepted=0,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))


if __name__=='__main__':main()
