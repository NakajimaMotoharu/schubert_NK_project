"""Same-source73 monitoring tests, missing observations never acquire a live target."""
import pg7006_monitoring_pure_host as runner
import pg7064_timed_filesystem_host as previous

SLOT=runner.host.W/'pg7084-registry-missing-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.MonitoringMissingObservationTest')


if __name__=='__main__':
    runner.main(SLOT,SUITES)
