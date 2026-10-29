"""Independent original event/periodic quota semantics; no Product PT or cost allocation."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13957-periodic-quota-semantics-post-v1'
PIN = '86593de60fa46eb34b7d2f85f587c3baa04d20aed1d84c3f88d5cdddb087761e'

def assess(value, before, after):
    if value['thresholdUsedPercent'] != 35 or type(value['thresholdUsedPercent']) is not int:
        raise ValueError('exact trigger threshold')
    if value['before'] != before or value['after'] != after:
        raise ValueError('original event quota observations only')
    for observed in (value['before'],value['after']):
        if any(type(observed.get(k)) is not int for k in ['usedPercent','resetsAt','windowDurationMins']):
            raise ValueError('typed quota values, not bool')
    same = before['resetsAt'] == after['resetsAt']
    expected_delta = after['usedPercent']-before['usedPercent'] if same else None
    if value['sameWindow'] is not same or value['observedSharedPp'] != expected_delta:
        raise ValueError('marker-exact observed shared difference')
    if any(value[key] is not None for key in ['dedicatedPgptPp','pmoPp','N','T']):
        raise ValueError('missing costs/tokens remain null')

def main():
    invocation = capture(__file__);assert not OUT.exists()
    original = data.read_checked(data.BASE/'PG13956-used35-periodic-original-manifest-audit-v1/manifest.json',PIN)
    events = [json.loads(line) for line in (data.ROOT.parent/'PMO/pgpt-execution-metrics/events.jsonl').read_text().splitlines()]
    baseline, = [e for e in events if e['eventId']=='PGPT-20261008-2900']
    start, = [e for e in events if e['eventId']=='PGPT-20261008-2929']
    corrected, = [e for e in events if e['eventId']=='PGPT-20261008-2930']
    before = baseline['quotaAfter'];after = start['freshQuota']['primary'];q = original['quotaObservation']
    assess(q,before,after)
    assert corrected['correctionForEventId'] == start['eventId'] and corrected['observedSharedPp'] == q['observedSharedPp'] == 6
    labels = []
    for label,change in [('wrong-delta',lambda v:v.update(observedSharedPp=5)),('dedicated-zero',lambda v:v.update(dedicatedPgptPp=0)),('token-estimate',lambda v:v.update(N=1)),('threshold-as-actual',lambda v:v['after'].update(usedPercent=35)),('boolean-quota',lambda v:v['after'].update(usedPercent=True))]:
        bad = copy.deepcopy(q);change(bad)
        try:assess(bad,before,after)
        except ValueError:labels.append(label)
        else:raise AssertionError('false quota/cost explanation accepted')
    changed_after = dict(after,resetsAt=after['resetsAt']+1)
    split = dict(copy.deepcopy(q),after=changed_after,sameWindow=False,observedSharedPp=None)
    assess(split,before,changed_after)
    bad = dict(split,observedSharedPp=6)
    try:assess(bad,before,changed_after)
    except ValueError:labels.append('different-window-no-delta')
    else:raise AssertionError('cross-window quota difference accepted')
    assert len(labels) == 6
    assert original['currentSourceQualifiedMethodsReferenced'] == 119 and original['newFunctionalMethodIds'] == 1 and original['existingMethodsRequalified'] == 118
    assert original['historicalSourceMethodsReferencedSeparately'] == 9 and original['sourceDomainsMerged'] is False
    assert original['productTestsExecutedByThisAudit'] == original['newAccepted'] == 0 and original['formalUpdated'] is False and original['effortPercent'] is None
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original['source'],invocation=invocation,periodicManifestSha256=PIN,
        baselineEvent=baseline['eventId'],startEvent=start['eventId'],correctionEvent=corrected['eventId'],thresholdUsedPercent=35,actualStartUsedPercent=after['usedPercent'],observedSharedPp=q['observedSharedPp'],dedicatedCost=None,
        quotaSemanticNegativeVectors=len(labels),labels=labels,differentWindowPositive=True,primaryAuditMetadataDifferenceProfilesNotProductTests=True,
        relatedBug='BUG-2083',relatedYkt='YKT-1831',originalEventsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
