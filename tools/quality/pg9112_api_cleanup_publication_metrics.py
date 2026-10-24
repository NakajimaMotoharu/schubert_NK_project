"""Record cache new20/necessary16, tool-construction/invocation costs separate from product PT."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9112-api-cleanup-publication-metrics-v1'
GROUP='P01809_API_CLEANUP_CONFIRMED_PUBLICATION_V1'
SOURCE='fa29009e4fdc97effb40e441110102caf46f3926'


def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9108-api-cleanup-publication-post-v1/manifest.json','b3f6ed290dd8fc0381cf0a9344b761110b28a33816c3b7db6c53b15b32cd4d7f'),
      (BASE/'PG9110-api-cleanup-publication-trace-v1/manifest.json','0e74d487c28358ab9e5c74645e0dd45be6762f1b76a02294edb3b7ed8a6d5083')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==240
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,sourceBefore='e87ab6ec893fa461dc98e6525e6bbc9885701f32',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=2,base=5,high=9),groupCapPp=10,
      quotaBefore=dict(usedPercent=53,remainingPercent=47,resetsAt=1793382075),quotaAfter=dict(usedPercent=54,remainingPercent=46,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T21:58:49+00:00',sameQuotaWindow=True,observedSharedPp=1,roundedZeroNotExclusiveZero=True,
      attemptResult='ACTUAL34_F0_E0_S0_NEW14_NECESSARY20; TWO_MAIN_FOUR100_WITH_REAL_BRANCHLESS_ENTRY; LIVE_PRODUCER_UNSUPPLIED_HOLD',
      technicalMeasurementDelta=dict(newTestIds=14,necessaryRegressionTests=20,actualSelectedTests=34,newMain=0,physicalMain=1839,sourceOwners=240,
        scopedCoverage=dict(LINE=33,METHOD=6,CLASS=2,BRANCH=11,missed=0),rawPmd=2,reviewedPrivateLock=2,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_CLEANUP_CONFIRMED_ATTEMPT_CACHE_PUBLICATION',componentOnly=True,liveProducerSupplied=False),
      toolConstructionAndInvocationRework=dict(unusedImportPreflight=1,childNotStarted=True,productTestsRerun=0,exclusivePp=None),
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1861_APIOutboxCleanupPublication_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,tokenMeasurementIds=['fe40f67cb9a861832f129c047b7a274d66bee102f5b455da61a204b5d53381b7'],
      pgptAllComplete=False,stopReason=None,nextCommand='9114 public scan/commit-push; bounded owned observation producer PG/PT in same API path'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=240)))


if __name__=='__main__':main()
