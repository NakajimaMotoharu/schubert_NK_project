"""Invert six explicit normal-close assertions and two imports to the preserved failed-build source."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10996-form-close-assert-source-post-v1'
PREFIX = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form/'
COUNTS = {'UserCreateFormTest':{'form':3},'QuestionSubmitFormTest':{'first':2,'invalid':1}}


def replace_exact(tokens,pattern,replacement,count):
    found = [i for i in range(len(tokens)-len(pattern)+1) if tokens[i:i+len(pattern)] == pattern]
    if len(found) != count:
        raise ValueError('exact existing close assertion/import site count')
    for i in reversed(found):
        tokens[i:i+len(pattern)] = replacement


def inverse(stem,before,after):
    tokens = canonical(after)
    replace_exact(tokens,canonical('import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;'),[],1)
    for variable,count in COUNTS[stem].items():
        replace_exact(tokens,canonical('assertDoesNotThrow('+variable+'::close);'),canonical(variable+'.close();'),count)
    if tokens != canonical(before):
        raise ValueError('only six normal-close assertions and imports; no suppression or oracle change')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    previous_path = data.BASE/'PG11000-form-lifecycle-six-compile-v1/manifest.json'
    previous = data.read_checked(previous_path,'060cfc19749da8f19e561fb08312cad26518c2b2ba582912888b39135281476a')
    assert previous['actualExit'] == 1 and previous['testsExecuted'] == 0
    assert previous['source'] == '9e001bc08b73bc03fc67f1489061e1b2168660b8'
    snapshot = Path(previous['jars']['protocol']['path']).parent.parent.parent.parent
    paths = {PREFIX+n+'.java' for n in COUNTS}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in previous['begin']['inputHashes'].items() if p not in paths)
    rows,negatives = [],0
    for stem,counts in COUNTS.items():
        path = PREFIX+stem+'.java'
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode()) == previous['begin']['inputHashes'][path]
        inverse(stem,before,after)
        variable = next(iter(counts))
        bads = [after.replace('assertDoesNotThrow','assertThrows',1),after.replace('@Test','@Disabled',1),
            after.replace(variable+'::close',variable+'::toRequest',1)]
        for bad in bads:
            assert bad != after
            try:
                inverse(stem,before,bad)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('changed normal-close contract or unrelated assertion accepted')
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),normalCloseAssertions=sum(counts.values())))
    assert negatives == 6 and sum(r['normalCloseAssertions'] for r in rows) == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=previous['source'],invocation=invocation,
        priorBuildManifestSha256=data.sha(previous_path.read_bytes()),priorBuildExit=1,sourceChanges=rows,
        normalCloseAssertions=6,staticImportsAdded=2,metadataNegativeVectors=negatives,allOtherInputsAndMainPreserved=True,
        existingTwrAndClosedFailureAssertionsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,
        suppressionsAdded=False,newAccepted=0,relatedBugs=['BUG-1888']))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
