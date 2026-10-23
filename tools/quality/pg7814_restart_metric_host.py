"""Current261 ordinary Batch cases, supplied restart counters; no live process operations."""
import pg7802_integrity_metric_host_v2 as previous
import pg7006_monitoring_pure_host as runner
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7814-restart-metric-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.ProcessRestartMetricRecorderTest')

if __name__=='__main__':
    runner.POM='tools/quality/harnesses/monitoring-pom.xml'
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
