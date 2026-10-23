"""Current132 monitoring PT including eight supplied DB pool cases; no real database/provider."""
import pg7006_monitoring_pure_host as runner
import pg7210_heap_connection_host as previous

SLOT=runner.host.W/'pg7224-db-pool-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.TimedDbPoolMonitorTest')

if __name__=='__main__':runner.main(SLOT,SUITES)
