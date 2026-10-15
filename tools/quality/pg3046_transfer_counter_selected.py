"""Independent signed counters plus existing real-FD TransferCleanup whole class."""
import inspect
import pg3044_expiry_boundary_selected as expiry

TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/TransferCleanupTest.java'
FILES = [TEST, 'tools/quality/vm/050_s1/SelectedClassContractLauncher.java', 'tools/quality/vm/050_s1/NativeCoverageXml471.java']


def server():
    raw = expiry.server().replace('PG3044', 'PG3046').replace('ExpiryWorkerRequestTest', 'TransferCleanupTest').replace('platform.TransferCleanupTest', 'file.TransferCleanupTest')
    start = raw.index("{'ereq3042001")
    end = raw.index('}.issubset(names)', start)
    raw = raw[:start] + "{'nullInvalidIdentityAndRootModeRefuseWithoutMutation','transfer001DeletesOldRegularFilesAndOnlyEmptyCanonicalDatesKeepsRoot','transfer002KeepsBoundaryFutureUnknownSymlinkHardlinkBadModeAndDepthThree','transfer003RetainedRootIsNotRedirectedAndFailedGuardDoesNotDelete'" + raw[end:]
    raw = raw.replace('dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry$PriorExpiry', 'dev/codex/schubert/nk/batch/file/TransferCleanup$Outcome')
    compile(raw, '<real transfer whole class and signed count oracle>', 'exec')
    return raw


def main():
    raw = inspect.getsource(expiry.main).replace('pg3044-expiry-boundary-selected-v1', 'pg3046-transfer-counter-selected-v1').replace('PG3044-candidate-v1', 'PG3046-candidate-v1')
    ns = {**expiry.__dict__, 'FILES': FILES, 'TEST': TEST, 'server': server}
    exec(compile(raw, '<transfer exact Test-only inputs>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
