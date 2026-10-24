"""BUG1691 corrected-source exact40/5; never transfer prior source results or old Jars."""
import scoped_prometheus_host as run

SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
COMPILE=run.host.W/'pg8212-counter-name-six-compile-v1'
COMPILE_SHA='db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6'

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8214-counter-name-host-v1'
    run.OUT=run.host.BASE/'PG8214-counter-name-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiPrometheusCounterJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'tools/quality/architecture/ApiPrometheusCounterContractTest.java'
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'tools/quality/architecture/PrometheusGaugeTextFixture.java',)
    run.TEST_ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.COUNTS={'InboxReplayMetricRecorderTest':8,'OperationMismatchMetricRecorderTest':8,
                'MqRedeliveryMetricRecorderTest':8,'MqMessageMetricRecorderTest':8,
                'ApiPrometheusCounterContractTest':8}
    run.SESSION_ID='PG8214-COUNTER-NAME'
    run.FIXTURES={}
    run.main()
