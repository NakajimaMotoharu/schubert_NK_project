"""Original API non-resource JVM14/1; own JVM and ports, no actual runtime/Root."""
import scoped_prometheus_host as run

SOURCE = '9607562237e7f827c8ff07f3b8299307cc3f3ddf'
COMPILE = run.host.W / 'pg8482-api-jvm-fixed-six-compile-v1'
COMPILE_SHA = '7dba64895e7ecb4e3bf244818fd2d2f7de2c5140edb1c1f719505fca7e6b6ae6'
COUNTS = {'ApiJvmMetricsTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8484-api-jvm-host-v1'
    run.OUT = run.host.BASE / 'PG8484-api-jvm-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiJvmMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiJvmMetricsTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8484-API-JVM'
    run.FIXTURES = {}
    run.main()

