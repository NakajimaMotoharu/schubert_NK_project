"""Independent inverse constant fold to the original complete token stream; no test execution."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10842_web_view_duplicate_source_post import inverse

OUT = data.BASE/'PG10948-form-literal-source-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10946-form-literal-plan-v1/manifest.json'
    plan = data.read_checked(path,'e2832f3f6cee4a408c9c6119b81968483be617d694c922149a7cdb1445b34c59')
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert plan['actualExit'] == 0 and plan['constantsAdded'] == 13 and len(plan['sourceChanges']) == 2
    changed = {r['path'] for r in plan['sourceChanges']}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives = 0
    for row in plan['sourceChanges']:
        before,after = (snapshot/row['path']).read_text(),(data.ROOT/row['path']).read_text()
        assert data.sha(before.encode()) == row['beforeSha256'] and data.sha(after.encode()) == row['sha256']
        inverse(before,after,row['constants'])
        first = row['constants'][0]
        declaration = 'private static final String '+first['name']+' = '+first['literal']+';'
        assert declaration in after
        for bad in (after.replace(first['literal'],'"wrong-fixture"',1),after.replace('@Test','@Disabled',1),after.replace(declaration,'',1)):
            assert bad != after
            try:
                inverse(before,bad,row['constants'])
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('changed oracle accepted')
    assert negatives == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,planManifestSha256=data.sha(path.read_bytes()),
        sourceBefore=normal['source'],sourceChanges=plan['sourceChanges'],constantsAdded=13,referencesReplaced=plan['referencesReplaced'],
        metadataNegativeVectors=negatives,allOtherInputsAndMainPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
