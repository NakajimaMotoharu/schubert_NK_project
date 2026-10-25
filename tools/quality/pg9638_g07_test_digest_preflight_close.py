"""Close zero-candidate metadata preflight without claiming secret classification progress."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE = '64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP = 'G07_TEST_CLASS_DIGEST_PREFLIGHT_V1'
OUT = BASE / 'PG9638-g07-test-class-digest-preflight-metrics-v1'

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    rows = [json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    starts = [row for row in rows if row['groupId'] == GROUP and row['eventType'] == 'GROUP_START']
    assert len(starts) == 1 and not any(row['groupId'] == GROUP and row.get('groupBoundary') == 'END' for row in rows)
    start = starts[0]
    assert start['groupStartEstimatePp'] == dict(low=.25, base=1, high=3) and start['groupCapPp'] == 10
    proofs = bind([(BASE / 'PG9636-g07-test-class-digest-preflight-v1/manifest.json',
        '0110285492142b48c418879f4d99ff452b0c1f172ea57dba409bae8b11730888')], SOURCE)
    verify(invocation)
    event = metrics.append(GROUP, 'GROUP_END', dict(primaryWbs='WBS-G07', source=SOURCE, sourceBefore=SOURCE,
        workCategory='CONTRACT_AUDIT', groupStartEstimatePp=start['groupStartEstimatePp'], groupCapPp=10,
        quotaBefore=start['quotaBefore'], quotaAfter=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T09:49:32Z', quotaAfterObservedAtUTC='2026-10-25T09:51:50Z',
        sameQuotaWindow=True, observedSharedPp=0, actualAllocatedPp=None, tokenTotals=None, effortCompletionRate=None,
        attemptResult='ZERO_PUBLIC_TEST_CLASS_METADATA_INTERSECTION_NO_EXPANSION_NO_CLASSIFICATION',
        originalPlanEngineeringDelta=dict(newAccepted=0, selectionOnly=True, wholeG07Accepted=False),
        technicalMeasurementDelta=dict(existingTestClassMetadata=1910, candidateFindings=0, additionalFalsePositives=0,
            remainingUnclassified=4493, actualSecretCount=None, productTestsExecuted=0, coverage=None, formalAccepted=0),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1, targetCompile=0, targetRuntimeInvocation=0, exclusivePp=None),
        sourceProofs=proofs, sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1959_G07TestClassDigest_候補なし・拡大中止.md'],
        tokenMeasurementIds=['5f816c5b0bf696a775c935c2c0cddcae258acbc9095a4c4fdb064bf616eaf07b'],
        pgptAllComplete=False, stopReason=None, nextCommand='9640 save/push; next independent codec oracle or necessary ordinary PGPT'))
    OUT.mkdir()
    with (OUT / 'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0, source=SOURCE, eventId=event, invocation=invocation,
            candidateFindings=0, additionalFalsePositives=0, remainingUnclassified=4493,
            productTestsExecuted=0, formalUpdated=False), stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0, eventId=event)))
    scan.BEFORE = 'aa9c374ae534adadfb90f522d149cebb9ef9dfab'
    scan.OUT = BASE / 'PG9640-g07-test-class-digest-preflight-public-delta-v1'
    scan.main()
