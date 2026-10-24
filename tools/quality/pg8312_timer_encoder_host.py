"""New Timer unit16/Web6 plus necessary Summary24/API6, one source/exec, no services."""
import scoped_prometheus_host as run

SOURCE = '1a066d08bf709e6a883fce1d289f9ce081d3bf54'
COMPILE = run.host.W / 'pg8310-timer-encoder-six-compile-v1'
COMPILE_SHA = '077b0cf7c0f526fc980d4ad9c1399e11cd4bad9f14865bc62aa09faeecb0b5f0'
COUNTS = {'PrometheusSummaryExporterTest': 24, 'PrometheusTimerExporterTest': 16,
          'ApiSummaryExporterContractTest': 6, 'WebTimerExporterContractTest': 6}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8312-timer-encoder-host-v1'
    run.OUT = run.host.BASE / 'PG8312-timer-encoder-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/TimerExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebTimerExporterContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/monitoring'
    run.TEST_SOURCE_OVERRIDES = {'ApiSummaryExporterContractTest': run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterContractTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8312-TIMER-ENCODER'
    run.FIXTURES = {}
    run.main()
