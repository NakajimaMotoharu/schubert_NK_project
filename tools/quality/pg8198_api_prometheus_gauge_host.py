"""Exact48/6 ordinary API gauges, no DB/worker/real pool or target environment."""
import scoped_prometheus_host as run

if __name__=='__main__':
    run.SLOT=run.host.W/'pg8198-api-prometheus-gauge-host-v1'
    run.OUT=run.host.BASE/'PG8198-api-prometheus-gauge-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiPrometheusGaugeJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'tools/quality/architecture/ApiPrometheusGaugeContractTest.java'
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'tools/quality/architecture/PrometheusGaugeTextFixture.java',)
    run.TEST_ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.COUNTS={'OutboxRowsMetricRecorderTest':8,'OutboxAgeMetricRecorderTest':8,
                'AsyncJobMetricRecorderTest':8,'DbPoolMetricRecorderTest':8,
                'GeneratedMetricValueContractTest':8,'ApiPrometheusGaugeContractTest':8}
    run.SESSION_ID='PG8198-API-PROMETHEUS-GAUGE'
    run.FIXTURES={}
    run.main()
