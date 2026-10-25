"""Record actual three new page tests, tool rework and honest uncovered counters."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
OPS = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
GROUP = 'PROTOCOL_PAGINATION_BOUNDARY3_V1'
OUT = BASE / 'PG9670-pagination-group-close-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    rows = [json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    starts = [r for r in rows if r['groupId'] == GROUP and r['eventType'] == 'GROUP_START']
    assert len(starts) == 1 and not any(r['groupId'] == GROUP and r.get('groupBoundary') == 'END' for r in rows)
    start = starts[0]
    assert start['groupStartEstimatePp'] == dict(low=.5, base=2, high=5) and start['groupCapPp'] == 10
    pins = [(OPS / 'PG9660-pagination-six-compile-v1/manifest.json', 'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c'),
        (BASE / 'PG9662-pagination-boundary-host-v1/manifest.json', 'c5dfb7e4137c0c96833bcba4a3a3c6ec5cba04a54b3134d13b7395d808cbc19e'),
        (BASE / 'PG9664-pagination-boundary-post-v1/manifest.json', 'd12d686512ce45599f7a9eaa89d03560a7c579aaa8c3e5036b9de2a641510959'),
        (BASE / 'PG9666-pagination-static-v2/manifest.json', '41807eb5d29a989424939246359f8eb7f9162bd03c7fbc4d1f2bd8932546de08'),
        (BASE / 'PG9668-pagination-trace-quality-post-v2/manifest.json', '9db0e573444f6fd72649fd68efcddfe8e6d15eedb1e0d2069efbb9d7525bd445')]
    proofs = bind(pins, SOURCE)
    post = json.loads(pins[2][0].read_bytes())
    assert post['actualTests'] == post['newTestIds'] == 3
    verify(invocation)
    event = metrics.append(GROUP, 'GROUP_END', dict(primaryWbs='WBS-P002-02', source=SOURCE,
        sourceBefore='64446a9f8901084a4ad7eba1f66ae975eb2bbdea', workCategory='SELECTED_TEST',
        groupStartEstimatePp=start['groupStartEstimatePp'], groupCapPp=10, quotaBefore=start['quotaBefore'],
        quotaAfter=dict(usedPercent=8, remainingPercent=92, resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T10:18:29Z', quotaAfterObservedAtUTC='2026-10-25T10:59:08Z',
        sameQuotaWindow=True, observedSharedPp=1, actualAllocatedPp=None, tokenTotals=None, effortCompletionRate=None,
        attemptResult='NEW_PAGE_COMPONENT_3_PT_PASS_CURRENT_STATIC_SIX_ZERO_POST_VERIFIED_FOUR100_FALSE',
        technicalMeasurementDelta=dict(productTestsExecuted=3, suites=1, newTestIds=3, newMain=0,
            wholeValidatorCounters=dict(line=dict(covered=72,total=315), method=dict(covered=11,total=38),
                classCounter=dict(covered=1,total=1), branch=dict(covered=22,total=197)),
            requiredWholeClassFour100=False, formalAccepted=0, ordinaryTestDeclarations=5625, declarationNotPassCount=True),
        originalPlanEngineeringDelta=dict(item='PAGE2_MAX999999_AND_SINGLE_FIELD_INVALID_COMPONENT_CASES', programPtComplete=False),
        additionalDiscoveries=dict(bugs=['BUG-1754','BUG-1755'], ykt=['YKT-1505','YKT-1506']),
        sourceReauthentication=dict(currentNormalInputHashes=True, all1843MainUnchanged=True, oldProductPtTransferred=False),
        toolConstructionAndEnvironmentRework=dict(staleM2MissingClassFailure=18, staticCorrectedMissingClass=0,
            ownerLookupV1Exit=1, ownerLookupV2Exit=0, beforeExecutionUnusedImportLint=1, exclusivePp=None),
        sourceProofs=proofs, sourceEvidenceRefs=['evidence/01_PT/002_NK-PRO-002/007_Page境界_実行結果.md'],
        tokenMeasurementIds=['b3264fb1adf4c8adf4d12442fe2fbc28d8a272601a4bd235ac04a47498d80bef'],
        stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE', oldCumulativeStopPolicyApplied=False,
        pgptAllComplete=False, stopReason=None,
        nextCommand='9672 public delta/save-push; then current-source new Test owner registration or needed ordinary PT; actual HOLD unchanged'))
    OUT.mkdir()
    with (OUT / 'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=event,invocation=invocation,actualTests=3,newTestIds=3,
            formalUpdated=False,newAccepted=0,wholeFour100=False,effortPercent=None),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event)))


if __name__ == '__main__':
    main()
