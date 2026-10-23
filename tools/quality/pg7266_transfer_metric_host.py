"""Actual161 monitoring PT with transfer gauges, same four SDK pins, no actual filesystem."""
import pg7006_monitoring_pure_host as runner
import pg7252_batch_metric_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7266-transfer-metric-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorderTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
