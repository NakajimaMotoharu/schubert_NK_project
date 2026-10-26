"""Independent two numeric-boundary substitutions and whole-input preservation; no target run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10862-web-boundary-source-post-v1'
NAMES = [('LogSearchTemplateTest','PAGE_SIZE_BOUNDARY','100',1),
         ('ScenarioSearchTemplateTest','MIDDLE_PAGE','2',2)]


def inverse(before,after,name,literal,count):
    declaration = canonical('private static final int '+name+' = '+literal+';')
    values = canonical(after)
    matches = [i for i in range(len(values)-len(declaration)+1) if values[i:i+len(declaration)] == declaration]
    if len(matches) != 1:
        raise ValueError('one exact independent boundary declaration')
    i = matches[0]
    del values[i:i+len(declaration)]
    if values.count(name) != count:
        raise ValueError('all boundary references')
    expanded = []
    for token in values:
        expanded.extend(canonical(literal) if token == name else [token])
    if expanded != canonical(before):
        raise ValueError('other token changed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10846-web-view-six-compile-v1/manifest.json',
        '8ac965984ed15b14e172677cf0c254012b70bece197feca7fea137df98cc751e')
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changes = []
    negatives = 0
    for file,name,literal,count in NAMES:
        path = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+file+'.java'
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][path]
        inverse(before,after,name,literal,count)
        declaration = 'private static final int '+name+' = '+literal+';'
        assert declaration in after
        for bad in (after.replace(declaration,declaration.replace(literal,'99'),1),
                    after.replace(declaration,'',1),after.replace('@Test','@Disabled',1)):
            assert bad != after
            try:
                inverse(before,bad,name,literal,count)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('bad boundary metadata accepted')
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            constant=name,independentLiteral=literal,references=count))
    assert negatives == 6 and len(changes) == 2
    changed = {r['path'] for r in changes}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=changes,constantsAdded=2,referencesReplaced=3,metadataNegativeVectors=6,
        allOtherInputsAndMainPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
