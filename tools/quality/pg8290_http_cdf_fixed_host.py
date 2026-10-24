"""BUG1696 current source original32/4, one exec; independent route fixture mandatory."""
import scoped_prometheus_host as run

SOURCE = 'f1a898b58a893837582b06861b33863407792139'
COMPILE = run.host.W / 'pg8288-http-cdf-six-compile-v1'
COMPILE_SHA = '302163c1bcbbf42bae2a6867b04c25ff26b71930c31ec724f236e9b79b76f7d6'
COUNTS = {'OverflowSafeHttpMeterRegistryTest': 12, 'HttpMetricRecorderTest': 10,
          'HttpMetricContractTest': 6, 'HttpCdfLifetimeContractTest': 4}
FIXTURE = 'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA = '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8290-http-cdf-fixed-host-v1'
    run.OUT = run.host.BASE / 'PG8290-http-cdf-fixed-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/HttpCdfFixedJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/HttpCdfLifetimeContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8290-HTTP-CDF-FIXED'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
