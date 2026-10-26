"""Independent inverse of twelve fixed literals, one private identifier and one boundary constant."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded

OUT = data.BASE/'PG11036-api-request-source-post-v1'


def remove(tokens,pattern):
    found = [i for i in range(len(tokens)-len(pattern)+1) if tokens[i:i+len(pattern)] == pattern]
    if len(found) != 1:
        raise ValueError('one exact same-value fixture declaration')
    i = found[0]
    del tokens[i:i+len(pattern)]


def inverse(stem,before,after,rows):
    tokens = canonical(after)
    if stem == 'QuestionSubmitRequestTest':
        remove(tokens,canonical('private static final int MAXIMUM_QUESTION_UTF8_BYTES = 4096;'))
        if tokens.count('MAXIMUM_QUESTION_UTF8_BYTES') != 1:
            raise ValueError('one original byte-limit reference')
        expanded = []
        for token in tokens:
            expanded += canonical('4096') if token == 'MAXIMUM_QUESTION_UTF8_BYTES' else [token]
        tokens = expanded
        if 'MESSAGE_ID' in canonical(before) or tokens.count('MESSAGE_ID') != canonical(before).count('MESSAGE'):
            raise ValueError('private identifier only, same reference count')
        tokens = ['MESSAGE' if token == 'MESSAGE_ID' else token for token in tokens]
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
    path = data.BASE/'PG11034-api-request-literal-plan-v1/manifest.json'
    plan = data.read_checked(path,'da263fb3fbf96b3d2de05be39b2c7e4787475f873e8a0b22509ba14e4e1e970b')
    normal = data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json',
        '5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed = {r['path'] for r in plan['sourceChanges']}
    assert len(changed) == 4 and plan['actualExit'] == 0 and plan['constantsAdded'] == 12
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
        if stem == 'QuestionSubmitRequestTest':
            bads += [after.replace('MAXIMUM_QUESTION_UTF8_BYTES = 4096','MAXIMUM_QUESTION_UTF8_BYTES = 4095',1),
                after.replace('MESSAGE_ID','MESSAGE',1)]
        for bad in bads:
            assert bad != after
            try:
                inverse(stem,before,bad,row['constants'])
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('changed expected/case/boundary/identifier accepted')
    assert negatives == 14
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],
        planManifestSha256=data.sha(path.read_bytes()),sourceChanges=plan['sourceChanges'],constantsAdded=12,
        referencesReplaced=plan['referencesReplaced'],privateIdentifierRenames=1,numericBoundaryConstants=1,
        metadataNegativeVectors=negatives,allMainAndOtherInputsPreserved=True,allOriginalOracleTokensRestored=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
