"""Original API owner-before-GC-activation14, fresh own JVM only."""
import scoped_prometheus_host as run

SOURCE = '20075e7f66c3ba8fcf9c52139e77de646abbc7c2'
COMPILE = run.host.W / 'pg8534-api-gc-owned-six-compile-v1'
COMPILE_SHA = '889dff45e9791631d80c81431741a1d8134fbaa7d41b1a74813bb3d2954d8d19'
COUNTS = {'ApiGcMetricRegistrationTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8536-api-gc-owned-host-v1'
    run.OUT = run.host.BASE / 'PG8536-api-gc-owned-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiGcMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiGcMetricRegistrationTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8536-API-GC'
    run.FIXTURES = {}
    run.main()
