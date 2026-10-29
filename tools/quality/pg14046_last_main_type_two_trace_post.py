"""Independent retained-raw/current-ref counters and immutable WBS semantics, typed JSON negatives."""
import copy
import json
import f03_last_main_type_two_trace as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

OUT = trace.data.BASE/'PG14046-last-main-type-two-trace-post-v1'
PIN = '28092d60e031be855606ea95218097fa5f748c54f978f33b6e4f30478f3ed761'

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
        ('refs', lambda v:v.update(joinedContextWarnings=3492)),
        ('pending', lambda v:v.update(sourceReboundCurrentWholePending=2633)),
        ('raw', lambda v:v.update(sourceDerivedRaw=6248)),
        ('retained', lambda v:v['currentLastMainTypeTwoReferences']['rows'][0].update(rawRetained=False)),
        ('accepted', lambda v:v.update(newAccepted=1)),
        ('boolean-counter', lambda v:v['currentLastMainTypeTwoReferences'].update(productTestsExecuted=False)),
        ('old-runtime', lambda v:v['currentLastMainTypeTwoReferences'].update(currentRuntimeQualification=True)),
    ]
    for label, change in mutations:
        bad = copy.deepcopy(actual)
        change(bad)
        assert json.dumps(bad, sort_keys=True) != json.dumps(actual, sort_keys=True) and not strict(bad)
        labels.append(label)
    catalog=trace.data.read_checked(trace.data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    ids,refs,pending=trace.state_after()
    remaining=[r for r in catalog if r['id'] in ids-refs and '/src/main/' in r['path'] and r['rule']=='AvoidInstanceofChecksInCatchClause']
    assert not remaining
    question=next(r for r in rows if r['id']=='PMD-00048')
    assert question['coordinateScope']['spanProofIsPrefixOnly'] is True and question['coordinateScope']['wholeJavaUnicodeTranslationValidated'] is False
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation)
    OUT.mkdir()
    trace.data.write(OUT/'manifest.json', dict(actualExit=0, source=trace.SOURCE, invocation=invocation,
        traceManifestSha256=PIN, reviewManifestSha256=trace.REVIEW[1], reviewPostManifestSha256=trace.PROOF[1],
        inventorySha256=trace.data.sha(a), snapshotSha256=trace.data.sha(b),
        rawRetained=2, newCurrentReferences=2, newSourceReasonRows=2, uniqueOperandSpans=2, uniqueCatchClauses=2, sourceDerivedRaw=6247, mainRaw=1491, testRaw=4756,
        joinedContextWarnings=3493, currentWholeJoinPending=2632, noCurrentReference=2754,
        all995SourceRowsHistoricalRuntimeUnchanged=True, metadataNegativeVectors=len(labels), labels=labels, unreferencedMainCatchInstanceof=0, selectedQuestionSpanPrefixOnly=True, wholeJavaUnicodeTranslationValidated=False,
        wholeWbsAudit=observed, productTestsExecuted=0, coverage=None, newAccepted=0,
        formalUpdated=False, whole451Accepted=False, effortPercent=None))
    print(trace.data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
