"""Actual eight API async metric cases with installed SDK, no business DB/JMS/HTTP/Root operation."""
import pg7006_monitoring_pure_host as runner
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7300-api-async-metric-host-v1'
POM='tools/quality/harnesses/monitoring-api-jobs-pom.xml'
SUITES=('dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorderTest',)

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
