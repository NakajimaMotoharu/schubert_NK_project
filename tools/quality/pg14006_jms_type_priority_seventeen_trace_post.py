"""Independent retained-raw/current-ref counters and immutable WBS semantics, typed JSON negatives."""
import copy
import json
import f03_jms_type_priority_seventeen_trace_v2 as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

OUT = trace.data.BASE/'PG14006-jms-type-priority-seventeen-trace-post-v1'
PIN = '93800c9f3b853037be7a7563e1c5cba65ab998788d99bfcc075e67b17626aa0e'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    prior, rows, raw, snap = trace.inputs()
    value = trace.data.read_checked(trace.OUT/'manifest.json', PIN)
    verify(value['invocation'])
    actual = copy.deepcopy(value)
    for key in ['invocation', 'wholeWbsAuditBefore', 'toolCorrection']:
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
        ('refs', lambda v:v.update(joinedContextWarnings=3440)),
        ('pending', lambda v:v.update(sourceReboundCurrentWholePending=2581)),
        ('raw', lambda v:v.update(sourceDerivedRaw=6248)),
        ('retained', lambda v:v['currentJmsTypePrioritySeventeenReferences']['rows'][0].update(rawRetained=False)),
        ('accepted', lambda v:v.update(newAccepted=1)),
        ('boolean-counter', lambda v:v['currentJmsTypePrioritySeventeenReferences'].update(productTestsExecuted=False)),
        ('old-runtime', lambda v:v['currentJmsTypePrioritySeventeenReferences'].update(currentRuntimeQualification=True)),
    ]
    for label, change in mutations:
        bad = copy.deepcopy(actual)
        change(bad)
        assert json.dumps(bad, sort_keys=True) != json.dumps(actual, sort_keys=True) and not strict(bad)
        labels.append(label)
    # BUG2084: validate distinct immutable input identities independently of generated OUT.
    fixed=('PG13992-management-catch-priority-eight-trace-v1','PG14000-jms-type-priority-seventeen-contexts-v1','PG14002-jms-type-priority-seventeen-post-v1','PG14005-jms-type-priority-seventeen-trace-v2')
    current=(trace.PRIOR[0],trace.REVIEW[0],trace.PROOF[0],trace.OUT.name)
    def roles(v):
        if tuple(v)!=fixed or len(set(v))!=4:raise ValueError('immutable prior/review/proof and fresh output roles required')
    roles(current)
    role_negatives=0
    for index,replacement in [(0,current[3]),(1,current[0]),(2,current[3]),(3,current[0])]:
        bad=list(current);bad[index]=replacement
        try:roles(bad)
        except ValueError:role_negatives+=1
        else:raise AssertionError('input/output collision accepted')
    import f03_management_catch_priority_eight_trace as prior_trace
    import f03_remaining_main_resource_six_trace as older_trace
    unaffected=[]
    for helper in [prior_trace,older_trace]:
        assert helper.PRIOR[0]!=helper.OUT.name
        trace.data.read_checked(helper.data.BASE/helper.PRIOR[0]/'manifest.json',helper.PRIOR[1])
        unaffected.append(helper.OUT.name)
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation)
    OUT.mkdir()
    trace.data.write(OUT/'manifest.json', dict(actualExit=0, source=trace.SOURCE, invocation=invocation,
        traceManifestSha256=PIN, reviewManifestSha256=trace.REVIEW[1], reviewPostManifestSha256=trace.PROOF[1],
        inventorySha256=trace.data.sha(a), snapshotSha256=trace.data.sha(b),
        rawRetained=17, newCurrentReferences=17, newSourceReasonRows=17, uniqueOperandSpans=12, uniqueCatchClauses=9, sourceDerivedRaw=6247, mainRaw=1491, testRaw=4756,
        joinedContextWarnings=3441, currentWholeJoinPending=2580, noCurrentReference=2806,
        all995SourceRowsHistoricalRuntimeUnchanged=True, metadataNegativeVectors=len(labels), labels=labels, roleCollisionNegativeVectors=role_negatives, priorToolsNonApplicable=unaffected, correctedToolBug='BUG2084/YKT1832',
        wholeWbsAudit=observed, productTestsExecuted=0, coverage=None, newAccepted=0,
        formalUpdated=False, whole451Accepted=False, effortPercent=None))
    print(trace.data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
