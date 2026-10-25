"""Verify mechanical patch exactness against independently qualified candidate; no Test execution."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'bba24d15923831a17e5464328b70fdb950fb2fcf'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10016-test-hygiene-candidate-v2'
OUT = data.BASE/'PG10022-test-hygiene-applied-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    proof = data.read_checked(data.BASE/'PG10016-test-hygiene-candidate-v2/manifest.json',
        'a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0')
    post = data.read_checked(data.BASE/'PG10018-test-hygiene-candidate-post-v1/manifest.json',
        '851c7ed89616c58b95a02868548f6dca84c38ba2cc7f847758315872476bd297')
    normal = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    assert proof['actualExit'] == post['actualExit'] == normal['actualExit'] == 0 and post['candidateAcceptedForMechanicalApply']
    assert proof['source'] == post['source'] == normal['source'] == SOURCE
    changed = {r['path']:r for r in proof['changed']}
    actual = set(subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT,text=True).splitlines())
    assert actual == set(changed) and len(actual) == 641
    ids = 0
    annotations = 0
    for name,digest in normal['begin']['inputHashes'].items():
        source = data.ROOT/name
        assert source.is_file() and not source.is_symlink()
        expected = changed[name]['candidateSha256'] if name in changed else digest
        assert data.sha(source.read_bytes()) == expected
        if name in changed:
            before,after = (SLOT/'original'/name).read_text(),source.read_text()
            assert data.sha((SLOT/'original'/name).read_bytes()) == digest == changed[name]['beforeSha256']
            assert source.read_bytes() == (SLOT/'candidate'/name).read_bytes()
            old_ids,new_ids = [Counter(re.findall(r'PT-[A-Za-z0-9_-]+',text)) for text in (before,after)]
            assert old_ids == new_ids
            assert before.count('@Test') == after.count('@Test')
            ids += sum(old_ids.values())
            annotations += before.count('@Test')
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in proof['heldSourceHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=SOURCE,source=None,
        qualification='EXACT_DECLARED_WORKTREE_HASHES_NOT_YET_COMMITTED_OR_NORMALLY_COMPILED',invocation=invocation,
        candidateManifestSha256='a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0',
        independentCandidatePostSha256='851c7ed89616c58b95a02868548f6dca84c38ba2cc7f847758315872476bd297',
        changedSourceHashes={p:r['candidateSha256'] for p,r in changed.items()},changedTestSources=641,
        unchangedOtherSourceInputs=True,heldSourceFilesUnchanged=3,testIdOccurrencesPreserved=ids,
        testAnnotationsPreserved=annotations,annotationCountIsNotExecutedPt=True,mainModified=False,
        productTestsExecuted=0,oldSuccessReassigned=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,changed=641,mainModified=False,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
