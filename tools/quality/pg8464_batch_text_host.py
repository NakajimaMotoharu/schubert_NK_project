"""New Batch closed text24 plus actual memory/parser8, original32/2 only."""
import scoped_prometheus_host as run

SOURCE = '441158e6eda607cb2cb24a192d73555740cb27a9'
COMPILE = run.host.W / 'pg8462-batch-text-six-compile-v1'
COMPILE_SHA = '0f0f417d1605188ca9b35f3178a6dbd181a445b297747200a07da722729bf637'
COUNTS = {'BatchMetricTextTest': 24, 'BatchMetricTextContractTest': 8}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8464-batch-text-host-v1'
    run.OUT = run.host.BASE / 'PG8464-batch-text-host-v1'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/BatchMetricTextJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/BatchMetricTextContractTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8464-BATCH-TEXT'
    run.FIXTURES = {}
    run.main()

