"""Dual-parser source registry work and auxiliary tool validation are not production PT."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9354-direct-companion-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_DIRECT_COMPANION_STATIC_AST_V1'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9344-direct-companion-ast-v1/manifest.json','6a8bea332ad27bccd567949395166f4cef2334bc9770063c3a7ed0d0f405c5d0'),
      (BASE/'PG9346-direct-companion-jdk-post-v1/manifest.json','5858a76efb999092d1dfe0471f797c61b2260482fa271908555ca186f2dd9879'),
      (BASE/'PG9348-direct-companion-owner-join-v1/manifest.json','fa2817d4f7b37d4d5cf2325edb2e1dd8b0763276fe0477805147606e86660f20'),
      (BASE/'PG9350-direct-companion-owner-post-v1/manifest.json','31f513e221023e39997830b2508d0770b7ac3f79b16d65b3150f8a562e767b4e'),
      (BASE/'PG9352-direct-companion-snapshot-post-v1/manifest.json','4d2684a37aa1c0baf6f7c09af8f2e2980478190018b46b229a4fc915d196d5b4')],SOURCE)
    quota=json.loads((BASE/'PG9348-direct-companion-owner-join-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==64 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=1,base=3,high=7),groupCapPp=10,
      quotaBefore=dict(usedPercent=63,remainingPercent=37,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=64,remainingPercent=36,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=1,stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',
      oldCumulativeStopAndLargeGroupPolicyApplied=False,
      attemptResult='675_POOL337_PARSED_DUAL_AST280_CONFIRMED_AND_REGISTERED; REMAIN395; NO_PRODUCT_PT_OR_ACCEPTANCE',
      technicalMeasurementDelta=dict(unregisteredBefore=675,parseInputs=337,dualParserConfirmed=280,
        directSourceOwnerCandidatesAdded=280,javaPaths=1789,registered=1394,registeredMain=965,totalMain=965,
        registeredTest=429,totalTest=824,unregisteredAfter=395,sourceRows=569,
        toolFixtureVectorsPrimary=16,toolFixtureVectorsIndependent=13,literalOwnerGolden=4,
        ownerMetadataNegatives=6,neighbourRuleInvariance=280,snapshotMetadataNegatives=6,
        productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='EXACT_COMPANION280_SOURCE_OWNER_TRACE_CANDIDATES',wholeG13Accepted=False),
      additionalDiscoveries=dict(unknownInheritanceScopes=2,bugs=[],ykt=[],wholeWbsCurrentSourceHoldMaintained=True),
      sourceReauthentication=dict(sourceUnchanged=True,old289CanonicalAndOriginal941943Preserved=True,oldSourceResultsTransferred=False),
      toolConstructionAndEnvironmentRework=dict(auxiliaryCompileJavms=2,auxiliaryReaderJvms=2,
        targetClassLoading=0,targetCompilation=0,targetRuntimeActions=0,preflightReadDiagnostics=2,exclusivePp=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1903_G13DirectCompanion_二種AST・所有候補280結果.md'],
      tokenMeasurementIds=['e1122e9642c740aa7aa753a15a475cadf532c34b2cf87a346d49f1f011200788'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9356 public delta/save-push; fresh remaining>10 then static-only companion55 or single-owner composite/source trace; independent PG/PT continues'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,newOwnerCandidates=280,
          productTestsExecuted=0,wholeWbsAuditAccepted=False,wholeG13Accepted=False,whole451Accepted=False,
          formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,newOwnerCandidates=280)))

if __name__=='__main__':main()
