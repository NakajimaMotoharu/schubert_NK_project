"""Original exact58/5 ordinary JUnit over actual fresh normal six artifacts; memory only."""
import scoped_prometheus_host as run

SOURCE = '7cba540ba7213e390d21ff46db73420caa5056e4'
COMPILE = run.host.W / 'pg8270-summary-encoder-six-compile-v1'
COMPILE_SHA = '41ab25f9bbaf9f8df32d600fea3c04c59eaf492bc1cbb77fcc0a6c22555f6428'
COUNTS = {'PrometheusSummaryExporterTest': 24, 'ExactDurationMeterRegistryTest': 10,
          'DbQueryDurationMetricRecorderTest': 9, 'MqProcessingDurationMetricRecorderTest': 9,
          'ApiSummaryExporterContractTest': 6}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8272-summary-encoder-host-v1'
    run.OUT = run.host.BASE / 'PG8272-summary-encoder-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.TEST_SOURCE_OVERRIDES = {'PrometheusSummaryExporterTest': run.host.ROOT / 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/monitoring/PrometheusSummaryExporterTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8272-SUMMARY-ENCODER'
    run.FIXTURES = {}
    run.main()
