"""Preserve G07 scan discovery separately from acceptance, product PT, costs and correction2074."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture, verify
from public_blob_scan import sha
from source_evidence_binding import bind

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG8975-g07-scan-metrics-v1'
GROUP='G07_PUBLIC_TRACKED_BLOB_SCAN_V1'
SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    events=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    assert len([row for row in events if row['groupId']==GROUP and row['eventType']=='GROUP_START'])==1
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    evidence=bind([(BASE/'PG8968-public-blob-scan-v1/manifest.json','f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739'),
                   (BASE/'PG8970-public-blob-scan-post-v1/manifest.json','4f7a18808c15ae412be665921e0673641beb225c53b192f0f3571acc9a7f8f00')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G07',source=SOURCE,
       workCategory='REVIEW',groupStartEstimatePp={'low':2,'base':4,'high':8},groupCapPp=10,
       quotaBefore={'usedPercent':49,'remainingPercent':51,'resetsAt':1793382075},
       quotaAfter={'usedPercent':49,'remainingPercent':51,'resetsAt':1793382075},
       quotaAfterObservedAtUTC='2026-10-24T19:19:13+00:00',sameQuotaWindow=True,observedSharedPp=0,
       attemptResult='FIXED55722_BLOBS_SCAN_COMPLETED; FINDINGS40086_UNCLASSIFIED; LIMITED22; G07_NOT_ACCEPTED',
       technicalMeasurementDelta={'publicBlobsScanned':55722,'bytes':1282356740,'findingsUnclassified':40086,
                                  'binaryOrContainerLimited':22,'newTestIds':0,'newMain':0,'newAccepted':0},
       discoveredWork={'kind':'ADDITIONAL_DISCOVERY','item':'G07_FINDING_PROVENANCE_CLASSIFICATION','count':40086,'remainingCostPp':None},
       productTestsExecuted=0,formalRunDelta=None,newAccepted=0,sourceProofs=evidence,
       sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1842_G07公開成果物Scan_実行結果.md',
                           'evidence/01_PT/018_NK-OPS-001/1843_計測source追記訂正・横展開結果.md'],
       unrelatedCorrectionEvent='PGPT-20261008-2074',failureIds=[],actualAllocatedPp=None,
       tokenMeasurementIds=['268d10eaabf89ff56f8910c1b87cefbdafc92f64706deea871523d7d23573498'],
       tokenTotals=None,effortCompletionRate=None,roundedSharedDeltaIsNotExclusiveZeroCost=True,
       nextCommand='Commit/push sanitized fixed-scan evidence; choose next bounded finding-provenance or independent C07 PG/PT group',
       stopReason=None,pgptAllComplete=False))
    OUT.mkdir()
    value=dict(actualExit=0,invocation=invocation,source=SOURCE,eventId=identifier,
               formalUpdated=False,newAccepted=0,productTestsExecuted=0)
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))


if __name__=='__main__':
    main()
