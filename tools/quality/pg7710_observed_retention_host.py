"""Current245 ordinary Batch cases; only supplied numeric retention configuration, no storage/service actions."""
import pg7610_dlq_health_host as previous
import pg7006_monitoring_pure_host as runner
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7710-observed-retention-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.MonitoringRetentionConfigurationTest')

if __name__=='__main__':
    runner.POM='tools/quality/harnesses/monitoring-pom.xml'
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
