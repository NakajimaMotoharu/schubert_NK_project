"""Same-source41 pure monitoring PT including12 new threshold evaluators."""
import pg7006_monitoring_pure_host as runner
import pg7018_alert_lifecycle_host as state

SLOT = runner.host.W/'pg7022-alert-thresholds-host-v1'
SUITES = (*state.SUITES, 'dev.codex.schubert.nk.batch.monitoring.AlertThresholdsTest')


if __name__ == '__main__':
    runner.main(SLOT, SUITES)
