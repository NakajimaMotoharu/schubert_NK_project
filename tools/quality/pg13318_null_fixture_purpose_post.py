"""Independent four original/current diagnostic rows and exact source evidence checks, never target execution."""
import copy
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg13312_web_business_trace_v2 import state_after
OUT = data.BASE/'PG13318-null-fixture-purpose-post-v1'
REVIEW = data.BASE/'PG13317-null-fixture-purpose-v2'
CLASSIFICATIONS = {'PMD-02148':'DELIBERATE_RECORD_EQUALS_NULL_NEGATIVE_ORACLE','PMD-05293':'NAMESPACE_FOR_STATIC_NESTED_FIXTURE_TYPES',
    'PMD-06238':'NESTED_IO_FAULT_PORT_NOT_JUNIT_TEST_CLASS','PMD-06249':'NESTED_IO_FAULT_PORT_NOT_JUNIT_TEST_CLASS'}

def check(v,old,normal):
    assert v['source'] == '81a1b0c32be8167c07320e6bfaf469bcd44eb7bd' and len(v['rows']) == 4 and {r['id'] for r in v['rows']} == set(old)
    reference = dict(scopeCount=4,purposeReferencesBefore=3345,purposeReferencesAfter=3349,pendingAfter=1370,noReferenceAfter=4398,rawDiagnostics=7747,originalCorrections=1694,newCorrections=0,
        sourceChanged=False,newTestIds=0,productTestsExecuted=0,coverage=None,newAccepted=0,actualViolationCount=None,qualityGateExit=1,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False)
    assert json.dumps({k:v[k] for k in reference},sort_keys=True) == json.dumps(reference,sort_keys=True)
    owners = {'DbQueryDurationMetricCollectorTest':'WBS-P018-09','InspectorUnitProbeFixture':'WBS-P004-04','InspectorCredentialLoaderTest':'WBS-P018-01'}
    for r in v['rows']:
        o = old[r['id']];text = (data.ROOT/o['path']).read_text();sha = data.sha(text.encode())
        assert r['path'] == o['path'] and r['originalAttributes'] == o['attributes'] and r['message'] == o['message'] and r['originalInputSha256'] == o['inputSha256']
        assert sha == r['sourceSha256'] == normal['begin']['inputHashes'][o['path']]
        assert r['evidence'] in text and data.sha(r['evidence'].encode()) == r['evidenceSha256']
        assert r['sourceLine'] == text.splitlines()[int(r['currentAttributes']['beginline'])-1]
        assert r['classification'] == CLASSIFICATIONS[r['id']] and r['canonicalOwner'] == r['canonicalCostOwner'] == owners[Path(o['path']).stem]
        assert r['manualPurposeReviewComplete'] is True and r['ptExecutionExempt'] is False and r['actualViolation'] is None
        assert type(r['productTestsExecuted']) is int and r['productTestsExecuted'] == 0 and r['status'] == 'SOURCE_PURPOSE_REVIEWED_NOT_DYNAMIC_ACCEPTED'
        assert len(r['purpose']) > 70 and len(r['residualRisk']) > 70
        if r['id'] == 'PMD-02148':assert r['evidence'] == 'assertFalse(first.equals(null));'
        elif r['id'] == 'PMD-05293':
            assert '  static final class Script implements InspectorUnitProbe.Reader {' in r['evidence'] and '  static final class Child extends Process {' in r['evidence']
            assert all('    final class '+s+' extends ' in r['evidence'] and 'static final class '+s not in r['evidence'] for s in ['ReadStream','WriteStream'])
        else:assert not re.search(r'^\s*@Test(?:\s|$|\()',r['evidence'],re.M)

def main():
    invocation = capture(__file__);assert not OUT.exists() and not (data.BASE/'PG13316-null-fixture-purpose-v1').exists()
    m = data.read_checked(REVIEW/'manifest.json','e3a2f4ba8d26b368328838e54db68be515dad20af72071d7b11c1862ef7aadd0');v = data.read_checked(REVIEW/'review.json',m['reviewSha256'])
    n = data.read_checked(data.BASE/'PG13306-web-business-literal-v2-v1/manifest.json','54547059dfcc03323666371126747e3503b35373bae18cc6b49de23d13854cea')
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    ids,refs,pending = state_after();assert [len(x) for x in [ids,refs,pending]] == [7747,3345,1366]
    old = {r['id']:r for r in original if r['id'] in CLASSIFICATIONS};assert set(old) <= ids-refs;check(v,old,n);labels = []
    for label,change in [('missing',lambda x:x['rows'].pop()),('duplicate',lambda x:x['rows'].__setitem__(1,x['rows'][0])),('oracle',lambda x:x['rows'][0].update(evidence='assertFalse(first == null);')),
        ('static-hierarchy',lambda x:x['rows'][1].update(evidence=x['rows'][1]['evidence'].replace('final class ReadStream','static final class ReadStream'))),
        ('owner',lambda x:x['rows'][0].update(canonicalCostOwner='WBS-F03')),('exemption',lambda x:x['rows'][0].update(ptExecutionExempt=True)),
        ('bool-zero',lambda x:x.update(productTestsExecuted=False)),('coverage',lambda x:x.update(coverage={'LINE':100}))]:
        bad = copy.deepcopy(v);change(bad)
        try:check(bad,old,n)
        except AssertionError:labels.append(label)
        else:raise AssertionError('false fixture review accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=v['source'],reviewManifestSha256=data.sha((REVIEW/'manifest.json').read_bytes()),
        independentOriginalIds=4,metadataNegativeVectors=len(labels),negativeLabels=labels,originalFailedInvocation=dict(session=42726,actualExit=1,operatorObserved=True,reportPersisted=False,originalOutAbsent=True,
        entrySha256='6bfedf4aaf91d0d1b6fd695c314571c5a14605a2bbfbc6f54a007985eb535dd5'),newPurposeReferences=4,newCorrections=0,sourceOrTestChanged=False,productTestsExecuted=0,newAccepted=0,qualityGateExit=1,coverage=None,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
