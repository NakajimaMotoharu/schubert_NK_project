"""SSC240 fixed candidate affected host suites; no VM or formal acceptance."""
import pg743_closing_selected as selected
selected.D = selected.W / 'pg854-completed-reference-selected-v1'
selected.TESTS = {'batch': [
    'MaintenanceRunFilesTest', 'MorningOriginalCompletionTest',
    'MorningNewRunAdmissionTest', 'MorningResumeAdmissionTest',
    'MorningStartupLaunchOwnerTest', 'MorningBackupCompletionTest',
    'MorningCleanupCompletionTest', 'MorningBackupObservedCompletionTest',
    'CleanupTerminalRepositoryTest']}
if __name__ == '__main__':
    import inspect
    raw = inspect.getsource(selected.main)
    raw = raw.replace('src/schubert-nk-bootstrap,src/schubert-nk-api', 'src/schubert-nk-batch')
    raw = raw.replace('PG743-closing-selected-v1', 'PG854-completed-reference-selected-v1')
    raw = raw.replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172', '2a0d5aa392c85a1dc12a1cdb423978e8500895b8')
    namespace = dict(selected.__dict__)
    exec(compile(raw, '<854 affected suites fixed source>', 'exec'), namespace)
    namespace['main']()
