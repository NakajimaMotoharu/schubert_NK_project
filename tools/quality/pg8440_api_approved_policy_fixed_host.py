"""New API catalog14/policy14 plus related API62/shared name4, original94/7."""
import scoped_prometheus_host as run

SOURCE = '75a198d53081b2a70babc9f2497d4faddfdbd508'
COMPILE = run.host.W / 'pg8438-api-approved-policy-fixed-six-compile-v1'
COMPILE_SHA = 'ec6c46e3d158b053cc3d958b633e6ead0ec77ebd8cb30d0d3ba14bf559544daa'
COUNTS = {'ApiMetricCatalogTest': 14, 'ApiMetricScrapeTest': 14,
          'ApiDurationMetricExporterTest': 24, 'ApiSummaryExporterContractTest': 6,
          'ApiScalarMetricExporterTest': 24, 'ApiScalarPrecisionContractTest': 8,
          'MetricIdentitySnapshotContractTest': 4}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8440-api-approved-policy-fixed-host-v1'
    run.OUT = run.host.BASE / 'PG8440-api-approved-policy-fixed-host-v1'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiApprovedPolicyJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/MetricIdentitySnapshotContractTest.java'
    run.TEST_SOURCE_OVERRIDES = {name: run.host.ROOT / ('tools/quality/architecture/' + name + '.java') for name in ('ApiSummaryExporterContractTest','ApiScalarPrecisionContractTest')}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8440-API-APPROVED-POLICY'
    run.FIXTURES = {}
    run.main()


