"""Exact qualified Main, independent seven expiry request tests, no guest operation."""
import pg2938_extra_row_selected as previous

TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ExpiryWorkerRequestTest.java'
FILES = [TEST, 'tools/quality/vm/050_s1/SelectedClassContractLauncher.java', 'tools/quality/vm/050_s1/NativeCoverageXml471.java']


def server():
    raw = previous.server().replace('PG2938', 'PG3044').replace('source-full-PG2930', 'source-full-PG3026').replace('repository.BackupFailureSnapshotTest', 'platform.ExpiryWorkerRequestTest').replace('BackupFailureSnapshotTest.xml', 'ExpiryWorkerRequestTest.xml')
    start = raw.index("{'cfdb2916001")
    end = raw.index('}.issubset(names)', start)
    raw = raw[:start] + "{'ereq3042001PriorBoundaryAndNullContractNeverAuthorizeCleanup','ereq3042002EveryRequiredFieldAndPriorPrecisionRejectsWithErasure'" + raw[end:]
    raw = raw.replace('dev/codex/schubert/nk/batch/repository/BackupFailureSnapshot', 'dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry$PriorExpiry')
    raw = raw.replace("require(all(counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']))", '# Measure without converting remaining branches to PASS.')
    raw = raw.replace("'targetClassFour100':True", "'targetClassFour100':all(counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])")
    compile(raw, '<exact seven expiry tests and measured counter>', 'exec')
    return raw


def main():
    raw = previous.prior.transport_body().replace('pg2916-failed-pair-boundary-selected-v1', 'pg3044-expiry-boundary-selected-v1').replace('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3028-extra-row-full-qualified-v1').replace('3680', '3685')
    raw = raw.replace("libraries=dict(old['libraries'])", "libraries=dict(old['libraries'])\n    libraries.update(json.loads((W/'pg3030-current-resume-native-qualified-v1/input.safe.json').read_bytes())['libraries'])")
    ns = {**previous.prior.prior.prior.__dict__, 'FILES': FILES, 'TEST': TEST, 'SLOT': 'PG3044-candidate-v1', 'SERVER': server()}
    exec(compile(raw, '<new-only expiry boundary input transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
