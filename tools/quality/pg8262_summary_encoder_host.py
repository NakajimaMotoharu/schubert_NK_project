"""Original exact58/5 ordinary JUnit over actual fresh normal six artifacts; memory only."""
import scoped_prometheus_host as run

SOURCE = 'b978c6832fe07ec65c162ab90d8bfe0bbddb8034'
COMPILE = run.host.W / 'pg8260-summary-encoder-six-compile-v1'
COMPILE_SHA = '161b14ae3bccce95b99ff06ded198d1210c3e0bed6a0b866380358415e7a19ce'
COUNTS = {'PrometheusSummaryExporterTest': 24, 'ExactDurationMeterRegistryTest': 10,
          'DbQueryDurationMetricRecorderTest': 9, 'MqProcessingDurationMetricRecorderTest': 9,
          'ApiSummaryExporterContractTest': 6}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8262-summary-encoder-host-v1'
    run.OUT = run.host.BASE / 'PG8262-summary-encoder-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.TEST_SOURCE_OVERRIDES = {'PrometheusSummaryExporterTest': run.host.ROOT / 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/monitoring/PrometheusSummaryExporterTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8262-SUMMARY-ENCODER'
    run.FIXTURES = {}
    run.main()
