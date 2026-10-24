"""New API scalar24 and actual precision source8; original32/2, no historical replay."""
import scoped_prometheus_host as run

SOURCE = '6143bf358'
COMPILE = run.host.W / 'pg8418-api-scalar-six-compile-v1'
COMPILE_SHA = 'cbd5b74c6409bc0c53b8732c5807661d6fe94fbf51743ba706c9018fafafeced'
COUNTS = {'ApiScalarMetricExporterTest': 24, 'ApiScalarPrecisionContractTest': 8}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8420-api-scalar-host-v1'
    run.OUT = run.host.BASE / 'PG8420-api-scalar-host-v1'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiScalarExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/ApiScalarPrecisionContractTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8420-API-SCALAR'
    run.FIXTURES = {}
    run.main()

