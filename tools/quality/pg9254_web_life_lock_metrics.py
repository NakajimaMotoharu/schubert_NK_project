"""New10 selected-method success, whole-Life incomplete; original90 and exact unclassified rows kept."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9254-web-life-lock-metrics-v1'
GROUP='P01806_WEB_LIFE_LOCK_REMEDY_V1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9250-web-life-lock-measure-v1/manifest.json','54fc9529a931f5a7c73802ba7818a5946e3821d24aa9afafafcc202e33227667'),
      (BASE/'PG9252-web-life-lock-trace-v1/manifest.json','70f008f4256751e5bf4ecc0baa9e398dc715643cbbff8eb1380927fbfb7d49b6')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==254
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-06',wbsLeafIds=['WBS-P018-06'],source=SOURCE,
      sourceBefore='600b966bab415690bf09d24ba07268a097b19d18',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=.5,base=1,high=2),groupCapPp=2,
      quotaBefore=dict(usedPercent=60,remainingPercent=40,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=60,remainingPercent=40,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-25T01:24:34+00:00',sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,cap=90,
        capturedLowerBoundPp=85,previousCapturedLowerBound=85,sameWindowEndpoint60To60Pp=0,
        unknownIntervalPp=2,cumulativeExactPp=None,newLargeGroupsSuppressed=True,rebased=False),
      attemptResult='NEW1_PLUS_IMPACT3_F0_E0_S0; WEB_STATIC_TARGETS_REMOVED_RAW8_REVIEWED; WHOLE_WEB_NOT100_HOLD',
      technicalMeasurementDelta=dict(newTestIds=1,necessaryRegressionTests=3,currentSourceSelectedTests=4,currentSuites=1,newMain=0,
        changedSourceUnits=1,changedPhysicalClasses=1,physicalMain=1843,sourceOwners=254,
        wholeSourceUnitCounters=dict(LINE=dict(covered=30,missed=28),METHOD=dict(covered=7,missed=3),
          CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=6,missed=8)),
        requiredWholeClassFour100=False,programPtComplete=False,rawPmd=8,reviewedPmd=8,unclassifiedPmd=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='WEB_PRIVATE_LOCK_AND_INTERVAL_TERMINAL_REPRESENTATION',componentOnly=True,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=['BUG-1743'],ykt=['YKT-1493','YKT-1494'],targetedStaticFindingsRemoved=3,
        ledgerState='STATIC_FIXED_PT_HOLD',actualUnknownIntervalExecuted=False),
      productRework=dict(normalSources=1,normalFailures=0,selectedSources=1,totalSelectedExecutions=4),
      toolConstructionAndEnvironmentRework=dict(productTestsRerunForConfirmation=0,exclusivePp=None),
      priorQuotaTimestampPrecisionCorrection=dict(targetEvent='PGPT-20261008-2113',field='quotaAfterObservedAtUTC',
        originalReported='2026-10-25T01:17:00+00:00',exactValue=None,precision='MANUAL_MINUTE_BUCKET_NOT_API_TIMESTAMP',
        observedEndpointUsed60AndShared1Unchanged=True,originalEventPreserved=True,additionalSharedCostPp=0),
      relatedWbs='WBS-P018-05',componentAdditionalBudgetPp=0,
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1883_WebLifeLock_限定是正結果・残実行.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['2e2b0c048d1655bc5e61f8b3b462d93a5169b42d16b74e78d446229e9d822552'],
      pgptAllComplete=False,stopReason=None,
      nextCommand='9256 public delta/commit-push; bounded permitted quality or ordinary PT within original90; all actual operations HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,
          logical941AndHistorical943Unchanged=True,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=254,programPtComplete=False)))

if __name__=='__main__':main()
