"""Actual169 monitoring PT, supplied Transfer data/contexts and owned SDK only."""
import pg7006_monitoring_pure_host as runner
import pg7272_transfer_metric_host_v2 as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7286-transfer-health-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.TransferHealthMonitorTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
