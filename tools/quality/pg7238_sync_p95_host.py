"""Current140 monitoring PT including eight supplied p95 cases; no real endpoint/provider."""
import pg7006_monitoring_pure_host as runner
import pg7224_db_pool_host as previous

SLOT=runner.host.W/'pg7238-sync-p95-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.TimedSyncLatencyMonitorTest')

if __name__=='__main__':runner.main(SLOT,SUITES)
