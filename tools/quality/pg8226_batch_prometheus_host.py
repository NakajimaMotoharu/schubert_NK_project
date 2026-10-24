"""Exact45/6 Batch supplied metric SDK ordinary PT; no file, backup, process or Root operation."""
import scoped_prometheus_host as run

if __name__=='__main__':
    run.SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
    run.COMPILE=run.host.W/'pg8212-counter-name-six-compile-v1'
    run.COMPILE_SHA='db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6'
    run.SLOT=run.host.W/'pg8226-batch-prometheus-host-v1'
    run.OUT=run.host.BASE/'PG8226-batch-prometheus-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/BatchPrometheusJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'tools/quality/architecture/BatchPrometheusContractTest.java'
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'tools/quality/architecture/BatchPrometheusTextFixture.java',)
    run.TEST_ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
    run.COUNTS={'TransferMetricRecorderTest':8,'IntegrityFailureMetricRecorderTest':8,
                'BatchMetricRecorderTest':8,'ProcessRestartMetricRecorderTest':8,
                'BatchMetricContractTest':5,'BatchPrometheusContractTest':8}
    run.SESSION_ID='PG8226-BATCH-PROMETHEUS'
    run.FIXTURES={}
    run.main()
