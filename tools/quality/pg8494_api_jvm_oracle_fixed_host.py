"""Original API non-resource JVM14/1; own JVM and ports, no actual runtime/Root."""
import scoped_prometheus_host as run

SOURCE = 'fe91dc6898c2f5b679c8fe14c70a490bed770c73'
COMPILE = run.host.W / 'pg8492-api-jvm-oracle-fixed-six-compile-v1'
COMPILE_SHA = 'b6c9978bf0c71e1b76314c81557ffe7113911c27ed172e01c7eaf66ad52ac884'
COUNTS = {'ApiJvmMetricsTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8494-api-jvm-oracle-fixed-host-v1'
    run.OUT = run.host.BASE / 'PG8494-api-jvm-oracle-fixed-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiJvmMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiJvmMetricsTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8494-API-JVM'
    run.FIXTURES = {}
    run.main()


