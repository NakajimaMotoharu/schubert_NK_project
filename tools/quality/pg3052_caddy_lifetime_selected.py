"""Whole fourteen Caddy lifetime tests using fixed independent manager/kernel/HTTP oracles."""
import inspect
import pg3044_expiry_boundary_selected as base

TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningCaddyReadinessTest.java'
FILES = [TEST, 'tools/quality/vm/050_s1/SelectedClassContractLauncher.java', 'tools/quality/vm/050_s1/NativeCoverageXml471.java']


def server():
    raw = base.server().replace('PG3044', 'PG3052').replace('ExpiryWorkerRequestTest', 'MorningCaddyReadinessTest')
    start = raw.index("{'ereq3042001")
    end = raw.index('}.issubset(names)', start)
    raw = raw[:start] + "{'caddy3052001ConstructorAndPostTlsGenerationDriftAlwaysRejects','caddy3052002EmbeddedBraceAndLiveNonzeroStartNeverBecomeReady'" + raw[end:]
    raw = raw.replace('dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry$PriorExpiry', 'dev/codex/schubert/nk/batch/platform/MorningCaddyReadiness')
    compile(raw, '<fourteen Caddy identity/lifetime tests>', 'exec')
    return raw


def main():
    raw = inspect.getsource(base.main).replace('pg3044-expiry-boundary-selected-v1', 'pg3052-caddy-lifetime-selected-v1').replace('PG3044-candidate-v1', 'PG3052-candidate-v1')
    ns = {**base.__dict__, 'FILES': FILES, 'TEST': TEST, 'server': server}
    exec(compile(raw, '<immutable Caddy lifetime Test inputs>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
