"""Current200 ordinary Batch monitoring cases; optional numeric count/memory-only Expiry kernel."""
import pg7006_monitoring_pure_host as runner
import pg7504_async_queue_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7518-expiry-backlog-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.ExpiryBacklogMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
