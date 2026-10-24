"""New API catalog14/policy14 plus related API62/shared name4, original94/7."""
import scoped_prometheus_host as run

SOURCE = 'a79d0ae0d88c265b4e26a545318399b74d98d97e'
COMPILE = run.host.W / 'pg8430-api-approved-policy-six-compile-v1'
COMPILE_SHA = '65b56cec716e91333cd067559f0f6c20b01963ccbf899ee29d41bdae38683744'
COUNTS = {'ApiMetricCatalogTest': 14, 'ApiMetricScrapeTest': 14,
          'ApiDurationMetricExporterTest': 24, 'ApiSummaryExporterContractTest': 6,
          'ApiScalarMetricExporterTest': 24, 'ApiScalarPrecisionContractTest': 8,
          'MetricIdentitySnapshotContractTest': 4}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8432-api-approved-policy-host-v1'
    run.OUT = run.host.BASE / 'PG8432-api-approved-policy-host-v1'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiApprovedPolicyJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/MetricIdentitySnapshotContractTest.java'
    run.TEST_SOURCE_OVERRIDES = {name: run.host.ROOT / ('tools/quality/architecture/' + name + '.java') for name in ('ApiSummaryExporterContractTest','ApiScalarPrecisionContractTest')}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8432-API-APPROVED-POLICY'
    run.FIXTURES = {}
    run.main()

