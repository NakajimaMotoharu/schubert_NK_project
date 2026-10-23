"""Same-source62 pure monitoring PT; explicit unknown/gap, no actual collector."""
import pg7006_monitoring_pure_host as runner
import pg7044_monitoring_status_host as status

SLOT=runner.host.W/'pg7056-monitoring-window-host-v1'
SUITES=(*status.SUITES,'dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindowTest')


if __name__=='__main__':
    runner.main(SLOT,SUITES)
