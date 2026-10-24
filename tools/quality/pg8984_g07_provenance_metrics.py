"""Freeze classification discovery separately from new implementation/PT/acceptance."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG8984-g07-provenance-metrics-v1'
GROUP='G07_PUBLIC_FINDING_PROVENANCE_V1'
SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG8980-public-finding-provenance-v1/manifest.json','fe4175077735018f5b500306e09c7300917a814c53196a2378e1b1e887b6f5ae'),
                 (BASE/'PG8982-public-finding-provenance-post-v1/manifest.json','c9e5b51a121f70f6359be78735ad0bad93c6094b775979d7d29c50b8b650df55')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G07',source=SOURCE,workCategory='REVIEW',
       groupStartEstimatePp={'low':1,'base':3,'high':6},groupCapPp=10,
       quotaBefore={'usedPercent':49,'remainingPercent':51,'resetsAt':1793382075},
       quotaAfter={'usedPercent':49,'remainingPercent':51,'resetsAt':1793382075},
       quotaAfterObservedAtUTC='2026-10-24T19:25:52+00:00',sameQuotaWindow=True,observedSharedPp=0,
       attemptResult='EXACT_CAPTURE_PUBLIC_BLOB_HASH29468_CLASSIFIED;10618_UNCLASSIFIED; G07_NOT_ACCEPTED',
       technicalMeasurementDelta={'findingsReviewed':40086,'falsePositivePublicBlobProof':29468,'unclassified':10618,'newTestIds':0,'newMain':0,'newAccepted':0},
       workNature='ADDITIONAL_DISCOVERY_CLASSIFICATION_NOT_ORIGINAL_PLAN_COMPLETION_OR_REESTIMATE_REDUCTION',
       sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1845_G07公開検出値_限定分類結果.md'],
       failureIds=[],productTestsExecuted=0,actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
       tokenMeasurementIds=['3a0f55e4d1f0b36d5256a1747d003879f082ed704066fe238edb36d0520fd29b'],
       roundedSharedDeltaIsNotExclusiveZeroCost=True,pgptAllComplete=False,stopReason=None,
       nextCommand='8986 public delta scan/commit/push; select permitted C07 remaining hook or scoped unresolved-provenance work'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))


if __name__=='__main__':main()
