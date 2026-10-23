"""Actual153 monitoring PT with same installed four SDK jars, no Batch/DB/target operation."""
import pg7006_monitoring_pure_host as runner
import pg7238_sync_p95_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7252-batch-metric-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.BatchMetricContractTest',
        'dev.codex.schubert.nk.batch.monitoring.BatchMetricRecorderTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
