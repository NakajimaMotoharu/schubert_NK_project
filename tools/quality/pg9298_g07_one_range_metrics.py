"""One public range proof, zero false-positive or formal acceptance increment."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9298-g07-one-range-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G07_ONE_RANGE_PUBLIC_DIAGNOSIS_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    rows=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in rows)
    proof=bind([
      (BASE/'PG9296-g07-one-range-diagnosis-v1/manifest.json','e1de541969ec807893a234c5a4e3fd23f74c4bf162728ab1c5582b68682615cf'),
      (BASE/'PG9297-g07-one-range-post-v1/manifest.json','884500a8231d88a2aa7bb08e3d4874c570a7b2e9d6d5cf703d816e210f9a8bbe')],SOURCE)
    quota=json.loads((BASE/'PG9294-g07-one-range-start-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==62 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-G07',wbsLeafIds=['WBS-G07'],source=SOURCE,sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',
      groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=61,remainingPercent=39,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=1,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,
        capturedLowerBoundPp=87,unknownIntervalPp=2,cumulativeExactPp=None,cap=90,rebased=False,newLargeGroupsSuppressed=True),
      attemptResult='ONE_PUBLIC_SOURCE_HASH_LINE_PROVED; ACTUAL_CAPTURE_NOT_RECONSTRUCTED; ADDITIONAL_FP0; UNCLASSIFIED8379',
      technicalMeasurementDelta=dict(publicMetadataRangeProof=1,selectedVendorRulesReauthenticated=2,
        additionalFalsePositives=0,remainingUnclassified=8379,actualSecretCount=None,
        actualCaptureReconstructed=False,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      historicalSubject=dict(contentCommit='05d73a7974da8df92228160b96d91e7a006768f3',
        scanSource='fb9fce0f91de3d9fdfa634fe277592700f915e45',notCurrentSourceSecretGate=True),
      originalPlanEngineeringDelta=dict(item='ONE_EXISTING_CAPTURE_RANGE_PROVENANCE_DIAGNOSIS',diagnosisOnly=True,wholeG07Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[],actualFragmentBoundaryStillUnknown=True),
      sourceReauthentication=dict(knownPublicSnapshotAndSourceBlobOnly=True,oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(syntheticRegexVectors=4,metadataCounterexamples=8,
        binaryHelpMetadataCalls=1,dataScannerCalls=0,publicDirectoryFetchUnavailable=True,retryOrAlternativeChannel=False,
        guessedPlanPathDiagnostic=1,exclusivePp=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1891_G07OneRange_限定診断結果・capture未確定.md'],
      tokenMeasurementIds=['8f25f8597b2ce39f3e5ffcf9887cefd0aaaab8425952e39c97b856af5f0fcab3'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9300 public delta/commit-push; bounded current source path-owner gap count only if lower+cap+reserve2<=90; no scanner or actual operations'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,additionalFalsePositives=0,
          remainingUnclassified=8379,whole451Accepted=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,publicRangeProof=1,additionalFalsePositives=0)))

if __name__=='__main__':main()
