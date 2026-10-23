"""BUG1659 fixed-source ordinary24; previous testCompile failures retained, never replayed."""
import pg7006_monitoring_pure_host as runner
import pg7328_api_async_collector_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7340-api-collector-owned-registry-host-v1'
POM=previous.POM
SUITES=previous.SUITES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
