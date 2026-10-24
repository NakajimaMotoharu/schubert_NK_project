"""Record worker44 once; defects, rework and metadata/compiler canaries are not extra product PT."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9162-api-observation-context-metrics-v1'
GROUP='P01809_API_OBSERVATION_CONTEXT_V1'
SOURCE='cb91bc2ec0ef5a36652369aff5c86fa037801cca'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9158-api-observation-context-post-v1/manifest.json','f2729d1e3eb68429dd43494d1ab737bd878dc08e113c963932197a2f6abbd385'),
      (BASE/'PG9160-api-observation-context-trace-v1/manifest.json','33d6811f8d10422d348f404c8269f689295c1e57f0dbd3e033b9e312e61849f1')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==246
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-09',source=SOURCE,sourceBefore='fdc229c9a7b7759cea106d1126c8da0f27a70e09',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=4,base=7,high=10),groupCapPp=10,
      quotaBefore=dict(usedPercent=56,remainingPercent=44,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=57,remainingPercent=43,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T23:22:57+00:00',sameQuotaWindow=True,observedSharedPp=1,
      attemptResult='CURRENT26_F0_E0_S0; WHOLE_ONE_MAIN_FOUR100; CS_SB0; RAW_PMD4_INDIVIDUAL; ACTUAL_NATIVE_UNRUN_HOLD',
      technicalMeasurementDelta=dict(newTestIds=26,necessaryRegressionTests=0,currentSourceSelectedTests=26,newMain=1,
        physicalMain=1842,sourceOwners=246,scopedCoverage=dict(LINE=58,METHOD=7,CLASS=1,BRANCH=20,missed=0),
        rawPmd=4,reviewedPmd=4,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_CALLER_HELD_OBSERVATION_SDK_ASSEMBLY_BORROWED_REMAINING_BUDGET',componentOnly=True,actualCallerConnected=False),
      additionalDiscoveries=dict(bugs=['BUG-1736','BUG-1737','BUG-1738'],ykt=['YKT-1487','YKT-1488','YKT-1489'],limitedScopeClosed=True),
      productRework=dict(normalSources=3,normalFailed=0,selectedSources=3,selectedRuns=4,totalSelectedExecutions=104,incrementalTestIdsOnly=26,
        correctedOracleIds=['OBSCTX016'],other25CasesAndCommonFixtureUnchanged=True,mainCorrection='HELD_FIELD_INTERNAL_RENAME_ONLY'),
      toolRepair=dict(originalLauncherCounts44Not26=True,oldHelperImmutable=True,newHelperExpectedCounts26=True,
        hostV3PreflightRegexFailureBeforeChild=True,staticV2PrerequisiteFailureBeforeChild=True,currentTraceMetadataNegatives=15,extraProductTestIds=0),
      outsideGroupQuotaBoundary=dict(before=56,after=56,allocatedToThisOrPriorGroup=False),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1869_APIObservationContext_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['2e446b3d2f2d6a4d21ed5cab84b65c5b641781ec161df7f580f2886cadffd65e'],
      pgptAllComplete=False,stopReason=None,nextCommand='9164 public delta/commit-push; same-caller original shared stop budget dependency and permitted implementation, actual Main/native HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=246)))

if __name__=='__main__':main()
