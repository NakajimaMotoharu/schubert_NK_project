"""Current221 ordinary Batch cases, independent restart rate-limit input, no Unit/history/control I/O."""
import pg7006_monitoring_pure_host as runner
import pg7562_backup_health_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7578-restart-health-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.RestartHealthMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
