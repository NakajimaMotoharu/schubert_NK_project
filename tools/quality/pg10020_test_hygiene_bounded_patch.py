"""Bounded mechanical diff export only, using qualified immutable original/candidate copies."""
import difflib
import json
import sys
import g07_host_class_provenance_inputs as data

ROOT = data.ROOT
SLOT = ROOT.parent/'pgpt-runs/PG379/pg10016-test-hygiene-candidate-v2'


def groups():
    proof = data.read_checked(data.BASE/'PG10016-test-hygiene-candidate-v2/manifest.json',
        'a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0')
    post = data.read_checked(data.BASE/'PG10018-test-hygiene-candidate-post-v1/manifest.json',
        '851c7ed89616c58b95a02868548f6dca84c38ba2cc7f847758315872476bd297')
    assert proof['actualExit'] == post['actualExit'] == 0 and post['candidateAcceptedForMechanicalApply']
    result = []
    group = []
    size = 0
    for row in proof['changed']:
        name = row['path']
        assert '/src/test/java/' in name and name.endswith('.java') and name not in proof['heldSourceHashes']
        before,after = SLOT/'original'/name,SLOT/'candidate'/name
        assert data.sha(before.read_bytes()) == row['beforeSha256'] and data.sha(after.read_bytes()) == row['candidateSha256']
        delta = list(difflib.unified_diff(before.read_text().splitlines(keepends=True),after.read_text().splitlines(keepends=True)))
        assert delta and all(line.endswith('\n') for line in delta)
        segment = '*** Update File: '+str(ROOT/name)+'\n'+''.join('@@\n' if line.startswith('@@') else line for line in delta[2:])
        length = len(segment.encode())
        assert length < 100000
        if group and size+length > 32000:
            result.append(group)
            group,size = [],0
        group.append((row,segment))
        size += length
    if group:
        result.append(group)
    return result


if __name__ == '__main__':
    batches = groups()
    if sys.argv[1:] == ['--inventory']:
        print(json.dumps(dict(batches=len(batches),files=sum(map(len,batches)),
            maxBytes=max(sum(len(s.encode()) for _,s in b) for b in batches))))
    elif len(sys.argv) == 3 and sys.argv[1] == '--emit-batch' and sys.argv[2].isdigit():
        index = int(sys.argv[2])
        assert 0 <= index < len(batches)
        for row,_ in batches[index]:
            path = ROOT/row['path']
            assert not path.is_symlink() and data.sha(path.read_bytes()) == row['beforeSha256']
        print('*** Begin Patch\n'+''.join(s for _,s in batches[index])+'*** End Patch\n',end='')
    else:
        raise ValueError('explicit patch inventory or bounded known batch only')
