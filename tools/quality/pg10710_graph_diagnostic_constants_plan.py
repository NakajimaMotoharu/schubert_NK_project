"""Four Test-only same-value constants,20 exact String tokens; no fixture execution."""
import difflib
from pathlib import Path
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from public_java_digest_provenance import LEX
from pg10694_graph_import_only_plan import TESTS

OUT = data.BASE/'PG10710-graph-diagnostic-constants-plan-v1'
BASE = '0a7ff657115228d6cdde3820b5f2ae36ac7f3186'
CONSTANTS = {
    'ApiStartupGraph330Test':(('PUBLIC_DIAGNOSTIC','"PUBLIC"',5),),
    'TemporaryFailureGraph329Test':(('PUBLIC_ROOT_DIAGNOSTIC','"PUBLIC root"',4),('PUBLIC_NEXT_DIAGNOSTIC','"PUBLIC next"',5)),
    'WebStartupGraph330Test':(('PUBLIC_DIAGNOSTIC','"PUBLIC"',6),),
}


def transformed(before,path):
    constants = CONSTANTS[Path(path).stem]
    table = {value:name for name,value,_ in constants}
    tokens = list(LEX.finditer(before))
    for name,value,count in constants:
        assert sum(m.group() == value for m in tokens) == count
        assert not any(m.group() == name for m in tokens)
    result = before
    for match in reversed(tokens):
        if match.group() in table:
            result = result[:match.start()]+table[match.group()]+result[match.end():]
    header = 'final class '+Path(path).stem+' {\n'
    assert result.count(header) == 1
    declarations = ''.join('  private static final String '+name+' = '+value+';\n' for name,value,_ in constants)
    return result.replace(header,header+declarations+'\n',1)


def validate(before,after,path):
    if canonical(after) != canonical(transformed(before,path)):
        raise ValueError('only four same-value declarations and20exact String references allowed')


def baseline():
    path = data.BASE/'PG10698-graph-import-six-compile-v1/manifest.json'
    normal = data.read_checked(path,'7177fe941af4b6df2f2237112b0f3cc5eb9a82f21f8ef22c34eca6674eec1338')
    assert normal['source'] == BASE and normal['actualExit'] == normal['testsExecuted'] == 0
    return normal,Path(normal['jars']['api']['path']).parent.parent.parent.parent


def emit():
    _,snapshot = baseline()
    patch = '*** Begin Patch\n'
    for path in TESTS:
        before = (snapshot/path).read_text()
        assert (data.ROOT/path).read_text() == before
        after = transformed(before,path)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'
        for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]:
            patch += ('@@' if line.startswith('@@') else line)+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot = baseline()
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in TESTS)
    rows,negatives = [],0
    for path in TESTS:
        before = (snapshot/path).read_text()
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][path]
        validate(before,after,path)
        name,value,_ = CONSTANTS[Path(path).stem][0]
        invalids = (after.replace(name+' = '+value,name+' = "WRONG"',1),
            after.replace('assertSame(', 'assertEquals(',1),after.replace(name,'UNREVIEWED_DIAGNOSTIC',1))
        for invalid in invalids:
            assert invalid != after
            try:
                validate(before,invalid,path)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('unapproved source change accepted')
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            constants=[dict(name=n,literal=v,references=c) for n,v,c in CONSTANTS[Path(path).stem]]))
    assert negatives == 9
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,sourceChanges=rows,
        constantsAdded=4,literalReferencesReplaced=20,metadataNegativeVectors=9,allOtherInputBytesPreserved=True,
        productTestsExecuted=0,graphNineDynamicHoldMaintained=True,coverage=None,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
