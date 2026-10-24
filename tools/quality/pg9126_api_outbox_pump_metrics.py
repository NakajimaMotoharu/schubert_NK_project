"""One new32/one Main engineering delta, three-source96 executions and static rework separated."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9126-api-outbox-pump-metrics-v1'
GROUP='P01809_API_OUTBOX_OBSERVATION_PUMP_V1'
SOURCE='f82e3e1ee6d6090b1b81222d18fd35366d0637c1'


def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([(BASE/'PG9122-api-outbox-pump-post-v1/manifest.json','d1393a7fee14afe4b246823db1268873cbfb30cd2aa8e280534b41738f023edc'),
      (BASE/'PG9124-api-outbox-pump-trace-v1/manifest.json','e24df0881bc6057c9d2e05e68334ee382ceac184b9564722f36ebfb49375d9f7')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==242
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,sourceBefore='fa29009e4fdc97effb40e441110102caf46f3926',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=3,base=6,high=10),groupCapPp=10,
      quotaBefore=dict(usedPercent=54,remainingPercent=46,resetsAt=1793382075),quotaAfter=dict(usedPercent=54,remainingPercent=46,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T22:14:23+00:00',sameQuotaWindow=True,observedSharedPp=0,roundedZeroNotExclusiveZero=True,
      attemptResult='CURRENT32_F0_E0_S0; WHOLE_ONE_MAIN_FOUR100; CS_SB0; RAW_PMD3_INDIVIDUAL_SAMPLER_CONTRACT; ACTUAL_NATIVE_UNRUN_HOLD',
      technicalMeasurementDelta=dict(newTestIds=32,currentSourceSelectedTests=32,necessaryRegressionTests=0,newMain=1,physicalMain=1840,sourceOwners=242,
        scopedCoverage=dict(LINE=50,METHOD=6,CLASS=1,BRANCH=31,missed=0),rawPmd=3,reviewedPmd=3,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_FINITE_SAMPLING_PUMP_STOP_UNKNOWN_GATES',componentOnly=True,workerSupplied=False),
      fixtureCompletionBeforeFirstPt=dict(normalSourceBuilds=2,selectedSources=1,totalSelectedExecutions=32,incrementalTestIdsOnly=32,
        mainBytesUnchangedBetweenDraftAndFixtureCompletion=True,originalDraftTests='UNRUN',exclusivePp=None),
      toolConstructionRework=dict(regexEscapeCorrectedBeforeExecution=True,productTestsRerun=0),sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1863_APIOutboxObservationPump_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,tokenMeasurementIds=['12682bf20ad21441269e82aca2760fa4f81de92906754608800f722e765437d4'],
      pgptAllComplete=False,stopReason=None,nextCommand='9128 public scan/commit-push; caller-owned worker with fake observation port PG/PT, actual API/VM/native HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=242)))


if __name__=='__main__':main()
