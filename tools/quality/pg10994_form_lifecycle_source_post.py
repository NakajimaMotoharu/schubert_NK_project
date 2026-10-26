"""Invert exactly four memory-fixture TWR scopes and two independent accessor assertions; no product run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10994-form-lifecycle-source-post-v1'
PREFIX = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form/'
EDITS = {
    'UserCreateFormTest':[
        ('create006ImmutableProjectionAndSecretLifetime','var form = UserCreateForm.bind(values)'),
        ('create008InvalidSecretsRemainAbsentAndClosedInvalidCannotSend','var form = UserCreateForm.bind(values)')],
    'QuestionSubmitFormTest':[
        ('qstForm007TerminalClosePreservesOtherOwners','var first = QuestionSubmitForm.bind(input("質問"))'),
        ('qstForm007TerminalClosePreservesOtherOwners','var invalid = QuestionSubmitForm.bind(input(""))')]}
ASSERTIONS = [
    'assertEquals(UUID.fromString(TOKEN), form.operationToken());',
    'assertThrows(IllegalStateException.class, first::operationToken);']


def positions(tokens,pattern,start=0,end=None):
    end = len(tokens) if end is None else end
    return [i for i in range(start,end-len(pattern)+1) if tokens[i:i+len(pattern)] == pattern]


def closing(tokens,opening):
    if tokens[opening] != '{':
        raise ValueError('block opening required')
    depth = 0
    for i in range(opening,len(tokens)):
        depth += (tokens[i] == '{')-(tokens[i] == '}')
        if depth == 0:
            return i
    raise ValueError('balanced complete block required')


def inverse(stem,before,after):
    tokens = canonical(after)
    if stem == 'QuestionSubmitFormTest':
        for statement in ASSERTIONS:
            pattern = canonical(statement)
            found = positions(tokens,pattern)
            if len(found) != 1:
                raise ValueError('one exact independent retained UUID/closed assertion')
            del tokens[found[0]:found[0]+len(pattern)]
    for method,declaration in EDITS[stem]:
        methods = positions(tokens,[method,'(',')'])
        if len(methods) != 1:
            raise ValueError('one original method declaration')
        begin = tokens.index('{',methods[0])
        end = closing(tokens,begin)
        header = canonical('try ('+declaration+') {')
        found = positions(tokens,header,begin,end)
        if len(found) != 1:
            raise ValueError('one exact original factory wrapped in TWR')
        i = found[0]
        body_start = i+len(header)-1
        body_end = closing(tokens,body_start)
        tokens = tokens[:i]+canonical(declaration+';')+tokens[body_start+1:body_end]+tokens[body_end+1:]
    if tokens != canonical(before):
        raise ValueError('only four TWR and two assertions; all existing oracle/input tokens preserved')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10978-four-form-literal-six-compile-v1/manifest.json',
        'ef9b0e1a6ca2a31d27fb23937b23568410204c0f48229b6e07d56e41799e897d')
    assert normal['source'] == '05e4428dd86e3197a5899a85e3292e1d27219513' and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    paths = {PREFIX+n+'.java' for n in EDITS}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in paths)
    rows,negatives = [],0
    for stem in EDITS:
        path = PREFIX+stem+'.java'
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][path]
        inverse(stem,before,after)
        bads = [after.replace('@Test','@Disabled',1),after.replace('assertTrue(','assertFalse(',1)]
        method,declaration = EDITS[stem][0]
        bads.append(after.replace('try ('+declaration+') {',declaration+'; {',1))
        if stem == 'QuestionSubmitFormTest':
            bads.append(after.replace('form.operationToken()','form.toRequest().operationToken()',1))
        for bad in bads:
            assert bad != after
            try:
                inverse(stem,before,bad)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('changed original fixture/oracle or missing lifecycle proof accepted')
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            twrScopesAdded=2,independentAccessorAssertionsAdded=2 if stem == 'QuestionSubmitFormTest' else 0))
    assert negatives == 7
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=rows,twrScopesAdded=4,independentAccessorAssertionsAdded=2,metadataNegativeVectors=negatives,
        allOtherInputsAndMainPreserved=True,existingGoldenAndAssertionsPreserved=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,relatedBugs=['BUG-1887']))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
