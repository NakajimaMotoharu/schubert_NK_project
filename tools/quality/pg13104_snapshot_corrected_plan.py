"""Freeze corrected strong exception oracles with original input/operation tokens preserved."""
import copy
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13101_snapshot_oracle_inverse import inverse, negative

SOURCE = '5c378e064f0f8a7366316d4afa28fbb2cd9cec81'
OUT = data.BASE/'PG13104-snapshot-corrected-plan-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    original_manifest = data.read_checked(data.BASE/'PG13100-snapshot-oracle-originals-v1/manifest.json','4c9db4bb5ddf53982ac6778a801a57a12ec84ce1ce55d37765ec1328f733a861')
    original = data.read_checked(data.BASE/'PG13100-snapshot-oracle-originals-v1/original.json',original_manifest['originalSha256'])
    old_plan = data.read_checked(data.BASE/'PG13094-snapshot-max-plan-v1/manifest.json','8b6b6112b7df66abb79906c3920d432246f38268e2d9710770018ad404b05708')
    p = data.read_checked(data.BASE/'PG13102-snapshot-oracle-preflight-v1/manifest.json','31581f6939034eaabe3df2a9fe8aa590bc0ce5c289d3ec48e70542f2b61f7b95')
    baseline = data.read_checked(data.BASE/'PG13076-monitor-test-six-compile-v1/manifest.json','77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932')
    assert p['baseSource'] == old_plan['source'] == original['source'] == '0a84859838be8826d58886e6d7f27bd849a9ea05'
    assert p['actualExit'] == 0 and all(v['findings'] == v['processingErrors'] == 0 for v in p['reports'].values())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in baseline['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in p['candidateSourceHashes'].items())
    text = (data.ROOT/original['test']).read_text(); change = inverse(original['text'],text); vectors = negative(original['text'],text)
    assert change == p['oracleCorrectionInverse'] and vectors == p['oracleCorrectionNegativeVectors'] == 7
    assert subprocess.check_output(['git','diff','--name-only',original['source'],SOURCE,'--','src'],cwd=data.ROOT,text=True).splitlines() == [original['test']]
    cases = copy.deepcopy(old_plan['cases']); whole = {original['test']:p['candidateSourceHashes'][original['test']]}
    for row in cases: row['sourceSha256'] = whole[row['path']]
    assert len(cases) == 3 and old_plan['eligibilityClosureSourceHashes'] == {path:sha for path,sha in p['candidateSourceHashes'].items() if '/src/main/java/' in path}
    value = dict(actualExit=0,source=SOURCE,before=baseline['source'],failedCandidateSource=original['source'],invocation=invocation,cases=cases,
        wholeTestSourceHashes=whole,eligibilityClosureSourceHashes=old_plan['eligibilityClosureSourceHashes'],supportTestSourceHashes={},
        protocolClosure=old_plan['protocolClosure'],originalTests=0,newTests=3,totalTests=3,totalCorrections=1,
        sameExecRequired=True,oldExecUnion=False,oracleCorrectionInverse=change,oracleCorrectionNegativeVectors=vectors,
        judgement='Same novel memory-only maximum/interior/tail vectors, strong corrected immutable-layout/field exception classes; old candidate failed2 remains failed, no old PASS transfer',
        additionalSourceQualificationCycles=1,newAccepted=0,whole451Accepted=False,externalActions=0)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
