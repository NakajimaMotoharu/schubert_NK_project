"""Current237 ordinary Batch cases, coherent current-DLQ entries only; no broker/body/triage operation."""
import pg7006_monitoring_pure_host as runner
import pg7594_integrity_health_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7610-dlq-health-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.DlqHealthMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
