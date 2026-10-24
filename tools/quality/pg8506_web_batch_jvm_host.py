"""New Web14 and Batch14 standard JVM composition, original28/2; no API replay."""
import scoped_prometheus_host as run

SOURCE = '4950b3daf1632ed9f57c3ca42276532b24204745'
COMPILE = run.host.W / 'pg8504-web-batch-jvm-six-compile-v1'
COMPILE_SHA = '3e19a0703f8b845bdf71d7e7d78fdb73733528103acad510a69ba65b4652cf8e'
COUNTS = {'WebJvmMetricsTest': 14, 'BatchJvmMetricsTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8506-web-batch-jvm-host-v1'
    run.OUT = run.host.BASE / 'PG8506-web-batch-jvm-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebBatchJvmMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchJvmMetricsTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8506-WEB-BATCH-JVM'
    run.FIXTURES = {}
    run.main()

