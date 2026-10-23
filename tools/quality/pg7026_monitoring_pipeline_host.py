"""Same-source48 pure monitoring PT; no live observation or business operation."""
import pg7006_monitoring_pure_host as runner
import pg7022_alert_thresholds_host as threshold

SLOT = runner.host.W/'pg7026-monitoring-pipeline-host-v1'
SUITES = (*threshold.SUITES, 'dev.codex.schubert.nk.batch.monitoring.MonitoringPolicyEngineTest')


if __name__ == '__main__':
    runner.main(SLOT, SUITES)
