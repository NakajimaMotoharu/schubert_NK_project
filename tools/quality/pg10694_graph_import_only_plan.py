"""Three exact import-only edits; Test bodies, fixtures and dynamic HOLD stay unchanged."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10694-graph-import-only-plan-v1'
TESTS = ('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/ApiStartupGraph330Test.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/TemporaryFailureGraph329Test.java',
    'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebStartupGraph330Test.java')
MEMBERS = ('assertArrayEquals','assertDoesNotThrow','assertEquals','assertNull','assertSame','assertThrows')
OLD = 'import static org.junit.jupiter.api.Assertions.*;'
NEW = '\n'.join('import static org.junit.jupiter.api.Assertions.'+name+';' for name in MEMBERS)


def validate(before,after):
    if before.count(OLD) != 1 or canonical(after) != canonical(before.replace(OLD,NEW)):
        raise ValueError('only six explicit JUnit imports replacing one wildcard allowed')
    calls = set(re.findall(r'\b(assert\w+)\s*\(',after))
    if calls != set(MEMBERS):
        raise ValueError('exact used JUnit member set required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    assert normal['source'] == '370fd74f6f170a18bc1bf959aa9fceced0def15a' and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['api']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in TESTS)
    rows,negatives = [],0
    for path in TESTS:
        before = (snapshot/path).read_text()
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][path]
        validate(before,after)
        for invalid in (after.replace('import static org.junit.jupiter.api.Assertions.assertSame;\n','',1),
            after.replace('assertSame(', 'assertEquals(',1),after.replace(NEW,NEW+'\nimport static org.junit.jupiter.api.Assertions.fail;')):
            assert invalid != after
            try:
                validate(before,invalid)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('unrelated source/missing/extra import change accepted')
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            removedWildcardImports=1,explicitStaticImports=list(MEMBERS),bodyTokensPreserved=True,dynamicStatus='NOT_EXECUTED_HOLD'))
    assert negatives == 9
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=normal['source'],invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),sourceChanges=rows,metadataNegativeVectors=9,
        allOtherInputBytesPreserved=True,productTestsExecuted=0,productCodeExecuted=False,
        graphNineDynamicHoldMaintained=True,coverage=None,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
