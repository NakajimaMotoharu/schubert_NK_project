"""One new32/one Main engineering delta, three-source96 executions and static rework separated."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9098-api-ro-attempt-metrics-v1'
GROUP='P01809_API_RO_OBSERVATION_ATTEMPT_V1'
SOURCE='e87ab6ec893fa461dc98e6525e6bbc9885701f32'


def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([(BASE/'PG9094-api-ro-attempt-union-post-v1/manifest.json','0f882a2d3866a07ae2751e2e9e339753b2c000221e005d2bc48e6c39ba552553'),
      (BASE/'PG9096-api-ro-attempt-union-trace-v1/manifest.json','287a0941eac016178e2e46b4fc4fe8f60dbfa39d9b8e6087c1169564d809a41b')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==239
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,sourceBefore='2ed81b14bb41512e1cda720a446ed7b261121605',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=3,base=6,high=10),groupCapPp=10,
      quotaBefore=dict(usedPercent=53,remainingPercent=47,resetsAt=1793382075),quotaAfter=dict(usedPercent=53,remainingPercent=47,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T21:49:11+00:00',sameQuotaWindow=True,observedSharedPp=0,roundedZeroNotExclusiveZero=True,
      attemptResult='CURRENT32_F0_E0_S0; WHOLE_ONE_MAIN_FOUR100; CS_SB0; RAW_PMD14_INDIVIDUAL_OWNER_CONTRACT; ACTUAL_NATIVE_UNRUN_HOLD',
      technicalMeasurementDelta=dict(newTestIds=32,currentSourceSelectedTests=32,necessaryRegressionTests=0,newMain=1,physicalMain=1839,sourceOwners=239,
        scopedCoverage=dict(LINE=61,METHOD=5,CLASS=1,BRANCH=16,missed=0),rawPmd=14,reviewedPmd=14,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_ONE_SHOT_RO_OBSERVATION_CONNECTION_OWNER',componentOnly=True,cachePublicationOrWorkerSupplied=False),
      rework=dict(bug='BUG-1731',ykt='YKT-1482',normalSourceBuilds=4,selectedSources=3,totalSelectedExecutions=96,incrementalTestIdsOnly=32,
        staticFailedSources=2,originalUnqualifiedSourcesPreserved=True,intermediateAfTests='UNRUN',normalConfirmationOnlyReplays=0,exclusivePp=None),
      toolConstructionRework=dict(unusedImportPreflight=1,childNotStarted=True),sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1859_APIReadOnlyObservationAttempt_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,tokenMeasurementIds=['9fbfadae3894ab54a9909f6165ceb0ab5d7e0c4a41655cb003ab84743fd46ee8','cfe3bc156abc7f6efe8b55d87c5fc70f31d5a4cac8a3a9e19f030a712ca65117'],
      pgptAllComplete=False,stopReason=None,nextCommand='9100 public scan/commit-push; cleanup-confirmed attempt result to cache publication fence PG/PT'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=239)))


if __name__=='__main__':main()
