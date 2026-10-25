"""Limited structural trace47, tool rework and shared rounded usage remain separate from PT."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9394-composite-group-metrics-v1'
GROUP='G13_COMPOSITE338_REFERENCE_GRAPH_V1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9386-composite-reference-graph-v3/manifest.json','3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'),
      (BASE/'PG9388-composite-reference-post-v1/manifest.json','46d1cf32bc0e7ec1ac5882f43250201eb6d23e72acb4c6ef64cea823d9f1087e'),
      (BASE/'PG9390-composite-owner-join-v1/manifest.json','90b5394c4afd5f9ee468620f9ef593f49ae350969e144d5d0db9b425ee03d602'),
      (BASE/'PG9392-composite-snapshot-post-v1/manifest.json','300a52afae71abeb53844af63e2c6ac5431c9b82da0fb68db1984c8cd50fb3c9')],SOURCE)
    assert json.loads((BASE/'PG9388-composite-reference-post-v1/manifest.json').read_bytes())['verifiedSourceClosure']==48
    verify(invocation)
    event=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,sourceBefore=SOURCE,
      workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=1,base=3,high=7),groupCapPp=10,
      quotaBefore=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),quotaAfter=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),
      quotaBeforeObservedAtUTC='2026-10-25T04:41:23Z',quotaAfterObservedAtUTC='2026-10-25T04:54:07Z',sameQuotaWindow=True,observedSharedPp=0,
      stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',oldCumulativeStopAndLargeGroupPolicyApplied=False,
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1909_G13Composite_47件責任対応・工具是正結果.md'],
      attemptResult='FINITE47_COMPOSITE_SOURCE_RESPONSIBILITIES_VERIFIED_AND_REGISTERED; OTHER291_KEEP_UNREGISTERED',
      failureIds=['BUG-1747','BUG-1748'],retryCause='TOOL_LEGAL_JVM_SYMBOL_AND_NULLABLE_PRIMITIVE_ARRAY_MEMBER; PRIOR_FAILURES_PRESERVED; NO_SECURITY_RETRY',
      originalPlanEngineeringDelta=dict(item='EXACT_REVIEWED47_STRUCTURAL_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
      additionalDiscoveries=dict(toolBugs=['BUG-1747','BUG-1748'],ykt=['YKT-1498','YKT-1499'],unresolvedSourcePaths=291),
      sourceReauthentication=dict(normalMainClasses=1843,normalTestClasses=1910,currentSnapshotInputHashesExact=True,old626CanonicalPreserved=True,oldSourceResultsTransferred=False),
      toolConstructionAndEnvironmentRework=dict(classfileAndGraphVectors=18,postJavapFormatVectors=9,producerAttempts=3,failedAttempts=2,
        preparationPyflakesUnusedVariable=1,originalFailuresSaved=True,targetRuntimeInvocation=0,exclusivePp=None),
      technicalMeasurementDelta=dict(newSourceOwnerCandidates=47,sourceRows=673,javaPaths=1789,registered=1498,registeredMain=965,totalMain=965,
        registeredTest=533,totalTest=824,unregisteredTest=291,independentClassMetadata=73,independentMainSourceFiles=96,
        metadataCounterexamples=6,neighbourInvariance=47,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      tokenMeasurementIds=['f1aa3d1a4433fd61ea5c274a0149b636f18f33cb623b295c34b5133095e8d84f'],tokenTotals=None,actualAllocatedPp=None,
      effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9396 public delta/save-push; remaining291 protocol/manual primary-related source responsibility and independent ordinary PG/PT'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:json.dump(dict(actualExit=0,source=SOURCE,eventId=event,invocation=invocation,newSourceOwnerCandidates=47,
      productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeWbsAuditAccepted=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event)))
    scan.BEFORE='3d0c608f46f4b653a6d5ac9281492ae094bbf55b';scan.OUT=BASE/'PG9396-composite-public-delta-v1';scan.main()

if __name__=='__main__':main()
