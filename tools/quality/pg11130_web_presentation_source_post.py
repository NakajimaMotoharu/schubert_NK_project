"""Independent inverse of twelve fixed Inbox value fixture literals; all original oracle tokens retained."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded

OUT = data.BASE/'PG11130-web-presentation-source-post-v1'


def remove(tokens,pattern):
    found = [i for i in range(len(tokens)-len(pattern)+1) if tokens[i:i+len(pattern)] == pattern]
    if len(found) != 1:
        raise ValueError('one exact same-value fixture declaration')
    i = found[0]
    del tokens[i:i+len(pattern)]


def inverse(stem,before,after,rows):
    tokens = canonical(after)
    for row in rows:
        remove(tokens,canonical('private static final String '+row['name']+' = '+row['literal']+';'))
        if tokens.count(row['name']) != row['references']:
            raise ValueError('all original fixed literal sites retained')
        literal = canonical(row['literal'])
        assert len(literal) == 1
        tokens = [literal[0] if token == row['name'] else token for token in tokens]
    if folded(tokens) != canonical(before):
        raise ValueError('unrelated fixture/assertion/golden/callee changed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG11128-web-presentation-literal-plan-v1/manifest.json'
    plan = data.read_checked(path,'74d26591ad7a23dc45122158d1b8a4e1b5289f4aa86aba260d90b6262bea8d8f')
    normal = data.read_checked(data.BASE/'PG11106-web-pure-value-six-compile-v1/manifest.json',
        '77fd485d4718416d3cb75e57e16458d2633289b432bb30a97738d326edcc364b')
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed = {r['path'] for r in plan['sourceChanges']}
    assert len(changed) == 4 and plan['actualExit'] == 0 and plan['constantsAdded'] == 9
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives = 0
    for row in plan['sourceChanges']:
        p = row['path']
        stem = Path(p).stem
        before,after = (snapshot/p).read_text(),(data.ROOT/p).read_text()
        assert data.sha(before.encode()) == row['beforeSha256'] and data.sha(after.encode()) == row['sha256']
        inverse(stem,before,after,row['constants'])
        first = row['constants'][0]
        declaration = 'private static final String '+first['name']+' = '+first['literal']+';'
        bads = [after.replace(first['literal'],'"wrong-fixed-vector"',1),after.replace(declaration,'',1),after.replace('@Test','@Disabled',1)]
        for bad in bads:
            assert bad != after
            try:
                inverse(stem,before,bad,row['constants'])
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('changed expected/case/boundary/identifier accepted')
    assert negatives == 12
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],
        planManifestSha256=data.sha(path.read_bytes()),sourceChanges=plan['sourceChanges'],constantsAdded=9,
        referencesReplaced=plan['referencesReplaced'],
        metadataNegativeVectors=negatives,allMainAndOtherInputsPreserved=True,allOriginalOracleTokensRestored=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()



