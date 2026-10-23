"""Actual current83 pure monitoring tests, borrowed fixed FileStore only and no live targets."""
import pg7006_monitoring_pure_host as runner
import pg7084_registry_missing_host as previous

SLOT=runner.host.W/'pg7152-filesystem-health-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.FilesystemHealthObservationTest')


if __name__=='__main__':runner.main(SLOT,SUITES)
