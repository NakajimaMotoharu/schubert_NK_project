"""Exact40/5 memory-only supplied counters, no actual Inbox/MQ/operation activity."""
import scoped_prometheus_host as run

if __name__=='__main__':
    run.SLOT=run.host.W/'pg8206-api-prometheus-counter-host-v1'
    run.OUT=run.host.BASE/'PG8206-api-prometheus-counter-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiPrometheusCounterJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'tools/quality/architecture/ApiPrometheusCounterContractTest.java'
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'tools/quality/architecture/PrometheusGaugeTextFixture.java',)
    run.TEST_ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.COUNTS={'InboxReplayMetricRecorderTest':8,'OperationMismatchMetricRecorderTest':8,
                'MqRedeliveryMetricRecorderTest':8,'MqMessageMetricRecorderTest':8,
                'ApiPrometheusCounterContractTest':8}
    run.SESSION_ID='PG8206-API-PROMETHEUS-COUNTER'
    run.FIXTURES={}
    run.main()
