"""Current253 ordinary Batch cases; supplied SDK counter only, no real integrity probes."""
import pg7710_observed_retention_host as previous
import pg7006_monitoring_pure_host as runner
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7788-integrity-metric-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.IntegrityFailureMetricRecorderTest')

if __name__=='__main__':
    runner.POM='tools/quality/harnesses/monitoring-pom.xml'
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
