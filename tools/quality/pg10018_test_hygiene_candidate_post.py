"""Independent source/candidate/actual compiler and Checkstyle receipt binding before mechanical apply."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_import_expansion_test import parse
from pg10016_test_hygiene_candidate_v2 import SLOT, OUT as CANDIDATE, SOURCE, path_hash

OUT = data.BASE/'PG10018-test-hygiene-candidate-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    proof = data.read_checked(CANDIDATE/'manifest.json',
        'a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0')
    baseline = data.read_checked(data.BASE/'PG10012-test-hygiene-checkstyle-baseline-v1/manifest.json',
        '2ca11b812be3c4feda2b9236eaf6956f38f8e521a5ba2b137865b12c3f7679f2')
    normal = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    assert proof['actualExit'] == baseline['actualExit'] == normal['actualExit'] == 0
    assert proof['source'] == baseline['source'] == normal['source'] == SOURCE
    selected = proof['selectedSourceHashes']
    assert selected == baseline['selectedSourceHashes'] and len(selected) == 832
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert proof['heldSourceHashes'] == baseline['heldSourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in proof['heldSourceHashes'].items())
    actual_changed = []
    for directory in ('original','candidate'):
        assert {p.relative_to(SLOT/directory).as_posix() for p in (SLOT/directory).rglob('*.java')} == set(selected)
    for path,digest in selected.items():
        old, new = SLOT/'original'/path,SLOT/'candidate'/path
        assert not old.is_symlink() and not new.is_symlink() and data.sha(old.read_bytes()) == digest
        current = data.sha(new.read_bytes())
        if current != digest:
            actual_changed.append(dict(path=path,beforeSha256=digest,candidateSha256=current))
    assert actual_changed == proof['changed'] and len(actual_changed) == 641
    all_files = set()
    import_count = 0
    module_counts = {}
    for module,row in proof['modules'].items():
        before_file,after_file = SLOT/(module+'-before-bindings.stdout'),SLOT/(module+'-after-bindings.stdout')
        assert data.sha(before_file.read_bytes()) == row['beforeTsvSha256']
        assert data.sha(after_file.read_bytes()) == row['afterTsvSha256']
        before,after = parse(before_file.read_text()),parse(after_file.read_text())
        assert set(before) == set(after) and len(before) == row['sourceFiles']
        module_counts[module] = len(before)
        prefix = f'src/schubert-nk-{module}/src/test/java/'
        all_files.update(prefix+p for p in before)
        for path in before:
            assert before[path]['binding'] == after[path]['binding']
            assert before[path]['declarations'] == after[path]['declarations'] and not after[path]['imports']
            import_count += len(before[path]['imports'])
    assert all_files == set(selected) and sum(module_counts.values()) == 832 and import_count == 2149
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in proof['stages'])
    assert set(proof['recoveredSuccessfulSteps']) == {'compileTools','apiBefore','batchBefore'}
    assert all(not s['reexecuted'] and s['receipt']['actualExit'] == 0 for s in proof['recoveredSuccessfulSteps'].values())
    assert all(path_hash(Path(p)) == h for p,h in proof['dependencyHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in proof['toolAndRuleHashes'].items())
    assert all(proof['toolAndRuleHashes'][p] == h for p,h in baseline['toolAndRuleHashes'].items())
    document = ET.parse(CANDIDATE/'candidate-checkstyle.xml').getroot()
    assert (CANDIDATE/'candidate-checkstyle.xml').read_bytes() == (SLOT/'candidate-checkstyle.xml').read_bytes()
    files = document.findall('file')
    assert len(files) == 832 and {str(SLOT/'candidate'/p) for p in selected} == {n.attrib['name'] for n in files}
    assert not document.findall('.//error') and proof['candidateCheckstyleFindings'] == 0
    assert proof['candidateCheckstyle']['actualExit'] == 0 and not proof['candidateCheckstyle']['timedOut']
    counts = Counter()
    for line in (SLOT/'declaration-candidates.stdout').read_text().splitlines():
        fields = line.split('\t')
        assert len(fields) == 6 and fields[0] == 'CANDIDATE' and fields[1] in selected
        counts.update(dict(zip(('groups','variables','literalTabs','heldGroups'),map(int,fields[2:]))))
    assert dict(counts) == proof['declarationCounts'] == dict(groups=556,variables=1553,literalTabs=0,heldGroups=1)
    assert len(proof['uniqueProgressPaths']) == len(set(proof['uniqueProgressPaths'])) == 12
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        candidateManifestSha256='a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0',
        selected=832,changed=641,moduleSourceCounts=module_counts,beforeCheckstyle=2705,afterCandidateCheckstyle=0,
        originalAndCandidateBytesBound=True,all832BindingsAndDeclarationValuesEqual=True,
        heldSourceFiles=3,heldSourceBytesUnchanged=True,recoveredSuccessfulStepsNotReplayed=True,
        candidateAcceptedForMechanicalApply=True,worktreeModified=False,productTestsExecuted=0,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,selected=832,changed=641,candidateCheckstyle=0,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
