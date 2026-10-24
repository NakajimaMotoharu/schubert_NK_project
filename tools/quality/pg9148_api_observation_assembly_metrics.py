"""Bounded dependency audit only; no test/Main/acceptance increment or cost reassignment."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9148-api-observation-assembly-metrics-v1'
GROUP='P01809_API_OBSERVATION_ASSEMBLY_DEPENDENCIES_V1'
SOURCE='fdc229c9a7b7759cea106d1126c8da0f27a70e09'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    rows=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in rows)
    proof=bind([(BASE/'PG9146-api-observation-assembly-dependencies-v1/manifest.json','54da1b50b7852aa1b583862782e4c5f85c98eaa36a4f31295373d496abf3a58b')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,workCategory='CONTRACT_AUDIT',
      groupStartEstimatePp=dict(low=0.5,base=2,high=4),groupCapPp=10,
      quotaBefore=dict(usedPercent=56,remainingPercent=44,resetsAt=1793382075),quotaAfter=dict(usedPercent=56,remainingPercent=44,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T23:05:23+00:00',sameQuotaWindow=True,observedSharedPp=0,roundedZeroNotExclusiveZero=True,
      priorGroupToStartSharedBoundaryPp=0,boundaryPpNotAllocatedToEitherGroup=True,
      attemptResult='TWELVE_PUBLIC_ARTIFACTS_FOUR_DEPENDENCIES_BOUND; EXPLICIT_STOP_REMAINDER_PORT_ASSEMBLY_PG_PT; REAL_MAIN_HOLD',
      technicalMeasurementDelta=dict(artifacts=12,dependencyRows=4,metadataCounterexamples=6,newTestIds=0,newMain=0,formalAccepted=0,coverage=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1867_APIObservationAssembly_必要依存結果.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,originalOrV4V5EstimateChanged=False,
      pgptAllComplete=False,stopReason=None,nextCommand='9150 scan/commit-push; caller-held observation context assembly with existing remaining budget and fake ports'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,newTests=0,newMain=0,newAccepted=0,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))


if __name__=='__main__':main()
