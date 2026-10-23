"""Same-source27 ordinary pure monitoring PT, no actual target observation/control."""
import pg7006_monitoring_pure_host as runner
import pg7012_metric_catalog_host as catalog

SLOT = runner.host.W/'pg7018-alert-lifecycle-host-v1'
SUITES = (*catalog.SUITES,
          'dev.codex.schubert.nk.batch.monitoring.AlertLifecycleTest',
          'dev.codex.schubert.nk.batch.monitoring.AlertRegistryTest')


if __name__ == '__main__':
    runner.main(SLOT, SUITES)
