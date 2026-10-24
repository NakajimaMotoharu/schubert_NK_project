"""Record worker44 once; defects, rework and metadata/compiler canaries are not extra product PT."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9140-api-observation-worker-metrics-v1'
GROUP='P01809_API_OBSERVATION_OWNED_WORKER_V1'
SOURCE='fdc229c9a7b7759cea106d1126c8da0f27a70e09'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9136-api-observation-worker-post-v1/manifest.json','24632ab8560ae2cf33785fff6868987375fb6e8d2a1de4e9cd8e7a9fdf0b3a12'),
      (BASE/'PG9138-api-observation-worker-trace-v1/manifest.json','68dd79441376d60e705e0856e3e0077c59a40f7f76c6d9cace1b0e5045c10d37')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==244
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-09',source=SOURCE,sourceBefore='f82e3e1ee6d6090b1b81222d18fd35366d0637c1',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=4,base=7,high=10),groupCapPp=10,
      quotaBefore=dict(usedPercent=55,remainingPercent=45,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=56,remainingPercent=44,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T22:57:24+00:00',sameQuotaWindow=True,observedSharedPp=1,
      attemptResult='CURRENT44_F0_E0_S0; WHOLE_ONE_MAIN_FOUR100; CS_SB0; RAW_PMD20_INDIVIDUAL; ACTUAL_NATIVE_UNRUN_HOLD',
      technicalMeasurementDelta=dict(newTestIds=44,necessaryRegressionTests=0,currentSourceSelectedTests=44,newMain=1,
        physicalMain=1841,sourceOwners=244,scopedCoverage=dict(LINE=87,METHOD=7,CLASS=1,BRANCH=46,missed=0),
        rawPmd=20,reviewedPmd=20,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_CALLER_OWNED_OBSERVATION_WORKER_FINITE_ORIGINAL_STOP_BUDGET',componentOnly=True,actualCallerConnected=False),
      additionalDiscoveries=dict(bugs=['BUG-1732','BUG-1733','BUG-1734','BUG-1735'],ykt=['YKT-1483','YKT-1484','YKT-1485','YKT-1486'],limitedScopeClosed=True),
      productRework=dict(normalSources=4,normalFailed=1,selectedSources=2,totalSelectedExecutions=88,incrementalTestIdsOnly=44,
        correctedOracleIds=['OBSOWN025'],addedVectorWithinExistingId='OBSOWN042',other42CasesAndCommonFixtureUnchanged=True),
      toolRepair=dict(original9137FailedBeforeChild=True,newVersionPreserved=True,compilerCanaries=3,independentArithmeticVectors=6,metadataCounterexamples=12,productTests=0),
      outsideGroupQuotaBoundary=dict(before=54,after=55,allocatedToThisOrPriorGroup=False),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1865_APIObservationOwnedWorker_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['abe482072991dc539c794574d7449ac4f9abf34a9b0fe307514d841572c2de80'],
      pgptAllComplete=False,stopReason=None,nextCommand='9142 public delta/commit-push; same-API caller/Pool/SDK/original stop budget dependency and permitted assembly PG/PT'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=244)))

if __name__=='__main__':main()
