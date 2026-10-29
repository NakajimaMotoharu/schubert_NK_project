"""Independent retained-raw/current-ref counters and immutable WBS semantics, typed JSON negatives."""
import copy
import json
import f03_last_main_resource_nine_trace as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

OUT = trace.data.BASE/'PG13982-last-main-resource-nine-trace-post-v1'
PIN = '456bae0fe833fa596971b8c746e96e80eb492a462108cac28048deff25a812df'

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
        ('refs', lambda v:v.update(joinedContextWarnings=3415)),
        ('pending', lambda v:v.update(sourceReboundCurrentWholePending=2556)),
        ('raw', lambda v:v.update(sourceDerivedRaw=6248)),
        ('retained', lambda v:v['currentLastMainResourceNineReferences']['rows'][0].update(rawRetained=False)),
        ('accepted', lambda v:v.update(newAccepted=1)),
        ('boolean-counter', lambda v:v['currentLastMainResourceNineReferences'].update(productTestsExecuted=False)),
        ('old-runtime', lambda v:v['currentLastMainResourceNineReferences'].update(currentRuntimeQualification=True)),
    ]
    for label, change in mutations:
        bad = copy.deepcopy(actual)
        change(bad)
        assert json.dumps(bad, sort_keys=True) != json.dumps(actual, sort_keys=True) and not strict(bad)
        labels.append(label)
    ids,refs,pending = trace.state_after()
    catalog = trace.data.read_checked(trace.data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    remaining = [r['id'] for r in catalog if r['id'] in ids-refs and '/src/main/' in r['path'] and r['rule']=='CloseResource']
    assert remaining == []
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation)
    OUT.mkdir()
    trace.data.write(OUT/'manifest.json', dict(actualExit=0, source=trace.SOURCE, invocation=invocation,
        traceManifestSha256=PIN, reviewManifestSha256=trace.REVIEW[1], reviewPostManifestSha256=trace.PROOF[1],
        inventorySha256=trace.data.sha(a), snapshotSha256=trace.data.sha(b),
        rawRetained=9, newCurrentReferences=9, newSourceReasons=9, sourceDerivedRaw=6247, mainRaw=1491, testRaw=4756,
        joinedContextWarnings=3416, currentWholeJoinPending=2555, noCurrentReference=2831,
        unreferencedMainCloseResourceInLegacyDerivedCatalog=0,allRawDiagnosticsRetained=True,resourceScopeNotGlobalStaticAcceptance=True,all995SourceRowsHistoricalRuntimeUnchanged=True, metadataNegativeVectors=len(labels), labels=labels,
        wholeWbsAudit=observed, productTestsExecuted=0, coverage=None, newAccepted=0,
        formalUpdated=False, whole451Accepted=False, effortPercent=None))
    print(trace.data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
