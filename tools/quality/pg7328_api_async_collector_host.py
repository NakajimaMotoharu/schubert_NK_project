"""Current24 API JDBC/SDK fixture cases, no real DB/worker/VM connection."""
import pg7006_monitoring_pure_host as runner
import pg7314_api_async_count_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7328-api-async-collector-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.AsyncJobMetricCollectorTest',)

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
