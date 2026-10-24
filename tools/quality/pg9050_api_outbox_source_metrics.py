"""Record cache new20/necessary16, tool-construction/invocation costs separate from product PT."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9050-api-outbox-source-metrics-v1'
GROUP='P01809_API_OUTBOX_OBSERVATION_SOURCE_V1'
SOURCE='2ed81b14bb41512e1cda720a446ed7b261121605'


def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9046-api-outbox-source-post-v1/manifest.json','d188fc8a7b0261a0e187d2aeda5f56af783db22f1b7fdcb4f6525685c6d69f14'),
      (BASE/'PG9048-api-outbox-source-trace-v1/manifest.json','9674bdaea983763fa6c5615ee747657f8bed9cebeeb0a91a0f36ce114ef44ed3')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==237
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,sourceBefore='73d94fc525c6ea8828ca82d906ec583146fee7bf',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=2,base=5,high=9),groupCapPp=10,
      quotaBefore=dict(usedPercent=52,remainingPercent=48,resetsAt=1793382075),quotaAfter=dict(usedPercent=52,remainingPercent=48,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T21:20:51+00:00',sameQuotaWindow=True,observedSharedPp=0,roundedZeroNotExclusiveZero=True,
      attemptResult='ACTUAL36_F0_E0_S0_NEW20_NECESSARY16; TWO_MAIN_FOUR100_WITH_REAL_BRANCHLESS_ENTRY; LIVE_PRODUCER_UNSUPPLIED_HOLD',
      technicalMeasurementDelta=dict(newTestIds=20,necessaryRegressionTests=16,actualSelectedTests=36,newMain=2,physicalMain=1838,sourceOwners=237,
        scopedCoverage=dict(LINE=25,METHOD=5,CLASS=2,BRANCH=7,missed=0),rawPmd=1,reviewedPrivateLock=1,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_SDK_INDEPENDENT_RO_OBSERVATION_CACHE_INVALIDATION_FENCE',componentOnly=True,liveProducerSupplied=False),
      toolConstructionAndInvocationRework=dict(importEnvironmentBeforeJob=1,syntaxPreflightBeforeAnalysis=2,productTestsRerun=0,exclusivePp=None),
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1855_APIOutboxObservationSource_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,tokenMeasurementIds=['a6edc9f33f5ccc739b4a03cf0015b8e1a858e7b282d23cd104686debb96e6d55'],
      pgptAllComplete=False,stopReason=None,nextCommand='9052 public scan/commit-push; bounded approved-source-only RO producer dependency audit before permitted PG/PT'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=237)))


if __name__=='__main__':main()
