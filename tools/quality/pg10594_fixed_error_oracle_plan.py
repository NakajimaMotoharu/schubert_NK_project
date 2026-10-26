"""Four expected-only fixed diagnostics; original fault Test bodies never execute."""
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

BASE = 'c91916e8fe1d46768b4ffcd8607164e973aa1bde'
OUT = data.BASE/'PG10594-fixed-error-oracle-plan-v2'
API = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/'
CHANGES = {
    API+'log/LogQueryApplicationServiceTest.java': ('TemporaryInfrastructureException', 'request transaction is unavailable', 'error', 'WBS-P010-04'),
    API+'admin/UserQueryApplicationServiceTest.java': ('TemporaryInfrastructureException', 'request transaction is unavailable', 'error', 'WBS-P010-01'),
    API+'admin/UserQueryReplayServiceTest.java': ('TemporaryInfrastructureException', 'request transaction is unavailable', 'e', 'WBS-P010-01'),
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/CleanupStepRepositoryTest.java': ('BatchRepositoryException', 'batch repository operation failed', 'e', 'WBS-P017-07'),
}


def statements(values):
    kind, message, actual, _ = values
    return (f'    assertEquals(new {kind}().getMessage(), {actual}.getMessage());\n',
            f'    assertEquals("{message}", {actual}.getMessage());\n')


def validate(before, after, values):
    old, new = statements(values)
    if before.count(old) != 1 or after.count(new) != 1 or old in after:
        raise ValueError('one independent literal expected required')
    if after.replace(new, old, 1) != before:
        raise ValueError('all other original bytes and assertions preserved')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    assert normal['source'] == BASE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in CHANGES)
    rows, rejected = [], 0
    for p,values in CHANGES.items():
        before = subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT).decode()
        after = (data.ROOT/p).read_text()
        assert data.sha(before.encode()) == normal['begin']['inputHashes'][p]
        validate(before,after,values)
        old,new = statements(values)
        samples = [after.replace(values[1], 'incorrect diagnostic', 1),
                   after.replace(new,old,1),
                   after.replace('assertEquals(0, '+values[2]+'.getSuppressed().length);',
                                 'assertEquals(1, '+values[2]+'.getSuppressed().length);',1)]
        for sample in samples:
            assert sample != after
            try:
                validate(before,sample,values)
            except ValueError:
                rejected += 1
        rows.append(dict(path=p,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            expected=values[1],canonicalOwner=values[3],canonicalCostOwner=values[3]))
    assert rejected == 12
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        sourceChanges=rows,normalManifestSha256=data.sha((data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json').read_bytes()),
        expectedOnlyChanges=4,allOtherSourceBytesPreserved=True,metadataNegativeVectors=rejected,
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,
        externalActions=0,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
