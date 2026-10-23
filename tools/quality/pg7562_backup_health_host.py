"""Current212 ordinary Batch cases, supplied Backup health kernel only/no real I/O."""
import pg7006_monitoring_pure_host as runner
import pg7549_protected_alert_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7562-backup-health-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.BackupHealthMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
