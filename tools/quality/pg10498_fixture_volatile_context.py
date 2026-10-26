"""Read-only source context for ten unchanged synthetic Fixture volatile controls."""
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
OUT = data.BASE/'PG10498-fixture-volatile-context-v1'
FIELDS = {'count','code','responder','failureStage'}
METHOD = re.compile(r'@Test\s+void\s+(\w+)\s*\(\s*\)(?:\s+throws\s+[^{}]+)?\s*\{')
WRITE = re.compile(r'\b(\w+)\.(count|code|responder|failureStage)\s*=(?!=)')


def block_end(text,start):
    depth = 1
    for token in LEX.finditer(text,start):
        if token.group() == '{':
            depth += 1
        elif token.group() == '}':
            depth -= 1
            if depth == 0:
                return token.end()
    raise ValueError('balanced source block required')


def context(text):
    methods = []
    for match in METHOD.finditer(text):
        end = block_end(text,match.end())
        methods.append(dict(name=match[1],start=match.start(),end=end,body=text[match.end():end]))
    assert methods
    writes = []
    for match in WRITE.finditer(text):
        owners = [m for m in methods if m['start'] < match.start() < m['end']]
        assert len(owners) == 1 and match[1] == 'f'
        owner, = owners
        assert re.search(r'\bvar\s+f\s*=\s*new\s+Fixture\s*\(\s*\)',owner['body'])
        writes.append(dict(field=match[2],method=owner['name'],line=text.count('\n',0,match.start())+1,
            sourceLine=text.splitlines()[text.count('\n',0,match.start())].strip()))
    concurrent = [m for m in methods if 'Executors.newFixedThreadPool(' in m['body']]
    assert len(concurrent) == 1
    phase, = concurrent
    phase_writes = [r for r in writes if r['method'] == phase['name']]
    assert not phase_writes and 'new Fixture()' in phase['body'] and 'TimeUnit.SECONDS' in phase['body']
    rmw = re.findall(r'\b(?:f\.)?(?:count|code|responder|failureStage)\s*(?:\+\+|--|[+\-*/|&^]=)',text)
    assert not rmw and not re.search(r'\.set(?:Accessible|Int|Long)\(',text)
    fixture = re.search(r'\bclass\s+Fixture\b[^{}]*\{',text)
    assert fixture
    end = block_end(text,fixture.end())
    body = text[fixture.end():end]
    declarations = re.findall(r'\bvolatile\s+(?:int|String|BiFunction<UUID,\s*byte\[\],\s*byte\[\]>)\s+(\w+)\s*=',body)
    assert set(declarations) <= FIELDS and len(declarations) in (3,4)
    bare_writes = re.findall(r'(?<!\.)\b(count|code|responder|failureStage)\s*=(?!=)',body)
    assert sorted(bare_writes) == sorted(declarations)
    return dict(controlFields=sorted(declarations),writes=writes,
        localFixturePerWritingMethod=True,fixtureMethodControlWritesBeyondInitializers=0,
        concurrentMethod=phase['name'],concurrentMethodStartLine=text.count('\n',0,phase['start'])+1,
        concurrentControlWrites=0,readModifyWriteControls=0,reflectionMutationPresent=False,
        disposition='INTENTIONAL_INDIVIDUAL_TEST_CONTROL_PUBLICATION_NOT_PRODUCTION_SHARED_STATE',
        scope='Static individual-control visibility and read-only concurrency phase; no atomic aggregate transition is asserted and no dynamic execution/liveness certified.')


def contract(value):
    if len(value) != 3 or sum(len(r['context']['controlFields']) for r in value) != 10:
        raise ValueError('three source scopes and all ten nested controls required')
    for row in value:
        c = row['context']
        if not c['localFixturePerWritingMethod'] or c['concurrentControlWrites'] != 0 or c['readModifyWriteControls'] != 0 or c['fixtureMethodControlWritesBeyondInitializers'] != 0:
            raise ValueError('exact bounded single-control Test setup/immutable concurrency contract required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    static = data.read_checked(data.BASE/'PG10478-disjoint-six-literal-static-v1/manifest.json',
        '1cae3c256e3442adace66f78b521f981b119754d1edfeaef03ac0c2a4f73e4bc')
    proof = data.read_checked(data.BASE/'PG10482-disjoint-six-literal-post-v1/manifest.json',
        '1c4458f2db226efc0ffeb32bbbdaada06c7a25fd75b22fc7f03abe619f76beeb')
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    findings = [r for r in static['reports']['pmd']['details'] if r['rule'] == 'AvoidUsingVolatile']
    assert len(findings) == 10
    rows = []
    for cls in sorted({r['class'].split('.')[0] for r in findings}):
        path, = [p for p in static['sourceHashes'] if Path(p).stem == cls]
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == static['sourceHashes'][path] == proof['sourceHashes'][path]
        c = context(text)
        matched = [r for r in findings if r['class'].split('.')[0] == cls]
        assert sorted(r['variable'] for r in matched) == c['controlFields']
        for row in matched:
            assert row['class'].endswith('.Fixture') and text.splitlines()[int(row['beginline'])-1].strip().startswith('volatile ')
        rows.append(dict(path=path,sha256=static['sourceHashes'][path],findings=matched,context=c))
    contract(rows)
    import copy
    negatives = []
    for label,edit in [
        ('concurrent-control-write',lambda r:r[0]['context'].update(concurrentControlWrites=1)),
        ('read-modify-write',lambda r:r[0]['context'].update(readModifyWriteControls=1)),
        ('shared-fixture',lambda r:r[0]['context'].update(localFixturePerWritingMethod=False)),
        ('self-mutation',lambda r:r[0]['context'].update(fixtureMethodControlWritesBeyondInitializers=1)),
        ('nested-loss',lambda r:r[0]['context']['controlFields'].pop())]:
        damaged = copy.deepcopy(rows)
        edit(damaged)
        try:
            contract(damaged)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('unsupported publication context accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes={r['path']:r['sha256'] for r in rows},controlFields=10,sourceCount=3,
        contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),metadataNegativeVectors=negatives,
        originalRawFindings=26,previousPending=10,currentContextuallyApplicableFindings=0,currentPending=0,
        thread16PreviouslyContextual=True,suppressionsAdded=False,rawSourceOrReportsChanged=False,
        staticClassificationOnly=True,originalDynamicPtStatus='NOT_EXECUTED_HOLD',
        productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,externalActions=0,
        bug1837NamingIssueUnmodifiedAndOpen=True,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
