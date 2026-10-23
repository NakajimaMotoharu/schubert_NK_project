"""Sixteen ordinary API metrics/JDBC-double cases; never opens a real DB connection."""
import pg7006_monitoring_pure_host as runner
import pg7300_api_async_metric_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7314-api-async-count-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.AsyncJobCountRepositoryTest',)

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
