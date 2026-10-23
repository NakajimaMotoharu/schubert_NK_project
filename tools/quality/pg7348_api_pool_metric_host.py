"""Actual32 SDK/JDBC-double API cases, no Hikari or DB source/management lookup."""
import pg7006_monitoring_pure_host as runner
import pg7340_api_collector_owned_registry_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7348-api-pool-metric-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorderTest',)

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
