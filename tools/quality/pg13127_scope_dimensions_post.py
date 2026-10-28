"""Independent checks of saved metadata/tool provenance, no Product class loads."""
import hashlib
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13127-scope-dimensions-post-v1'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13126-scope-dimensions-check-v2/manifest.json','15eeaf448f0e9dca5c3bb1c6f82bd9fe707fb0a734001c66dcea9bc15cfb56c0')
    assert m['actualExit'] == 0 and m['productTestsExecuted'] == m['externalActions'] == m['newAccepted'] == 0
    assert m['dimensions'] == dict(source='5c378e064f0f8a7366316d4afa28fbb2cd9cec81',observed_cases=3,suites=1,whole_test_sources=1,new_test_ids=3,old_test_physical_unchanged=1972,new_test_physical=1,main_physical_unchanged=1843)
    assert m['metadataNegativeVectors'] == len(m['labels']) == len(set(m['labels'])) == 24
    assert {'bool-terminal','stale-six','qualification-oldTestPhysicalUnchanged','qualification-newTestPhysical'} <= set(m['labels'])
    assert m['distinctSourcePhysicalPositive'] and not m['priorResultsMutated'] and not m['whole451Accepted'] and m['effortPercent'] is None
    assert hashlib.sha256((data.ROOT/'tools/quality/pg13124_scope_dimensions_check.py').read_bytes()).hexdigest() == 'abc3f40f15feea4eecfd40181f84932deef8d0f39d28663529d5b66ad3efd519'
    verify(m['invocation'])
    for name,sha in m['inputPins'].values():
        data.read_checked(data.BASE/name/'manifest.json',sha)
    assert len({json.dumps(v) for v in [False,0,0.0,True,1]}) == 5
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        checkedManifestSha256='15eeaf448f0e9dca5c3bb1c6f82bd9fe707fb0a734001c66dcea9bc15cfb56c0',
        helperAndInputsUnchanged=True,metadataNegativeVectors=24,independentJsonTypeVectors=5,
        productTestsExecuted=0,externalActions=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
