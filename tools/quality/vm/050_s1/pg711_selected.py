"""One batch candidate group; fixed five other modules, explicit candidate delta only."""
from pathlib import Path
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = (R / 'pg707_selected.py').read_text()
    a = raw.index('    assert not subprocess.check_output'); b = raw.index('    assert hashlib.sha256', a)
    raw = raw[:a] + raw[b:]
    raw = replace(raw, (
        ('pg707-owner-negatives-v1', 'pg711-expiry-core-v1'),
        ("for module in ('api', 'batch'):", "for module in ('batch',):"),
        ('BootstrapAdminMainTest.xml', 'ExpiryResultContractTest.xml'),
        ('ApiProcessMainTest.xml', 'CleanupExpiryExecutionTest.xml'),
        ('MorningDatabaseSessionTest.xml', 'ExpiryOwnerTest.xml'),
        ("'src/schubert-nk-api,src/schubert-nk-batch'", "'src/schubert-nk-batch'"),
        ('BootstrapAdminMainTest,ApiProcessMainTest,MorningDatabaseSessionTest',
         'ExpiryResultContractTest,CleanupExpiryExecutionTest,ExpiryOwnerTest'),
        ("'allSixMainBytesUnchanged': outcome.returncode == 0", "'candidateChanged':True,'wholeSourceRegressionPending':True"),
        ("'productionSource': '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'", "'candidateSource':source,'installedVmProductionSource':'9bd50536f692610036a0ed8b83e0a8b35fe2a66f'"),
    ))
    before = """            assert classes(HOST / module / name) == classes(T / 'src' / ('schubert-nk-' + module) / 'target' / name)"""
    after = """            old=classes(HOST/module/name);new=classes(T/'src'/('schubert-nk-'+module)/'target'/name)
            if module!='batch':assert new==old
            else:
                assert sorted(new.keys()-old.keys())==['dev/codex/schubert/nk/batch/file/CleanupExpiryExecution$1.class','dev/codex/schubert/nk/batch/file/CleanupExpiryExecution$ExpiryWork.class']
                assert not old.keys()-new.keys()
                assert sorted(k for k in old if old[k]!=new[k])==['dev/codex/schubert/nk/batch/file/CleanupExpiryExecution.class']"""
    return replace(raw, ((before, after),))


if __name__ == '__main__':
    env = {'__file__': str(R / 'pg711_selected.py'), '__name__': 'expiry_candidate_only'}
    exec(compile(source(), '<candidate Expiry group>', 'exec'), env); env['main']()
