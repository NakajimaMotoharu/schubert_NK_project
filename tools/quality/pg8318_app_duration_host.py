"""Correct app owners, original independent52/4; no generic Bootstrap metric responsibility."""
import scoped_prometheus_host as run

SOURCE = 'd496e7430d70a9edb4092c2b09ca78b8ecfd9004'
COMPILE = run.host.W / 'pg8316-app-duration-six-compile-v1'
COMPILE_SHA = '2b979a3b19cb662a6c74d42dc48b426ac9086d34c312928e093a434b88839196'
COUNTS = {'ApiDurationMetricExporterTest': 24, 'WebDurationMetricExporterTest': 16,
          'ApiSummaryExporterContractTest': 6, 'WebTimerExporterContractTest': 6}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8318-app-duration-host-v1'
    run.OUT = run.host.BASE / 'PG8318-app-duration-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/AppDurationExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebTimerExporterContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.TEST_SOURCE_OVERRIDES = {
        'WebDurationMetricExporterTest': run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDurationMetricExporterTest.java',
        'ApiSummaryExporterContractTest': run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterContractTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8318-APP-DURATION'
    run.FIXTURES = {}
    run.main()
