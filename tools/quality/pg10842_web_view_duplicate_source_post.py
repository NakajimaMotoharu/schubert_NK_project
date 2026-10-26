"""Independent inverse55Web view fixture constants and unrelated-token/negative checks; no target execution."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded

OUT = data.BASE/'PG10842-web-view-duplicate-source-post-v1'


def inverse(before,after,rows):
    values = canonical(after)
    for row in rows:
        declaration = canonical('private static final String '+row['name']+' = '+row['literal']+';')
        positions = [i for i in range(len(values)-len(declaration)+1) if values[i:i+len(declaration)] == declaration]
        if len(positions) != 1:
            raise ValueError('exact same-value fixture declaration required')
        i = positions[0]
        del values[i:i+len(declaration)]
        if values.count(row['name']) != row['references']:
            raise ValueError('all original literal reference sites required')
        literal = canonical(row['literal'])
        assert len(literal) == 1
        values = [literal[0] if token == row['name'] else token for token in values]
    if folded(values) != canonical(before):
        raise ValueError('unrelated assertion/fixture/input changed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10840-web-view-duplicate-plan-v1/manifest.json'
    plan = data.read_checked(path,'884adb2d7f9e25bf2a613ad60e8aa7b1c603eac97e2ccd68227b157249e00ba3')
    normal = data.read_checked(data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json',
        'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert plan['actualExit'] == 0 and plan['constantsAdded'] == 55 and len(plan['sourceChanges']) == 8
    changed = {r['path'] for r in plan['sourceChanges']}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negative_count = 0
    for row in plan['sourceChanges']:
        before,after = (snapshot/row['path']).read_text(),(data.ROOT/row['path']).read_text()
        assert data.sha(before.encode()) == row['beforeSha256'] and data.sha(after.encode()) == row['sha256']
        inverse(before,after,row['constants'])
        first = row['constants'][0]
        declaration = 'private static final String '+first['name']+' = '+first['literal']+';'
        assert declaration in after
        for bad in (after.replace(first['literal'],'"wrong-fixture-value"',1),
            after.replace('@Test','@Disabled',1),after.replace(declaration,'',1)):
            assert bad != after
            try:
                inverse(before,bad,row['constants'])
            except ValueError:
                negative_count += 1
            else:
                raise AssertionError('changed fixture/assertion/declaration accepted')
    assert negative_count == 24
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,planManifestSha256=data.sha(path.read_bytes()),
        sourceBefore=normal['source'],sourceChanges=plan['sourceChanges'],constantsAdded=55,referencesReplaced=plan['referencesReplaced'],
        metadataNegativeVectors=33,allOtherInputsAndMainPreserved=True,productTestsExecuted=0,coverage=None,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
