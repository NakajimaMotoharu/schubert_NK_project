"""Persist limited trace group cost and public delta; not formal PGPT acceptance."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9382-inherited-companion-metrics-v1'
GROUP='G13_INHERITED_COMPANION2_INTERFACE_V1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9374-inherited-companion-join-v1/manifest.json','0f2cfc89eb1750dd6a6ba220a721554ee6388c5441aec6775e40028b5dd0d0aa'),
      (BASE/'PG9376-inherited-companion-post-v1/manifest.json','bc6547634bd4b3ac7e5f121ad887b1f7258499878353ede6e237d2d908e2aa7e'),
      (BASE/'PG9378-inherited-companion-snapshot-post-v1/manifest.json','e5f2b493816d2e68cdf9d34ff38963dccb923ed25c74481dee2737415436bcbd')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.25,base=1,high=3),groupCapPp=10,
      quotaBefore=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),quotaAfter=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-25T04:41:23Z',sameQuotaWindow=True,observedSharedPp=0,
      stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',oldCumulativeStopAndLargeGroupPolicyApplied=False,
      attemptResult='TWO_LITERAL_INTERFACE_SOURCE_RESPONSIBILITIES_REGISTERED; NO_TARGET_COMPILE_OR_RUNTIME; REMAIN338',
      technicalMeasurementDelta=dict(newSourceOwnerCandidates=2,sourceRows=626,javaPaths=1789,registered=1451,
        registeredMain=965,totalMain=965,registeredTest=486,totalTest=824,unregisteredTest=338,
        metadataCounterexamples=6,neighbourInvariance=2,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='EXACT_TWO_INTERFACE_FIXTURE_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[],wholeWbsCurrentScopeHold=True),sourceReauthentication=dict(old624CanonicalPreserved=True,oldSourceResultsTransferred=False),
      toolConstructionAndEnvironmentRework=dict(javapDeclarationReadOnly=2,targetRuntimeInvocation=0,preparationPathFailures=2,producerRetries=0,exclusivePp=None),
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1907_G13InheritedCompanion_明示interface二件結果.md'],
      tokenMeasurementIds=['77cccc453dd6e46cc75395c370f4a3df4f50d6428434dce0d6927739aaec1bdd'],actualAllocatedPp=None,tokenTotals=None,
      effortCompletionRate=None,pgptAllComplete=False,stopReason=None,nextCommand='public scan/save-push; remaining293 composite/45helper independent source responsibility then permitted PG/PT'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,newSourceOwnerCandidates=2,
          productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeWbsAuditAccepted=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))
    scan.BEFORE='1964de28d0ec7dd5900c2a6527104a9c2f631ab1';scan.OUT=BASE/'PG9384-inherited-companion-public-delta-v1';scan.main()

if __name__=='__main__':main()
