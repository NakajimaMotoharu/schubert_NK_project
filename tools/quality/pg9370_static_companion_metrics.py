"""Static compilation/reference evidence is not executed production PT or global quality."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9370-static-companion-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_STATIC_COMPANION55_BYTECODE_V1'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9358-static-companion-compile55-v1/manifest.json','1e6283063e08ae26c4abe5b9cd2d4eb4fce69a45365c4aae14b996641f61d751'),
      (BASE/'PG9360-static-companion-javap-v1/manifest.json','a6cc01273a2d12b966524fdf7366ec90f9650d4826b5fcffc944cb1e115a65b6'),
      (BASE/'PG9362-static-companion-asm-v1/manifest.json','5a98abbe4cf6ddbaf7259b72c6b68996e46f5feaeaaba51455756f5d1d53ff37'),
      (BASE/'PG9364-static-companion-owner-join-v1/manifest.json','5f7b552fb08fb96e388232952ab88ac61d70a581176c1e63400b405da864cbbb'),
      (BASE/'PG9366-static-companion-owner-post-v1/manifest.json','163360ae9e8819fb7566c094df9333893316f480a0377e0f444c2c6ae0bf4295'),
      (BASE/'PG9368-static-companion-snapshot-post-v1/manifest.json','03a970c0a502993cfd3f8b1dda15ff19947d1b5c457f1418e19bd7f04c9cbbdc')],SOURCE)
    quota=json.loads((BASE/'PG9364-static-companion-owner-join-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==65 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=1,base=3,high=6),groupCapPp=10,
      quotaBefore=dict(usedPercent=64,remainingPercent=36,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=1,stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',oldCumulativeStopAndLargeGroupPolicyApplied=False,
      attemptResult='FRESH_STATIC_SOURCE55_CLASS96_ASM_JAVAP_REFERENCE55_REGISTERED; RUNTIME_PT0; REMAIN340',
      technicalMeasurementDelta=dict(staticallyCompiledTestSources=55,freshTestClasses=96,newSourceOwnerCandidates=55,
        asmLiteralVectors=10,javapMetadataVectors=9,ownerMetadataNegatives=6,neighbourInvariance=55,snapshotMetadataNegatives=6,
        sourceRows=624,javaPaths=1789,registered=1449,registeredMain=965,totalMain=965,registeredTest=484,totalTest=824,
        unregisteredTest=340,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='EXACT_STATIC_REFERENCE55_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[],compilerPluginServices=0,productionMainOutputShadows=0,fullWbsCurrentScopeHoldMaintained=True),
      sourceReauthentication=dict(productionInputsUnchanged=True,old569CanonicalAndOriginal941943Preserved=True,oldSourceResultsTransferred=False),
      toolConstructionAndEnvironmentRework=dict(targetTestStaticCompileOnly=True,targetRuntimeClassLoading=0,targetRuntimeInvocation=0,
        rawDisassemblyPublished=False,retries=0,exclusivePp=None),sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1905_G13StaticCompanion_55件compile・二種参照結果.md'],
      tokenMeasurementIds=['7f097456a83bab4210963e2ceb7feee1be171a723b2de043345cf60f0b0ea947'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9372 public delta/save-push; fresh remaining>10 then inherited2 or unmatched293/helper45 source responsibility; independent PG/PT continues'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,newSourceOwnerCandidates=55,
          productTestsExecuted=0,wholeWbsAuditAccepted=False,wholeG13Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,newOwnerCandidates=55)))

if __name__=='__main__':main()
