"""Eleven same-value Test-local constants; metadata only, no fixture execution."""
import difflib
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10339_result_profile_oracle_post_v2 import folded

BASE = '095720ee2766cd9f0bd441ee4bc019833fde8184'
OUT = data.BASE/'PG10608-log-cleanup-literal-plan-v1'
LOG = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogQueryApplicationServiceTest.java'
CLEANUP = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/CleanupStepRepositoryTest.java'
VALUES = {
    LOG: [('FIXTURE_RESULT_SUCCESS','0000',13),('FIXTURE_RESULT_IDEMPOTENT_SUCCESS','0200',12),
          ('FIXTURE_RESULT_FORBIDDEN','0103',4),('FIXTURE_INBOX_COUNT_SQL','select count(*) from schubert.request_inbox',6),
          ('FIXTURE_NO_CONNECTION_FAULT','none',4),('FIXTURE_IN_VM_BROKER_URL','vm://0',4),
          ('FIXTURE_DATABASE_FAULT_POINT','database',5)],
    CLEANUP: [('FIXTURE_STEP_TARGET_COUNT_COLUMN','step_target_count',4),
              ('FIXTURE_STEP_SUCCESS_COUNT_COLUMN','step_success_count',4),
              ('FIXTURE_QUESTION_TWO_COUNT_SQL','select count(*) from schubert.questions where id=2',4),
              ('FIXTURE_ROW_CLOSE_FAULT_POINT','row.close',4)],
}


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def declaration(name,value):
    return '  private static final String '+name+' = "'+value+'";\n'


def transformed(before,path):
    changes = []
    for name,value,count in VALUES[path]:
        assert name not in tokens(before)
        found = [m for m in LEX.finditer(before) if m.group() == '"'+value+'"']
        assert len(found) == count
        changes.extend((m.start(),m.end(),name) for m in found)
    result = before
    for start,end,name in sorted(changes,reverse=True):
        result = result[:start]+name+result[end:]
    header = ('class LogQueryApplicationServiceTest {' if path == LOG else 'final class CleanupStepRepositoryTest {')+'\n'
    assert result.count(header) == 1
    block = ''.join(declaration(name,value) for name,value,_ in VALUES[path])+'\n'
    return result.replace(header,header+block,1)


def validate(before,after,path):
    values = tokens(after)
    for name,value,count in VALUES[path]:
        item = tokens(declaration(name,value))
        starts = [i for i in range(len(values)-len(item)+1) if values[i:i+len(item)] == item]
        if len(starts) != 1:
            raise ValueError('one exact Test-local constant declaration required')
        i, = starts
        values = values[:i]+values[i+len(item):]
        if values.count(name) != count:
            raise ValueError('all original literal occurrences must use same constant')
        values = ['"'+value+'"' if token == name else token for token in values]
    if folded(values) != folded(tokens(before)):
        raise ValueError('all original tokens, independent literals and assertions immutable')


def changes():
    rows = {}
    for path in VALUES:
        before = subprocess.check_output(['git','show',BASE+':'+path],cwd=data.ROOT).decode()
        rows[path] = (before,transformed(before,path))
    return rows


def emit():
    print('*** Begin Patch')
    for path,(before,after) in changes().items():
        assert (data.ROOT/path).read_text() == before
        print('*** Update File: '+str(data.ROOT/path))
        for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]:
            print('@@' if line.startswith('@@') else line)
    print('*** End Patch')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10598-fixed-error-oracle-compile-v1/manifest.json',
        '9f88bf4302849e40fed8a699c391e7552d98af1e2038878d63b4fe4585b44077')
    assert normal['source'] == BASE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in VALUES)
    rows, rejected = [], 0
    for path,(before,_) in changes().items():
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][path]
        validate(before,after,path)
        name,value,_ = VALUES[path][0]
        samples = [after.replace('"'+value+'"','"WRONG"',1),
                   after.replace(name,name+'_UNKNOWN',1),
                   after.replace('assertEquals(0,','assertEquals(999,',1),
                   after.replace('select count(*)','select count(1)',1),
                   after.replace('assertEquals(0,','assertEquals(0 + 1,',1)]
        for sample in samples:
            assert sample != after
            try:
                validate(before,sample,path)
            except ValueError:
                rejected += 1
            else:
                raise AssertionError('invalid same-value transformation accepted')
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            constants=[dict(name=n,value=v,references=c) for n,v,c in VALUES[path]]))
    assert rejected == 10
    assert folded(tokens('"a" + 1')) == tokens('"a" + 1')
    assert folded(tokens('"a" + "b"')) == tokens('"ab"')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        sourceChanges=rows,constantsAdded=11,references=64,metadataNegativeVectors=rejected,
        allOriginalTokensPreserved=True,productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',
        coverage=None,externalActions=0,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        emit()
    else:
        assert not sys.argv[1:]
        main()
