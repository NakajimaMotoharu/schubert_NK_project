"""BUG1657 private naming correction, actual same161 ordinary cases, original source kept."""
import pg7006_monitoring_pure_host as runner
import pg7266_transfer_metric_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7272-transfer-metric-host-v2'
SUITES=previous.SUITES

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
