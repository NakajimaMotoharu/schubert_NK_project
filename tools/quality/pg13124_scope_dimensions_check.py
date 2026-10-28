"""Metadata-only tool tests using already saved source/run domains, never replay Product."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from quality_scope_dimensions import bind, verify_qualification

OUT = data.BASE/'PG13124-scope-dimensions-check-v1'
PINS = {
    'plan':('PG13104-snapshot-corrected-plan-v1','03bc1cd8dc48f66167728284be8e5a5d04f32aea515ff3d07119dec4c66f9cd8'),
    'host':('PG13108-snapshot-corrected-host-v1','776be8fff9f5c812c557a02f2198313adf8f506f2f88fea1c809e200911b525a'),
    'proof':('PG13112-snapshot-corrected-post-v1','2e506ef62e654842ad448b38aa0a61f90b26ebaa98e3b84f42df50d221f07c9d'),
    'trace':('PG13118-snapshot-max-trace-v3','2fcf6b839ebf0cf918f81573491f82bd54a54b09184c2f685b28fee74343a83f'),
}

def rejected(action):
    try:
        action()
    except (ValueError,KeyError,TypeError):
        return
    raise AssertionError('non-equivalent metadata accepted')

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    values = {k:data.read_checked(data.BASE/name/'manifest.json',sha) for k,(name,sha) in PINS.items()}
    p,h,f = (values[k] for k in ('plan','host','proof'))
    dimensions = bind(p,h,f)
    verify_qualification(dimensions,values['trace']['currentQualification'])
    labels = []
    mutations = [
        ('wrong-source','host',lambda v:v.update(source='0'*40)),
        ('failed-terminal','host',lambda v:v.update(actualExit=1)),
        ('bool-terminal','proof',lambda v:v.update(actualExit=False)),
        ('no-cases','plan',lambda v:v.update(cases=[])),
        ('duplicate-plan','plan',lambda v:v['cases'].append(copy.deepcopy(v['cases'][0]))),
        ('duplicate-actual','host',lambda v:v['cases'].append(copy.deepcopy(v['cases'][0]))),
        ('wrong-method','host',lambda v:v['cases'][0].update(name='other')),
        ('nonpass','host',lambda v:v['cases'][0].update(nonPass=['skipped'])),
        ('missing-source','plan',lambda v:v.update(wholeTestSourceHashes={})),
        ('wrong-case-hash','plan',lambda v:v['cases'][0].update(sourceSha256='0'*64)),
        ('stale-six','proof',lambda v:v.update(observedTestExecutions=6)),
        ('bool-cases','proof',lambda v:v.update(observedTestExecutions=True)),
        ('suite-is-source','proof',lambda v:v.update(suites=2)),
        ('wrong-new','proof',lambda v:v.update(newTestIds=2)),
        ('old-new-partition','plan',lambda v:v.update(originalTests=1)),
        ('union','host',lambda v:v.update(oldExecUnion=True)),
        ('negative-physical','proof',lambda v:v.update(newTestPhysical=-1)),
        ('bool-main','proof',lambda v:v.update(allMainClassesUnchanged=True)),
    ]
    for label,key,mutate in mutations:
        bad = copy.deepcopy(values); mutate(bad[key]); assert bad != values
        rejected(lambda:bind(bad['plan'],bad['host'],bad['proof']));labels.append(label)
    for key in ['observedTestExecutions','suites','newTestIds','allMainClassesUnchanged','oldTestPhysicalUnchanged','newTestPhysical']:
        q = copy.deepcopy(values['trace']['currentQualification']);q[key] += 1
        rejected(lambda:verify_qualification(dimensions,q));labels.append('qualification-'+key)
    # A new source file may contain multiple physical classes. This is tool metadata only.
    nested = copy.deepcopy(f);nested['newTestPhysical'] = 3
    nested_dimensions = bind(p,h,nested)
    assert nested_dimensions.whole_test_sources == 1 and nested_dimensions.new_test_physical == 3
    q = copy.deepcopy(values['trace']['currentQualification']);q['newTestPhysical'] = 3
    verify_qualification(nested_dimensions,q)
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=p['source'],
        dimensions=dimensions.public(),metadataNegativeVectors=len(labels),labels=labels,
        distinctSourcePhysicalPositive=True,inputPins=PINS,productTestsExecuted=0,externalActions=0,
        priorResultsMutated=False,newAccepted=0,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
