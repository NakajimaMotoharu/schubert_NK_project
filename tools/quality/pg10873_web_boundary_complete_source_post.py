"""Independent whole-token inverse of four numeric fixtures after compound-condition correction."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10873-web-boundary-complete-source-post-v1'
ITEMS = [('LogSearchTemplateTest',[('PAGE_SIZE_BOUNDARY','100',1)]),
         ('ScenarioSearchTemplateTest',[('MIDDLE_PAGE','2',2),('FIRST_PAGE','1',1),('PAGE_SIZE_BOUNDARY','100',1)])]


def inverse(before,after,constants):
    values = canonical(after)
    for name,literal,count in constants:
        decl = canonical('private static final int '+name+' = '+literal+';')
        matches = [i for i in range(len(values)-len(decl)+1) if values[i:i+len(decl)] == decl]
        if len(matches) != 1:
            raise ValueError('one exact boundary declaration')
        i = matches[0]
        del values[i:i+len(decl)]
        if values.count(name) != count:
            raise ValueError('all original references')
        expanded = []
        for token in values:
            expanded.extend(canonical(literal) if token == name else [token])
        values = expanded
    if values != canonical(before):
        raise ValueError('other token changed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original = data.read_checked(data.BASE/'PG10846-web-view-six-compile-v1/manifest.json',
        '8ac965984ed15b14e172677cf0c254012b70bece197feca7fea137df98cc751e')
    snapshot = Path(original['jars']['protocol']['path']).parent.parent.parent.parent
    changes,negatives = [],0
    for file,constants in ITEMS:
        path = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+file+'.java'
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode()) == original['begin']['inputHashes'][path]
        inverse(before,after,constants)
        for name,literal,_ in constants:
            decl = 'private static final int '+name+' = '+literal+';'
            for bad in (after.replace(decl,decl.replace(literal,'99'),1),after.replace(decl,'',1),after.replace('@Test','@Disabled',1)):
                assert bad != after
                try: inverse(before,bad,constants)
                except ValueError: negatives += 1
                else: raise AssertionError('bad constant metadata accepted')
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=constants))
    assert negatives == 12 and len(changes) == 2
    changed = {r['path'] for r in changes}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in original['begin']['inputHashes'].items() if p not in changed)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=original['source'],invocation=invocation,
        sourceChanges=changes,constantsAdded=4,referencesReplaced=5,metadataNegativeVectors=12,
        allOtherInputsAndMainPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
