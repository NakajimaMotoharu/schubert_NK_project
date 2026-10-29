"""Independent retained-raw/current-ref counters and immutable WBS semantics, typed JSON negatives."""
import copy
import json
import f03_jms_owner_six_trace as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

OUT = trace.data.BASE/'PG13778-jms-owner-six-trace-post-v1'
PIN = 'aac5c97bfa530a2bef14fcbf2eda0293e72d95e06751d79960dbf4fe340e9d2a'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    prior, rows, raw, snap = trace.inputs()
    value = trace.data.read_checked(trace.OUT/'manifest.json', PIN)
    verify(value['invocation'])
    actual = copy.deepcopy(value)
    for key in ['invocation', 'wholeWbsAuditBefore']:
        actual.pop(key, None)
    expected = trace.expected(prior, rows)
    strict = lambda v: json.dumps(v, sort_keys=True) == json.dumps(expected, sort_keys=True)
    assert strict(actual)
    a, b = trace.documents(value, raw, snap)
    assert (trace.data.ROOT/trace.INV).read_bytes() == a and (trace.data.ROOT/trace.SNAP).read_bytes() == b
    trace.validate_docs(a, b, json.loads(raw), json.loads(snap))
    labels = []
    mutations = [
        ('source', lambda v:v.update(source='0'*40)),
        ('refs', lambda v:v.update(joinedContextWarnings=3354)),
        ('pending', lambda v:v.update(sourceReboundCurrentWholePending=2488)),
        ('raw', lambda v:v.update(sourceDerivedRaw=6243)),
        ('retained', lambda v:v['currentJmsOwnerSixReferences']['rows'][0].update(rawRetained=False)),
        ('accepted', lambda v:v.update(newAccepted=1)),
        ('boolean-counter', lambda v:v['currentJmsOwnerSixReferences'].update(productTestsExecuted=False)),
        ('old-runtime', lambda v:v['currentJmsOwnerSixReferences'].update(currentRuntimeQualification=True)),
    ]
    for label, change in mutations:
        bad = copy.deepcopy(actual)
        change(bad)
        assert json.dumps(bad, sort_keys=True) != json.dumps(actual, sort_keys=True) and not strict(bad)
        labels.append(label)
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation)
    OUT.mkdir()
    trace.data.write(OUT/'manifest.json', dict(actualExit=0, source=trace.SOURCE, invocation=invocation,
        traceManifestSha256=PIN, reviewManifestSha256=trace.REVIEW[1], reviewPostManifestSha256=trace.PROOF[1],
        inventorySha256=trace.data.sha(a), snapshotSha256=trace.data.sha(b),
        rawRetained=6, newCurrentReferences=6, newSourceReasons=None,reviewedCurrentReasons=6, sourceDerivedRaw=6247, mainRaw=1491, testRaw=4756,
        joinedContextWarnings=3394, currentWholeJoinPending=2533, noCurrentReference=2853,
        all995SourceRowsHistoricalRuntimeUnchanged=True, metadataNegativeVectors=len(labels), labels=labels,
        wholeWbsAudit=observed, productTestsExecuted=0, coverage=None, newAccepted=0,
        formalUpdated=False, whole451Accepted=False, effortPercent=None))
    print(trace.data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
