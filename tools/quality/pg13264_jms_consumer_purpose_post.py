"""Independent saved-source/diagnostic/owner checks; no target compilation or execution."""
from collections import Counter
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13258_current_catalog_supplement import state_after

OUT = data.BASE/'PG13264-jms-consumer-purpose-post-v1'
REVIEW = data.BASE/'PG13262-jms-consumer-purpose-review-v1'
RULES = dict(CloseResource='LONG_LIVED_OWNER_AND_CONTEXT_CHILD',AvoidCatchingGenericException='BOUNDARY_FAILURE_RETENTION_NOT_SUCCESS',
    AvoidInstanceofChecksInCatchClause='FATAL_PRIORITY_AND_IDENTITY',AvoidSynchronizedStatement='SERIAL_OWNER_CLOSE_STATE')

def check(v,old,normal):
    assert v['source'] == 'db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
    assert len(v['rows']) == len({r['id'] for r in v['rows']}) == 72 and {r['id'] for r in v['rows']} == set(old)
    assert Counter(r['rule'] for r in v['rows']) == Counter(CloseResource=7,AvoidCatchingGenericException=39,AvoidInstanceofChecksInCatchClause=23,AvoidSynchronizedStatement=3)
    for k,x in dict(rawDiagnostics=8022,originalCorrections=1419,newCorrections=0,productTestsExecuted=0,newAccepted=0,purposeReferencesAfter=3345,pendingAfter=1255,noReferenceAfter=4677,qualityGateExit=1).items():
        assert type(v[k]) is int and v[k] == x
    assert v['coverage'] is v['actualViolationCount'] is None and v['wholeF03Accepted'] is v['whole451Accepted'] is v['formalUpdated'] is False
    owners = dict(QuestionWorkConsumers='WBS-P012-01',SyncRequestConsumers='WBS-P005-03',WebLogConsumers='WBS-P006-05')
    for r in v['rows']:
        source = old[r['id']];path = source['path'];text = (data.ROOT/path).read_text()
        assert r['path'] == path and r['sourceSha256'] == source['inputSha256'] == data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        assert r['attributes'] == source['attributes'] and r['message'] == source['message'] and r['rule'] == source['rule']
        assert r['enclosingMethod'] == source['attributes']['method'] and r['sourceLine'] == text.splitlines()[source['line']-1]
        assert r['canonicalOwner'] == r['canonicalCostOwner'] == owners[Path(path).stem]
        assert r['classification'] == RULES[r['rule']] and len(r['purpose']) > 80 and len(r['residualRisk']) > 80
        assert r['manualPurposeReviewComplete'] is True and r['ptExecutionExempt'] is False and r['actualViolation'] is r['measuredProductCounters'] is None
        assert type(r['productTestsExecuted']) is int and r['productTestsExecuted'] == 0 and r['status'] == 'SOURCE_PURPOSE_REVIEWED_DYNAMIC_AND_WHOLE_STATIC_HOLD'
    assert len(v['sourceFiles']) == len(v['testSourceExpectations']) == 3
    for path,item in {**v['sourceFiles'],**v['testSourceExpectations']}.items():
        raw = (data.ROOT/path).read_bytes();assert data.sha(raw) == item['sha256'] == normal['begin']['inputHashes'][path]

def main():
    invocation = capture(__file__);assert not OUT.exists()
    m = data.read_checked(REVIEW/'manifest.json','21035e3b63cb7a03ecbdc3c95496bd8c21d53d73de5cf365fd540ebec10bca46')
    v = data.read_checked(REVIEW/'review.json',m['reviewSha256'])
    n = data.read_checked(data.BASE/'PG13242-business-delivery-literal-v1/manifest.json','73d770b42807892d7b39bdc6d7da6d45e73857c152cb6aace83c0387e3239496')
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    ids,refs,pending = state_after();assert [len(x) for x in [ids,refs,pending]] == [8022,3273,1183]
    names = {'QuestionWorkConsumers.java','SyncRequestConsumers.java','WebLogConsumers.java'}
    old = {r['id']:r for r in original if r['id'] in ids-refs and Path(r['path']).name in names};check(v,old,n)
    labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('missing',lambda x:x['rows'].pop()),('duplicate',lambda x:x['rows'].__setitem__(1,x['rows'][0])),
        ('owner',lambda x:x['rows'][0].update(canonicalCostOwner='WBS-F03')),('purpose',lambda x:x['rows'][0].update(manualPurposeReviewComplete=False)),
        ('bool-zero',lambda x:x.update(productTestsExecuted=False)),('quality',lambda x:x.update(qualityGateExit=0)),('coverage',lambda x:x.update(coverage={'LINE':100}))]:
        bad = copy.deepcopy(v);change(bad)
        try:check(bad,old,n)
        except AssertionError:labels.append(label)
        else:raise AssertionError('false source-only review qualification accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=v['source'],reviewManifestSha256=data.sha((REVIEW/'manifest.json').read_bytes()),
        independentOriginalIds=72,metadataNegativeVectors=len(labels),negativeLabels=labels,rawDiagnostics=8022,newPurposeReferences=72,sourceOwnersCostsUnchanged=True,newCorrections=0,newAccepted=0,
        productTestsExecuted=0,coverage=None,actualViolationCount=None,qualityGateExit=1,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
