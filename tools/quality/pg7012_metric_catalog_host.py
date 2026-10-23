"""Required same-source regression of mode + new metric catalogue, pure host only."""
import pg7006_monitoring_pure_host as runner

SLOT = runner.host.W/'pg7012-metric-catalog-host-v1'
SUITES = (runner.SUITE, 'dev.codex.schubert.nk.batch.monitoring.MetricContractTest')


if __name__ == '__main__':
    runner.main(SLOT, SUITES)
