"""One correct same-value result name and three ordinal constants in five conditions."""
import difflib
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from public_java_digest_provenance import LEX

BASE = '95894757e2bd7f392262497ea620873430ccc5f1'
OUT = data.BASE/'PG10628-query-semantic-constant-plan-v1'
LOG = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogQueryApplicationServiceTest.java'
USER = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQueryApplicationServiceTest.java'
OLD,NEW = 'SYSTEM_ERROR_RESULT','IDEMPOTENT_RESULT'
ORDINALS = [('FIXTURE_FIRST_COMMIT_ORDINAL',1,3),('FIXTURE_SECOND_COMMIT_ORDINAL',2,1),('FIXTURE_THIRD_COMMIT_ORDINAL',3,1)]


def transformed(before,path):
    if path == USER:
        assert before.count(OLD) == 8 and NEW not in before
        return before.replace(OLD,NEW)
    header = 'class LogQueryApplicationServiceTest {\n'
    assert before.count(header) == 1
    block = ''.join('  private static final int '+n+' = '+str(v)+';\n' for n,v,_ in ORDINALS)
    result = before.replace(header,header+block,1)
    for name,value,count in ORDINALS:
        old = f'if (f.commits.get() == {value})'
        assert result.count(old) == count
        result = result.replace(old,f'if (f.commits.get() == {name})')
    return result


def validate(before,after,path):
    if canonical(after) != canonical(transformed(before,path)):
        raise ValueError('only same-value rename and five ordinal conditions; other semantics immutable')


def changes():
    return {p:subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT).decode() for p in (LOG,USER)}


def emit():
    print('*** Begin Patch')
    for path,before in changes().items():
        assert (data.ROOT/path).read_text() == before
        after = transformed(before,path)
        print('*** Update File: '+str(data.ROOT/path))
        for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]:
            print('@@' if line.startswith('@@') else line)
    print('*** End Patch')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10612-log-cleanup-literal-compile-v1/manifest.json',
        '7e484e3e66d5f8b678c933a8628d40e4ecb7d145d1f426d8372c9e22d411fcf1')
    assert normal['source'] == BASE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in (LOG,USER))
    rows, negatives = [], 0
    for path,before in changes().items():
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][path]
        validate(before,after,path)
        samples = [after.replace('assertEquals(0,','assertEquals(999,',1)]
        if path == USER:
            samples += [after.replace(NEW,OLD),after.replace('"0200"','"9000"',1)]
        else:
            samples += [after.replace('FIXTURE_FIRST_COMMIT_ORDINAL = 1','FIXTURE_FIRST_COMMIT_ORDINAL = 2'),
                        after.replace('if (f.commits.get() == FIXTURE_FIRST_COMMIT_ORDINAL)','if (f.commits.get() == 1)',1)]
        for sample in samples:
            assert sample != after
            try:
                validate(before,sample,path)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('invalid source semantics accepted')
        token_values = [m.group() for m in LEX.finditer(after)]
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            newResultIdentifierReferences=token_values.count(NEW) if path == USER else None,
            ordinalConditionalReferences=5 if path == LOG else None))
    assert negatives == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        sourceChanges=rows,renamedResultIdentifier=1,ordinalConstants=3,ordinalConditionalReferences=5,
        metadataNegativeVectors=negatives,allOtherOriginalTokensPreserved=True,
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        emit()
    else:
        assert not sys.argv[1:]
        main()
