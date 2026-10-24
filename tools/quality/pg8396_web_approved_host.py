"""New approved point join12 plus necessary Web80/shared identity4, original96/9 only."""
import scoped_prometheus_host as run

SOURCE = 'b347581d26d925885a4cb882eeb2326449eded94'
COMPILE = run.host.W / 'pg8394-web-approved-six-compile-v1'
COMPILE_SHA = '6dd0204d10bb95888fed9693cb864685f37fb34323b0a54c5ec801413eda51fe'
COUNTS = {'WebDurationMetricExporterTest': 16, 'WebCounterMetricExporterTest': 16,
          'WebGaugeMetricExporterTest': 16, 'WebMetricCatalogTest': 14,
          'WebCounterExporterContractTest': 6, 'WebTimerExporterContractTest': 6,
          'WebGaugeExporterContractTest': 6, 'MetricIdentitySnapshotContractTest': 4,
          'WebApprovedMetricExporterContractTest': 12}
FIXTURE = 'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA = '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8396-web-approved-host-v1'
    run.OUT = run.host.BASE / 'PG8396-web-approved-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebApprovedMetricJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebApprovedMetricExporterContractTest.java'
    run.TEST_SOURCE_OVERRIDES = {name: run.host.ROOT / ('tools/quality/architecture/' + name + '.java') for name in ('WebCounterExporterContractTest', 'WebTimerExporterContractTest', 'WebGaugeExporterContractTest', 'MetricIdentitySnapshotContractTest')}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8396-WEB-APPROVED'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
