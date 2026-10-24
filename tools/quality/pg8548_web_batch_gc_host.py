"""New Web14 and Batch14 standard JVM composition, original28/2; no API replay."""
import scoped_prometheus_host as run

SOURCE = '623be8eeaf078f85cfa5682dced7a3b2e21a2b49'
COMPILE = run.host.W / 'pg8546-web-batch-gc-six-compile-v1'
COMPILE_SHA = 'cac5a32fa54aad3854c3f843a2289fd04ec26a70765c4da45a36ebe31b2fd8cb'
COUNTS = {'WebGcMetricRegistrationTest': 14, 'BatchGcMetricRegistrationTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8548-web-batch-gc-host-v1'
    run.OUT = run.host.BASE / 'PG8548-web-batch-gc-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebBatchGcMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchGcMetricRegistrationTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8548-WEB-BATCH-GC'
    run.FIXTURES = {}
    run.main()
