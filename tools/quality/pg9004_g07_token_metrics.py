"""Record pure public token provenance separately from product PT and original plan completion."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9004-g07-token-metrics-v1'
GROUP='G07_PUBLIC_TOKEN_DIGEST_PROVENANCE_V1'
SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9000-public-token-provenance-v1/manifest.json','c3216ab47b1ebe8a9da9c6587b1784b99b89a46390e1f0c61c80154dcc9f1847'),
                 (BASE/'PG9002-public-token-provenance-post-v1/manifest.json','3af5c448f053d77bac336122f4f7372e7bffa41aacea24052456f07c06f7a177')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G07',source=SOURCE,workCategory='REVIEW',
       groupStartEstimatePp={'low':0.5,'base':2,'high':4},groupCapPp=10,
       quotaBefore={'usedPercent':50,'remainingPercent':50,'resetsAt':1793382075},
       quotaAfter={'usedPercent':50,'remainingPercent':50,'resetsAt':1793382075},
       quotaAfterObservedAtUTC='2026-10-24T19:43:36+00:00',sameQuotaWindow=True,observedSharedPp=0,
       attemptResult='ADDITIONAL1581_PUBLIC_JAVA_TOKEN_PROOF; RESIDUAL8379; G07_UNACCEPTED',
       technicalMeasurementDelta={'additionalFalsePositiveProof':1581,'cumulativeFalsePositiveProof':31707,'unclassified':8379,'newTestIds':0,'newMain':0,'newAccepted':0},
       workNature='ADDITIONAL_DISCOVERY_PUBLIC_TRANSFORM_PROOF_NOT_ORIGINAL_PLAN_COMPLETION',
       sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1849_G07公開tokenDigest_残検出分類結果.md'],
       failureIds=[],productTestsExecuted=0,actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
       tokenMeasurementIds=['e2f4d70650866cff5b2bf8952447085d2eca52fb42374a701f5e8dafd730f1ea'],
       pgptAllComplete=False,stopReason=None,nextCommand='9006 public scan/commit-push; inspect current C01 format gap and permit-only source/static/unit path'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))


if __name__=='__main__':main()
