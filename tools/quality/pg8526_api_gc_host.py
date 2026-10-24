"""Original API owner-before-GC-activation14, fresh own JVM only."""
import scoped_prometheus_host as run

SOURCE = '7c6ae66a83f300ad0b9cef4824e01701a82d0654'
COMPILE = run.host.W / 'pg8524-api-gc-six-compile-v1'
COMPILE_SHA = '3b8391d5a7a6a11cea8fb3e6a5e9e3cc815bea720c7bf85f025162d6053fbbc1'
COUNTS = {'ApiGcMetricRegistrationTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8526-api-gc-host-v1'
    run.OUT = run.host.BASE / 'PG8526-api-gc-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiGcMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiGcMetricRegistrationTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8526-API-GC'
    run.FIXTURES = {}
    run.main()
