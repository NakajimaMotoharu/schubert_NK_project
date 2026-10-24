"""Exact new-only 14/2 MQ supplied pressure SDK host PT; no Artemis or control."""
import scoped_prometheus_host as run

if __name__=='__main__':
    run.SLOT=run.host.W/'pg8190-mq-prometheus-gauge-host-v1'
    run.OUT=run.host.BASE/'PG8190-mq-prometheus-gauge-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MqPrometheusGaugeJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'tools/quality/architecture/MqPrometheusGaugeContractTest.java'
    run.TEST_ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.COUNTS={'MqPressureMetricRecorderTest':8,'MqPrometheusGaugeContractTest':6}
    run.SESSION_ID='PG8190-MQ-PROMETHEUS-GAUGE'
    run.FIXTURES={}
    run.main()
