"""One Main domain name and one Test TWR owner; all original oracle/control tokens preserved."""
import difflib
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG12716-alert-threshold-plan-v1'
SOURCE_BEFORE = 'e353b1f49a740a426031fdc199f7ce8b26081971'
MAIN = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/AlertThresholds.java'
TEST = MAIN.replace('/main/','/test/').replace('.java','Test.java')
DECL = '  private static final int MAX_PERCENTAGE = 100;\n'
OPEN = '    var executor = Executors.newFixedThreadPool(4);\n'
OWNED = '    try (var executor = Executors.newFixedThreadPool(4)) {\n'


def raw(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n = data.read_checked(data.BASE/'PG12686-scenario-writer-six-compile-v1/manifest.json','20ef6bfc17fb7fdb9a7cab61c1d927bcb480ec36dffadbd0e5e7fc5c0ed23a9d')
    assert n['source'] == SOURCE_BEFORE and n['actualExit'] == n['testsExecuted'] == 0
    snapshot = Path(n['jars']['batch']['path']).parent.parent.parent.parent
    texts = {p:(snapshot/p).read_text() for p in [MAIN, TEST]}
    assert all(data.sha(t.encode()) == n['begin']['inputHashes'][p] for p,t in texts.items())
    return n, texts


def intended(old):
    a, b = old[MAIN], old[TEST]
    assert a.count('  private static final String INVALID') == a.count('if (value > 100)') == 1
    a = a.replace('  private static final String INVALID', DECL+'  private static final String INVALID',1).replace('if (value > 100)','if (value > MAX_PERCENTAGE)',1)
    assert b.count(OPEN) == 1 and b.endswith('    }\n  }\n}\n')
    b = b.replace(OPEN,OWNED,1)
    b = b[:-len('  }\n}\n')]+'    }\n  }\n}\n'
    return {MAIN:a, TEST:b}


def require(old, new):
    a = new[MAIN]
    assert a.count(DECL)==1 and raw(a).count('MAX_PERCENTAGE')==2
    a = a.replace(DECL,'',1).replace('if (value > MAX_PERCENTAGE)','if (value > 100)',1)
    assert raw(a) == raw(old[MAIN])
    tokens = raw(new[TEST])
    opening = raw(OWNED)
    positions = [i for i in range(len(tokens)) if tokens[i:i+len(opening)]==opening]
    assert len(positions)==1
    index=positions[0]
    tokens[index:index+len(opening)] = raw(OPEN)
    assert tokens[-4:] == ['}', '}', '}', '}']
    tokens.pop(-3)
    assert tokens == raw(old[TEST])


def emit():
    _, old = before()
    new = intended(old)
    require(old,new)
    patch = '*** Begin Patch\n'
    for path in [MAIN,TEST]:
        assert (data.ROOT/path).read_text()==old[path]
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(old[path].splitlines(),new[path].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    n,old = before()
    new = {p:(data.ROOT/p).read_text() for p in [MAIN,TEST]}
    require(old,new)
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items() if p not in new)
    vectors = []
    for path,a,b in [(MAIN,'MAX_PERCENTAGE = 100','MAX_PERCENTAGE = 99'),(MAIN,'if (value > MAX_PERCENTAGE)','if (value >= MAX_PERCENTAGE)'),(MAIN,'return warning ?','return critical ?'),(TEST,'index < 64','index < 63'),(TEST,'assertEquals(expected, future.get())','assertEquals(expected, expected)'),(TEST,'executor.shutdownNow();',''),(TEST,'awaitTermination(10,','awaitTermination(1,'),(TEST,'thresholds.filesystem(100,','thresholds.filesystem(99,'),(TEST,'@Test','@Disabled')]:
        bad = {**new,path:new[path].replace(a,b,1)}
        assert bad != new
        try:
            require(old,bad)
        except AssertionError:
            vectors.append(path+':'+a)
        else:
            raise AssertionError('changed independent oracle or owner accepted')
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2373_AlertThreshold上限命名・所有pool是正_単体テスト仕様書.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=SOURCE_BEFORE,invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in [MAIN,TEST]],mainCorrections=1,testCorrections=1,totalCorrections=2,metadataNegativeVectors=len(vectors),nonVacuousNegativeLabels=vectors,originalTests=14,originalSuites=1,allOtherInputsUnchanged=True,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
