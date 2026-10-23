"""Current229 ordinary Batch cases, supplied integrity count only; no real probes/repair/retirement."""
import pg7006_monitoring_pure_host as runner
import pg7578_restart_health_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7594-integrity-health-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.IntegrityHealthMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
