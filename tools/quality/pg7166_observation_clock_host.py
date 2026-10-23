"""Current monitoring91 actual tests; fixed clock/tick/FileStore, no OS time or live target changes."""
import pg7006_monitoring_pure_host as runner
import pg7152_filesystem_health_host as previous

SLOT=runner.host.W/'pg7166-observation-clock-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.MonitoringObservationClockTest')


if __name__=='__main__':runner.main(SLOT,SUITES)
