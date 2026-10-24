"""Record ancestor-hash classification and tool rework without changing product/acceptance totals."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG8994-g07-ancestor-metrics-v1'
GROUP='G07_ANCESTOR_PUBLIC_BLOB_PROVENANCE_V1'
SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG8990-public-ancestor-provenance-v1/manifest.json','23ce1b56dffe743048e2c5fd07fc09c94e026c947c2711487420dcfdb8732be6'),
                 (BASE/'PG8993-public-ancestor-provenance-post-v2/manifest.json','a637cdaaab67a215611a5695a6103562ee942ec13cd54ae0129b037d90b471c5')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G07',source=SOURCE,workCategory='REVIEW',
       groupStartEstimatePp={'low':1,'base':3,'high':6},groupCapPp=10,
       quotaBefore={'usedPercent':49,'remainingPercent':51,'resetsAt':1793382075},
       quotaAfter={'usedPercent':50,'remainingPercent':50,'resetsAt':1793382075},
       quotaAfterObservedAtUTC='2026-10-24T19:35:35+00:00',sameQuotaWindow=True,observedSharedPp=1,
       attemptResult='ADDITIONAL658_PUBLIC_BLOB_PROOF; RESIDUAL9960; INITIAL_POST1_PRESERVED_COUNTER_FIXED',
       technicalMeasurementDelta={'additionalFalsePositivePublicBlobProof':658,'cumulativeFalsePositiveProof':30126,'unclassified':9960,'newTestIds':0,'newMain':0,'newAccepted':0},
       workNature='ADDITIONAL_DISCOVERY_WITH_TOOL_REWORK_NOT_ORIGINAL_PLAN_COMPLETION',
       rework={'kind':'TOOL_COUNTING_DEFECT','failure':'PG8992_EXIT1','corrected':'PG8993_EXIT0','productRerun':False,'exclusiveCostPp':None},
       failureIds=['BUG-1727','YKT-1478'],sourceProofs=proofs,
       sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1847_G07残検出_公開履歴hash照合結果.md'],
       productTestsExecuted=0,actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
       tokenMeasurementIds=['2631beccc7335e7fa9bec3fe20d5aad1fd4e36b0509b4e701ac62a47142b6160'],
       pgptAllComplete=False,stopReason=None,nextCommand='8996 public delta/commit-push; select scoped derived-public-token or C07 permitted PG/PT'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))


if __name__=='__main__':main()
