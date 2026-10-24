"""BUG1701 same-source original100/9: new4 plus affected API30/Web66, no catalog replay."""
import scoped_prometheus_host as run

SOURCE = 'f775f095c0721340c20376b8d37d8baa2e97bc21'
COMPILE = run.host.W / 'pg8382-metric-identity-six-compile-v1'
COMPILE_SHA = '3e5b5fa6e22805dde3d851e880ba74d27713b854e7aa1d9aa694fa94669f73b5'
COUNTS = {'ApiDurationMetricExporterTest': 24, 'ApiSummaryExporterContractTest': 6,
          'WebDurationMetricExporterTest': 16, 'WebCounterMetricExporterTest': 16,
          'WebGaugeMetricExporterTest': 16, 'WebCounterExporterContractTest': 6,
          'WebTimerExporterContractTest': 6, 'WebGaugeExporterContractTest': 6,
          'MetricIdentitySnapshotContractTest': 4}
FIXTURE = 'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA = '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8384-metric-identity-full-host-v1'
    run.OUT = run.host.BASE / 'PG8384-metric-identity-full-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/MetricIdentityFullJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/MetricIdentitySnapshotContractTest.java'
    run.TEST_SOURCE_OVERRIDES = {
        'ApiDurationMetricExporterTest': run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporterTest.java',
        **{name: run.host.ROOT / ('tools/quality/architecture/' + name + '.java') for name in ('ApiSummaryExporterContractTest', 'WebCounterExporterContractTest', 'WebTimerExporterContractTest', 'WebGaugeExporterContractTest')}}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8384-METRIC-IDENTITY'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
