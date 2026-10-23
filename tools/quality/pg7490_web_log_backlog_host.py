"""Current184 ordinary Batch cases, supplied scalar backlog/kernel only, no broker/DB/runtime calls."""
import pg7006_monitoring_pure_host as runner
import pg7420_batch_generated_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7490-web-log-backlog-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.WebLogBacklogMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
