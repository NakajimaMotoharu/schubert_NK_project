"""New Counter16/Web6 plus necessary Web duration16/Web6, one original44/4 JVM."""
import scoped_prometheus_host as run

SOURCE = '30fe7bb8947cc8c5c1ac56838c4af4197afcc9df'
COMPILE = run.host.W / 'pg8334-web-counter-six-compile-v1'
COMPILE_SHA = 'a004aacb492e2e76c6122de3caadff0719d1837340be62919b6e3781fbed702a'
COUNTS = {'WebCounterMetricExporterTest': 16, 'WebDurationMetricExporterTest': 16,
          'WebCounterExporterContractTest': 6, 'WebTimerExporterContractTest': 6}
FIXTURE = 'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA = '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8336-web-counter-host-v1'
    run.OUT = run.host.BASE / 'PG8336-web-counter-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebCounterExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebCounterExporterContractTest.java'
    run.TEST_SOURCE_OVERRIDES = {'WebTimerExporterContractTest': run.host.ROOT / 'tools/quality/architecture/WebTimerExporterContractTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8336-WEB-COUNTER'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
