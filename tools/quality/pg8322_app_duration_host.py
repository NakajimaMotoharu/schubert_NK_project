"""Correct app owners, original independent52/4; no generic Bootstrap metric responsibility."""
import scoped_prometheus_host as run

SOURCE = '3968abacec2052b9e7b803702a3a9231f9209f26'
COMPILE = run.host.W / 'pg8320-app-duration-six-compile-v1'
COMPILE_SHA = '873d524e75f2826777d633eaadc1888b76d47ad0913c8f74b8d957a447d8c7aa'
COUNTS = {'ApiDurationMetricExporterTest': 24, 'WebDurationMetricExporterTest': 16,
          'ApiSummaryExporterContractTest': 6, 'WebTimerExporterContractTest': 6}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8322-app-duration-host-v1'
    run.OUT = run.host.BASE / 'PG8322-app-duration-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/AppDurationExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebTimerExporterContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.TEST_SOURCE_OVERRIDES = {
        'WebDurationMetricExporterTest': run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDurationMetricExporterTest.java',
        'ApiSummaryExporterContractTest': run.host.ROOT / 'tools/quality/architecture/ApiSummaryExporterContractTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8322-APP-DURATION'
    run.FIXTURES = {}
    run.main()
