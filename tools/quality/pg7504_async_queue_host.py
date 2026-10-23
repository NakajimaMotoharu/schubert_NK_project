"""Current192 ordinary Batch cases, optional supplied count/capacity/memory-only alert kernel."""
import pg7006_monitoring_pure_host as runner
import pg7490_web_log_backlog_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7504-async-queue-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.AsyncQueueMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
